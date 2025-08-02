import os
import shutil
from PIL import Image
import requests
from requests.exceptions import RequestException
import time
import uuid
from pathlib import Path
from tqdm import tqdm
import math
import json
import argparse
import boto3
from botocore.client import Config
from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings
import subprocess
import tempfile
from urllib.parse import quote
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue

# Supported video file types
VIDEO_EXTENSIONS = {
    '.mp4': 'application/octet-stream',
    '.mov': 'application/octet-stream',
    '.avi': 'application/octet-stream',
    '.mkv': 'application/octet-stream',
    '.hevc': 'application/octet-stream'
}

# Supported image file types
IMAGE_EXTENSIONS = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.bmp': 'image/bmp',
    '.tiff': 'image/tiff',
    '.tif': 'image/tiff',
    '.webp': 'image/webp'
}

class OptimizedVideoProcessor:
    """Optimized video processor that extracts metadata without downloading"""
    
    def __init__(self):
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if FFmpeg/FFprobe are available"""
        try:
            subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "FFprobe not found. Install FFmpeg:\n"
                "Windows: Download from https://ffmpeg.org/\n"
                "macOS: brew install ffmpeg\n"
                "Linux: sudo apt install ffmpeg"
            )
    
    def get_video_metadata_from_url(self, video_url, timeout=30):
        """Extract video metadata from URL without downloading, with timeout"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                '-select_streams', 'v:0',
                '-timeout', str(timeout * 1000000),  # ffprobe timeout in microseconds
                video_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode != 0:
                print(f"FFprobe error for {video_url}: {result.stderr.strip()}")
                return None
                
            data = json.loads(result.stdout)
            
            if not data.get('streams'):
                print("No video streams found.")
                return None
                
            video_stream = data['streams'][0]
            format_info = data.get('format', {})
            
            # Calculate FPS
            fps_str = video_stream.get('r_frame_rate', '0/1')
            if '/' in fps_str:
                num, den = map(int, fps_str.split('/'))
                fps = num / den if den != 0 else 0
            else:
                fps = float(fps_str)
            
            return {
                'fps': round(fps, 2),
                'duration': round(float(format_info.get('duration', 0)), 2),
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0))
            }
            
        except subprocess.TimeoutExpired:
            print(f"FFprobe timed out after {timeout} seconds for {video_url}")
            return None
        except Exception as e:
            print(f"Failed to get metadata for {video_url}: {e}")
            return None

class OptimizedImageProcessor:
    """Optimized image processor for metadata extraction and thumbnail creation"""
    
    def __init__(self, max_workers=8):
        self.max_workers = max_workers
        self.session = requests.Session()
        
    def get_image_metadata_from_url(self, image_url, timeout=240):
        """Extract image metadata from URL without downloading full image"""
        try:
            # Make a HEAD request to get basic info
            response = self.session.head(image_url, timeout=timeout)
            
            # if response.status_code != 200:
            #     print(f"Failed to access image URL: {response.status_code}")
            #     return None
            
            # Get partial image data to read metadata
            headers = {'Range': 'bytes=0-2048'}  # First 2KB should be enough for most image headers
            response = self.session.get(image_url, headers=headers, timeout=timeout, stream=True)
            
            if response.status_code in [200, 206]:  # 206 is partial content
                # Save partial data to temp file
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(response.content)
                    temp_path = temp_file.name
                
                try:
                    # Try to open with PIL to get dimensions
                    with Image.open(temp_path) as img:
                        width, height = img.size
                        format_name = img.format
                    
                    os.unlink(temp_path)
                    
                    return {
                        'width': width,
                        'height': height,
                        'format': format_name
                    }
                except Exception as e:
                    # If partial read fails, try downloading a bit more
                    os.unlink(temp_path)
                    return self._get_image_metadata_full_download(image_url, timeout)
            else:
                return self._get_image_metadata_full_download(image_url, timeout)
                
        except Exception as e:
            print(f"Failed to get image metadata for {image_url}: {e}")
            return None
    
    def _get_image_metadata_full_download(self, image_url, timeout=30):
        """Fallback method to download full image for metadata"""
        try:
            response = self.session.get(image_url, timeout=timeout)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            try:
                with Image.open(temp_path) as img:
                    width, height = img.size
                    format_name = img.format
                
                os.unlink(temp_path)
                
                return {
                    'width': width,
                    'height': height,
                    'format': format_name
                }
            except Exception as e:
                os.unlink(temp_path)
                print(f"Failed to process downloaded image: {e}")
                return None
                
        except Exception as e:
            print(f"Failed to download image for metadata: {e}")
            return None
    
    def create_single_thumbnail(self, task_data):
        """Create a single thumbnail - optimized for parallel processing"""
        try:
            # Handle both old and new task data formats
            if len(task_data) == 7:
                image_url, thumbnail_key, provider, bucket_name, credentials, s3_client, file_name = task_data
                region = 'eu-west-2'  # Default region
            else:
                image_url, thumbnail_key, provider, bucket_name, credentials, s3_client, file_name, region = task_data
            
            print(f"🔄 Processing thumbnail for: {file_name}")
            
            # Download image
            response = self.session.get(image_url, timeout=30)
            response.raise_for_status()
            print(f"✅ Downloaded image: {file_name} ({len(response.content)} bytes)")
            
            # Create thumbnail
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_path = temp_file.name
            
            try:
                with tempfile.NamedTemporaryFile() as temp_input:
                    temp_input.write(response.content)
                    temp_input.flush()
                    
                    with Image.open(temp_input.name) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'LA', 'P'):
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Create thumbnail with consistent size
                        img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                        img.save(temp_path, "JPEG", quality=85, optimize=True)
                
                print(f"✅ Created thumbnail: {file_name}")
                
                # Upload thumbnail based on provider
                if provider == "AZURE_BLOB_STORAGE":
                    self._upload_to_azure(temp_path, thumbnail_key, bucket_name, credentials, s3_client, file_name)

                elif provider == "GCP":
                    self._upload_to_gcp(temp_path, thumbnail_key, bucket_name, credentials, file_name)
                elif provider in ["AWS_S3", "S3"]:
                    self._upload_to_s3(temp_path, thumbnail_key, bucket_name, s3_client, file_name)
                else:
                    # Default fallback to S3-compatible
                    self._upload_to_s3(temp_path, thumbnail_key, bucket_name, s3_client, file_name)
                
                # Get file size for reporting
                file_size = os.path.getsize(temp_path)
                os.unlink(temp_path)
                
                print(f"✅ Successfully processed thumbnail: {thumbnail_key}")
                return thumbnail_key, None, file_size
                
            except Exception as e:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                error_msg = f"Processing error for {file_name}: {str(e)}"
                print(f"❌ {error_msg}")
                return None, error_msg, 0
                
        except Exception as e:
            error_msg = f"Download error for {file_name}: {str(e)}"
            print(f"❌ {error_msg}")
            return None, error_msg, 0
    
    def _upload_to_azure(self, temp_path, thumbnail_key, bucket_name, credentials, s3_client, file_name):
        """Upload to Azure Blob Storage"""
        try:
            container_client = s3_client.get_container_client(bucket_name)
            blob_client = container_client.get_blob_client(thumbnail_key)
            
            with open(temp_path, "rb") as data:
                blob_client.upload_blob(
                    data,
                    overwrite=True,
                    content_settings=ContentSettings(content_type='image/jpeg')
                )
            print(f"✅ Azure upload successful: {thumbnail_key}")
            
        except Exception as azure_error:
            print(f"❌ Main Azure client failed for {file_name}, trying direct approach: {str(azure_error)}")
            
            if 'sas_token' in credentials:
                sas_token = credentials.get('sas_token')
                
                if sas_token.startswith('http'):
                    from urllib.parse import urlparse
                    parsed = urlparse(sas_token)
                    blob_url = f"{parsed.scheme}://{parsed.netloc}/{bucket_name}/{thumbnail_key}?{parsed.query}"
                else:
                    account_name = credentials.get('account_name') or credentials.get('access_key_id') or credentials.get('extracted_account_name')
                    clean_sas_token = sas_token.strip()
                    if not clean_sas_token.startswith('?'):
                        clean_sas_token = f"?{clean_sas_token}"
                    blob_url = f"https://{account_name}.blob.core.windows.net/{bucket_name}/{thumbnail_key}{clean_sas_token}"
                
                blob_client_direct = BlobClient.from_blob_url(blob_url)
                
                with open(temp_path, "rb") as data:
                    blob_client_direct.upload_blob(
                        data,
                        overwrite=True,
                        content_settings=ContentSettings(content_type='image/jpeg')
                    )
                print(f"✅ Azure direct upload successful: {thumbnail_key}")
            else:
                raise azure_error

    def _upload_to_gcp(self, temp_path, thumbnail_key, bucket_name, credentials, file_name):
        """Upload to GCP Cloud Storage"""
        try:
            # Initialize GCP client from credentials
            from google.cloud import storage
            from google.oauth2 import service_account
            import json
            
            project_id = credentials.get('service_account_json').get('project_id')
            if not project_id:
                raise ValueError("GCP Cloud Storage requires project_id")
            
            # Create GCP client based on credential type
            if credentials.get('service_account_json'):
                service_account_json = credentials.get('service_account_json')
                
                if isinstance(service_account_json, str):
                    credentials_info = json.loads(service_account_json)
                else:
                    credentials_info = service_account_json
                
                creds = service_account.Credentials.from_service_account_info(credentials_info)
                gcp_client = storage.Client(project=project_id, credentials=creds)
                
            elif credentials.get('service_account_path'):
                service_account_path = credentials.get('service_account_path')
                gcp_client = storage.Client.from_service_account_json(
                    service_account_path,
                    project=project_id
                )
            else:
                # Use default credentials
                gcp_client = storage.Client(project=project_id)
            
            # Get bucket and create blob
            bucket = gcp_client.bucket(bucket_name)
            blob = bucket.blob(thumbnail_key)
            
            # Upload file with content type
            blob.upload_from_filename(
                temp_path,
                content_type='image/jpeg'
            )
            
            print(f"✅ GCP upload successful: {thumbnail_key}")
            
        except Exception as gcp_error:
            print(f"❌ GCP upload failed for {file_name}: {str(gcp_error)}")
            raise gcp_error

    def _upload_to_s3(self, temp_path, thumbnail_key, bucket_name, s3_client, file_name):
        """Upload to S3-compatible storage"""
        try:
            s3_client.upload_file(
                temp_path,
                bucket_name,
                thumbnail_key,
                ExtraArgs={'ContentType': 'image/jpeg'}
            )
            print(f"✅ S3 upload successful: {thumbnail_key}")
            
        except Exception as s3_error:
            print(f"❌ S3 upload failed for {file_name}: {str(s3_error)}")
            raise s3_error
    
    def bulk_create_thumbnails(self, thumbnail_tasks, max_workers=8):
        """Create thumbnails in parallel for better performance"""
        results = []
        failed_tasks = []
        total_size = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.create_single_thumbnail, task): task 
                for task in thumbnail_tasks
            }
            
            # Process results with progress bar
            with tqdm(total=len(thumbnail_tasks), desc="Creating individual thumbnails", unit="thumbnail") as pbar:
                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        thumbnail_key, error, file_size = future.result()
                        if thumbnail_key:
                            results.append(thumbnail_key)
                            total_size += file_size
                            pbar.set_postfix({'Created': len(results), 'Size': f'{total_size//1024}KB'})
                        else:
                            failed_tasks.append((task, error))
                        pbar.update(1)
                    except Exception as e:
                        failed_tasks.append((task, str(e)))
                        pbar.update(1)
        
        return results, failed_tasks

def get_file_type(file_path):
    """Determine if file is video, image, or other"""
    if hasattr(file_path, 'suffix'):
        extension = file_path.suffix.lower()
    else:
        extension = os.path.splitext(file_path)[1].lower() if isinstance(file_path, str) else ""
    
    if extension in VIDEO_EXTENSIONS:
        return "VIDEO"
    elif extension in IMAGE_EXTENSIONS:
        return "IMAGE"
    else:
        return "OTHER"

def is_video_file(file_path):
    """Check if the file is a video based on extension"""
    return get_file_type(file_path) == "VIDEO"

def is_image_file(file_path):
    """Check if the file is an image based on extension"""
    return get_file_type(file_path) == "IMAGE"

def is_thumbnail_file(file_path):
    """Check if the file is a thumbnail based on filename pattern"""
    filename = os.path.basename(file_path).lower()
    return "thumbnail" in filename

def get_file_size_readable(size_bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def build_presigned_url(provider, bucket_name, key, credentials, region=None):
    """Build presigned URL for media access"""
    if provider == "AZURE_BLOB_STORAGE":
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        from datetime import datetime, timedelta
        from urllib.parse import quote
        
        # Check if connection string is provided
        connection_string = credentials.get('connection_string')
        
        if connection_string:
            # Parse connection string to extract account name and key
            account_name = None
            account_key = None
            endpoint_suffix = "core.windows.net"
            
            # Parse connection string components
            parts = connection_string.split(';')
            for part in parts:
                if '=' in part:
                    key_part, value = part.split('=', 1)
                    if key_part == 'AccountName':
                        account_name = value
                    elif key_part == 'AccountKey':
                        account_key = value
                    elif key_part == 'EndpointSuffix':
                        endpoint_suffix = value
            
            if account_name and account_key:
                try:
                    # Generate SAS token using account key from connection string
                    sas_token = generate_blob_sas(
                        account_name=account_name,
                        container_name=bucket_name,
                        blob_name=key,
                        account_key=account_key,
                        permission=BlobSasPermissions(read=True),
                        expiry=datetime.utcnow() + timedelta(hours=6)  # 6 hour expiry
                    )
                    
                    return f"https://{account_name}.blob.{endpoint_suffix}/{bucket_name}/{quote(key)}?{sas_token}"
                except Exception as e:
                    print(f"Error generating SAS token from connection string: {e}")
                    # Fallback to basic URL without SAS
                    return f"https://{account_name}.blob.{endpoint_suffix}/{bucket_name}/{quote(key)}"
            else:
                raise ValueError("Invalid connection string format - missing AccountName or AccountKey")
        
        elif 'sas_token' in credentials:
            # Use provided SAS token
            sas_token = credentials.get('sas_token')
            
            if sas_token.startswith('http'):
                # Full SAS URL provided - construct blob URL
                from urllib.parse import urlparse, urlunparse
                parsed = urlparse(sas_token)
                # Reconstruct URL with specific blob path
                return f"{parsed.scheme}://{parsed.netloc}/{bucket_name}/{quote(key)}?{parsed.query}"
            else:
                # SAS token parameters provided
                account_name = credentials.get('account_name')
                
                # Extract account name from various sources if not provided
                if not account_name:
                    if 'access_key_id' in credentials:
                        account_name = credentials['access_key_id']
                    elif 'endpoint_url' in credentials:
                        endpoint_url = credentials['endpoint_url']
                        if endpoint_url.startswith("https://"):
                            account_name = endpoint_url.split("//")[1].split(".")[0]
                        else:
                            account_name = endpoint_url.split(".")[0]
                    else:
                        raise ValueError("Account name is required when using SAS token")
                
                if sas_token:
                    # Clean up SAS token
                    clean_sas_token = sas_token.strip()
                    
                    # Handle different SAS token formats
                    if clean_sas_token.startswith('http'):
                        # Full URL provided, extract query parameters
                        if '?' in clean_sas_token:
                            clean_sas_token = clean_sas_token.split('?', 1)[1]
                        else:
                            clean_sas_token = ""
                    
                    # Ensure proper format
                    if clean_sas_token and not clean_sas_token.startswith('?'):
                        clean_sas_token = f"?{clean_sas_token}"
                    
                    return f"https://{account_name}.blob.core.windows.net/{bucket_name}/{quote(key)}{clean_sas_token}"
                else:
                    return f"https://{account_name}.blob.core.windows.net/{bucket_name}/{quote(key)}"
        
        elif 'account_key' in credentials:
            # Use account key to generate SAS token
            account_name = credentials.get('account_name')
            account_key = credentials.get('account_key')
            
            if not account_name:
                raise ValueError("Account name is required when using account key")
            
            try:
                # Generate SAS token using account key
                sas_token = generate_blob_sas(
                    account_name=account_name,
                    container_name=bucket_name,
                    blob_name=key,
                    account_key=account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(hours=6)  # 6 hour expiry
                )
                
                return f"https://{account_name}.blob.core.windows.net/{bucket_name}/{quote(key)}?{sas_token}"
            except Exception as e:
                print(f"Error generating SAS token from account key: {e}")
                # Fallback to basic URL without SAS
                return f"https://{account_name}.blob.core.windows.net/{bucket_name}/{quote(key)}"
        
        else:
            # Legacy approach with access_key_id (treat as account name)
            account_name = credentials.get('access_key_id')
            if account_name:
                return f"https://{account_name}.blob.core.windows.net/{bucket_name}/{quote(key)}"
            else:
                raise ValueError("Azure Blob Storage credentials not configured properly. Expected 'connection_string', 'sas_token', 'account_key', or 'access_key_id'")

    elif provider == "GCP":
        from google.cloud import storage
        from google.oauth2 import service_account
        from datetime import datetime, timedelta, timezone
        import json
        
        project_id = credentials.get('service_account_json').get('project_id')
        if not project_id:
            raise ValueError("GCP Cloud Storage requires project_id")
        
        try:
            # Initialize GCP client based on credential type
            if credentials.get('service_account_json'):
                # Handle service account JSON (string or dict)
                service_account_json = credentials.get('service_account_json')
                
                if isinstance(service_account_json, str):
                    try:
                        credentials_info = json.loads(service_account_json)
                    except json.JSONDecodeError:
                        raise ValueError("Invalid service_account_json format")
                else:
                    credentials_info = service_account_json
                
                creds = service_account.Credentials.from_service_account_info(credentials_info)
                client = storage.Client(project=project_id, credentials=creds)
                
            elif credentials.get('service_account_path'):
                # Handle service account key file path
                service_account_path = credentials.get('service_account_path')
                client = storage.Client.from_service_account_json(
                    service_account_path,
                    project=project_id
                )
                
            else:
                # Use Application Default Credentials (ADC)
                client = storage.Client(project=project_id)
            
            # Get bucket and blob
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(key)
            
            # Generate signed URL with expiration
            expiration_time = datetime.now(timezone.utc) + timedelta(
                hours=credentials.get('expire_hours', 6)  # Default 6 hours like Azure
            )
            
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=expiration_time,
                method="GET"
            )
            
            return signed_url
            
        except Exception as e:
            print(f"Error generating GCP signed URL: {e}")
            # Fallback to public URL (if blob is public)
            return f"https://storage.googleapis.com/{bucket_name}/{key}"
    
    elif provider in ["S3", "AWS_S3", "MINIO", "WASABI", "CLOUDFLARE_R2"]:
        import boto3
        from botocore.config import Config
        import re
        
        # Check if connection string is provided for S3-compatible services
        connection_string = credentials.get('connection_string')
        
        if connection_string:
            # Parse S3 connection string format
            # Format: "s3://access_key:secret_key@endpoint/region"
            match = re.match(r's3://([^:]+):([^@]+)@([^/]+)/?(.+)?', connection_string)
            if match:
                access_key = match.group(1)
                secret_key = match.group(2)
                endpoint = match.group(3)
                region = match.group(4) or 'us-east-1'
                
                credentials_from_string = {
                    'access_key_id': access_key,
                    'secret_access_key': secret_key,
                    'endpoint_url': f"https://{endpoint}",
                    'region': region
                }
            else:
                raise ValueError("Invalid S3 connection string format")
        else:
            credentials_from_string = credentials
        
        # Use provided region or default to eu-west-2 for your setup
        aws_region = region or credentials_from_string.get('region') or 'eu-west-2'
        
        # Create S3 client with credentials
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=credentials_from_string.get('access_key_id'),
                aws_secret_access_key=credentials_from_string.get('secret_access_key'),
                region_name=aws_region,
                endpoint_url=credentials_from_string.get('endpoint_url'),
                config=Config(signature_version='s3v4')
            )
            
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': key},
                ExpiresIn=3600  # 1 hour
            )
            return url
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def find_matching_thumbnail(main_file_key, thumbnail_files, thumbnail_path=None):
    """Find matching thumbnail file for main image/video file"""
    main_filename = os.path.basename(main_file_key)
    main_name = os.path.splitext(main_filename)[0]
    main_folder = os.path.dirname(main_file_key)
    
    # Try different matching patterns
    for thumb_file in thumbnail_files:
        thumb_filename = os.path.basename(thumb_file['key'])
        thumb_folder = os.path.dirname(thumb_file['key'])
        thumb_name = os.path.splitext(thumb_filename)[0]
        
        # Check if in same folder, _thumbnails subfolder, or specified thumbnail path
        folder_match = (thumb_folder == main_folder or 
                       thumb_folder == f"{main_folder}/_thumbnails" or
                       thumb_folder == "_thumbnails" or
                       (thumbnail_path and thumb_folder.startswith(thumbnail_path)))
        
        if folder_match:
            # Pattern 1: exact name match with thumbnail suffix
            # example: blueberry_037.jpg -> blueberry_037_thumbnail.jpg
            expected_thumb_name = f"{main_name}_thumbnail"
            if thumb_name == expected_thumb_name:
                return thumb_file['key']
            
            # Pattern 2: exact base name match (for exact matching)
            # example: blueberry_037.jpg -> blueberry_037_thumbnail.jpg
            if thumb_name.startswith(main_name) and thumb_name.endswith("_thumbnail"):
                return thumb_file['key']
            
            # Pattern 3: fallback - check if main_name is exactly in thumbnail name
            # Only match if the main name is followed by "_thumbnail"
            if f"{main_name}_thumbnail" in thumb_name:
                return thumb_file['key']
        
        # Pattern 4: Cross-folder matching by exact filename similarity (for custom thumbnail paths)
        if thumbnail_path and thumb_folder.startswith(thumbnail_path):
            expected_thumb_name = f"{main_name}_thumbnail"
            if thumb_name == expected_thumb_name:
                return thumb_file['key']
    
    return None

def chunk_list(lst, chunk_size):
    """Split list into chunks of specified size"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def process_single_batch(batch_files, batch_num, total_batches, video_processor, image_processor, 
                        provider, bucket_name, credentials, s3_client, json_files_lookup, 
                        thumbnail_files_lookup, file_type, thumbnail_path=None, region=None):
    """Process a single batch of files (videos or images) with existing thumbnails"""
    
    print(f"\n   🎬 Processing {len(batch_files)} {file_type.lower()} files for metadata...")
    
    batch_items = []
    
    # Process each file in the batch
    for idx, media_file in enumerate(batch_files, 1):
        media_key = media_file['key']
        file_name = os.path.basename(media_key)
        base_name = os.path.splitext(file_name)[0]
        folder = os.path.dirname(media_key)
        
        # Find matching thumbnail
        file_name = os.path.basename(media_key)
        thumbnail_key = find_matching_thumbnail(media_key, thumbnail_files_lookup.get(folder, []), thumbnail_path)
        
        if not thumbnail_key:
            # If no existing thumbnail found, check if we have a newly created one
            base_name = os.path.splitext(file_name)[0]
            
            # Check in all thumbnail folders
            for thumb_folder, thumb_files in thumbnail_files_lookup.items():
                for thumb_file in thumb_files:
                    thumb_filename = os.path.basename(thumb_file['key'])
                    thumb_base = os.path.splitext(thumb_filename)[0].replace('_thumbnail', '')
                    
                    if base_name == thumb_base:
                        thumbnail_key = thumb_file['key']
                        break
                    elif f"{base_name}_thumbnail" in thumb_filename:
                        thumbnail_key = thumb_file['key']
                        break
                if thumbnail_key:
                    break
        
        if not thumbnail_key:
            continue
        
        # Find matching JSON file
        matching_json = json_files_lookup.get(folder)
        
        # Create progress bar for this file
        file_pbar = tqdm(total=100, desc=f"Processing {file_name}", leave=False)
        
        try:
            # Build presigned URL for media access
            media_url = build_presigned_url(provider, bucket_name, media_key, credentials, region)
            if not media_url:
                raise Exception("Failed to generate media URL")
            
            file_pbar.update(50)
            
            # Process based on file type
            if file_type == "VIDEO":
                file_pbar.set_description(f"Getting video metadata...")
                
                # Get video metadata WITHOUT downloading
                metadata = video_processor.get_video_metadata_from_url(media_url)
                
                if not metadata:
                    # Use default values if metadata extraction fails
                    metadata = {
                        'fps': 10.0,
                        'duration': 0.0,
                        'width': 1920,
                        'height': 1080
                    }
            
            elif file_type == "IMAGE":
                file_pbar.set_description(f"Getting image metadata...")
                
                # Get image metadata
                metadata = image_processor.get_image_metadata_from_url(media_url)
                
                if not metadata:
                    # Use default values if metadata extraction fails
                    metadata = {
                        'width': 1920,
                        'height': 1080,
                        'format': 'JPEG'
                    }
            
            file_pbar.update(50)
            
            # Create registration item with extracted metadata
            if file_type == "VIDEO":
                item = {
                    "key": media_key,
                    "thumbnail_key": thumbnail_key,
                    "file_name": file_name,
                    "width": metadata['width'],
                    "height": metadata['height'],
                    "fps": metadata['fps'],
                    "duration": f"{metadata['duration']}"
                }
            elif file_type == "IMAGE":
                item = {
                    "key": media_key,
                    "thumbnail_key": thumbnail_key,
                    "file_name": file_name,
                    "width": metadata['width'],
                    "height": metadata['height']
                }
            
            # Add metadata reference
            if matching_json:
                item["metadata"] = matching_json
            else:
                item["metadata"] = media_key
            
            batch_items.append(item)
            
        except Exception as e:
            # Still create a registration item with default values if thumbnail exists
            if thumbnail_key:
                if file_type == "VIDEO":
                    item = {
                        "key": media_key,
                        "thumbnail_key": thumbnail_key,
                        "file_name": file_name,
                        "width": 1920,
                        "height": 1080,
                        "fps": 10.0,
                        "duration": 0.0
                    }
                elif file_type == "IMAGE":
                    item = {
                        "key": media_key,
                        "thumbnail_key": thumbnail_key,
                        "file_name": file_name,
                        "width": 1920,
                        "height": 1080
                    }
                
                if matching_json:
                    item["metadata"] = matching_json
                else:
                    item["metadata"] = media_key
                
                batch_items.append(item)
        
        file_pbar.close()
    
    print(f"      📊 Prepared {len(batch_items)} items for registration")
    return batch_items

def register_existing_s3_files(base_url, token, user_id, project_id, folder_path, base_file=None, 
                               file_type="IMAGE", thumbnail_path=None, create_thumbnails=True,
                               max_workers=8):
                               
    """Batch processing of S3 files with smart thumbnail handling - existing or auto-create"""
    
    import datetime
    import builtins
    
    # Set batch sizes based on file type
    if file_type == "IMAGE":
        batch_size = 100
    elif file_type == "VIDEO":
        batch_size = 10
    
    # Validate file_type
    if file_type not in ["VIDEO", "IMAGE"]:
        raise ValueError("file_type must be either 'VIDEO' or 'IMAGE'")
    
    # Set up logging
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{timestamp}_batch_{file_type.lower()}_uploads_log.txt"
    os.makedirs('logs', exist_ok=True)
    log_filepath = os.path.join('logs', log_filename)
    
    original_print = builtins.print
    
    def tee_print(*args, **kwargs):
        original_print(*args, **kwargs)
        with open(log_filepath, "a", encoding="utf-8") as f:
            f.write(" ".join(map(str, args)) + "\n")
    
    builtins.print = tee_print
    
    try:
        # Initialize processors
        video_processor = None
        image_processor = None
        
        if file_type == "VIDEO":
            video_processor = OptimizedVideoProcessor()
        elif file_type == "IMAGE":
            image_processor = OptimizedImageProcessor(max_workers=max_workers)
        
        # API endpoints
        list_objects_endpoint = f"{base_url}/settings/cloud_storage/list-folder-buckets/{user_id}?prefix={folder_path}"
        get_bucket_endpoint = f"{base_url}/settings/cloud_storage/{user_id}"
        register_endpoint = f"{base_url}/uploads/entry-datas/bucket?media_type={file_type}"
        confirm_media_endpoint = f"{base_url}/uploads/confirm-upload/{{}}"
        batch_confirm_endpoint = f"{base_url}/uploads/batch-confirm/{{}}"
        delete_endpoint = f"{base_url}/task/bulk_delete/{{}}"
        
        headers = {'Authorization': f'Bearer {token}'}
        
        print(f"🚀 BATCH {file_type} PROCESSOR WITH SMART THUMBNAILS")
        print("✅ Using existing thumbnail files when available")
        if create_thumbnails and file_type == "IMAGE":
            print("✅ Auto-creating missing thumbnails with parallel processing")
            print(f"⚡ Using {max_workers} parallel workers for thumbnail creation")
        else:
            print("⚠️  Skipping thumbnail creation - only processing files with existing thumbnails")
        
        if thumbnail_path:
            print(f"📁 Custom thumbnail path: {thumbnail_path}")
        else:
            print(f"📁 Default thumbnail location: _thumbnails subfolders")
            
        print(f"📦 Processing {batch_size} files per batch")
        print("=" * 60)
        
        # Get bucket credentials
        response = requests.get(get_bucket_endpoint, headers=headers)
        response.raise_for_status()
        bucket_data = response.json()
        
        bucket_name = bucket_data.get('resource_name')
        credentials = bucket_data.get('credentials', {})
        provider = bucket_data.get('provider')
        
        print(f"Using bucket: {bucket_name} (Provider: {provider})")
        
        # Debug: Show available credential keys (without values for security)
        print(f"Available credential keys: {list(credentials.keys())}")
        
        # # Initialize storage client and region
        region = 'eu-west-2'  # Default region
        
        if provider == "AZURE_BLOB_STORAGE":
            # Azure initialization
            connection_string = credentials.get('connection_string')
            
            if connection_string:
                s3_client = BlobServiceClient.from_connection_string(connection_string)
                print("✅ Azure client initialized with connection string")
                
            elif credentials.get('sas_token'):
                sas_token = credentials.get('sas_token')
                
                if sas_token.startswith('http'):
                    s3_client = BlobServiceClient(account_url=sas_token)
                    from urllib.parse import urlparse
                    parsed = urlparse(sas_token)
                    account_name = parsed.hostname.split('.')[0]
                    credentials['extracted_account_name'] = account_name
                else:
                    account_name = credentials.get('account_name') or credentials.get('access_key_id')
                    if not account_name:
                        raise ValueError("Account name is required when using SAS token parameters")
                    
                    if not sas_token.startswith('?'):
                        sas_token = f"?{sas_token}"
                    
                    account_url = f"https://{account_name}.blob.core.windows.net{sas_token}"
                    s3_client = BlobServiceClient(account_url=account_url)
                
                print(f"✅ Azure client initialized with SAS token")
                
            elif credentials.get('account_key'):
                account_name = credentials.get('account_name') or credentials.get('access_key_id')
                account_key = credentials.get('account_key') or credentials.get('secret_access_key')
                
                if not account_name or not account_key:
                    raise ValueError("Account name and key are required")
                
                account_url = f"https://{account_name}.blob.core.windows.net"
                s3_client = BlobServiceClient(
                    account_url=account_url,
                    credential=account_key
                )
                print(f"✅ Azure client initialized with account key for: {account_name}")
            else:
                raise ValueError("Azure Blob Storage requires connection_string, sas_token, or account_key")
            
            # Test Azure client connection
            try:
                container_client = s3_client.get_container_client(bucket_name)
                blob_list = list(container_client.list_blobs(max_results=1))
                print(f"✅ Azure connection test successful - found container: {bucket_name}")
            except Exception as test_error:
                print(f"⚠️  Azure connection test failed: {str(test_error)}")
        elif provider == "GCP":
            print(111111111111111)
            # GCP Cloud Storage initialization
            from google.cloud import storage
            from google.oauth2 import service_account
            import json
            
            project_id = credentials.get('service_account_json').get('project_id')
            if not project_id:
                raise ValueError("GCP Cloud Storage requires project_id")
            
            if credentials.get('service_account_json'):
                # Handle service account JSON (string or dict)
                service_account_json = credentials.get('service_account_json')
                
                if isinstance(service_account_json, str):
                    try:
                        credentials_info = json.loads(service_account_json)
                    except json.JSONDecodeError:
                        raise ValueError("Invalid service_account_json format")
                else:
                    credentials_info = service_account_json
                
                creds = service_account.Credentials.from_service_account_info(credentials_info)
                s3_client = storage.Client(project=project_id, credentials=creds)
                print("✅ GCP client initialized with service account JSON")
                
            elif credentials.get('service_account_path'):
                # Handle service account key file path
                service_account_path = credentials.get('service_account_path')
                
                try:
                    s3_client = storage.Client.from_service_account_json(
                        service_account_path,
                        project=project_id
                    )
                    print(f"✅ GCP client initialized with service account file: {service_account_path}")
                except Exception as e:
                    raise ValueError(f"Failed to load service account file: {str(e)}")
                    
            elif credentials.get('use_default_credentials', True):
                # Use Application Default Credentials (ADC)
                try:
                    s3_client = storage.Client(project=project_id)
                    print("✅ GCP client initialized with default credentials")
                except Exception as e:
                    raise ValueError(f"Default credentials not available: {str(e)}")
                    
            else:
                raise ValueError("GCP Cloud Storage requires service_account_json, service_account_path, or default credentials")
            
            # Test GCP client connection
            try:
                bucket = s3_client.bucket(bucket_name)
                # Check if bucket exists and is accessible
                if bucket.exists():
                    # Try to list a few objects to verify permissions
                    blobs = list(bucket.list_blobs(max_results=1))
                    print(f"✅ GCP connection test successful - found bucket: {bucket_name}")
                else:
                    print(f"⚠️  GCP bucket '{bucket_name}' not found or not accessible")
            except Exception as test_error:
                print(f"⚠️  GCP connection test failed: {str(test_error)}")

        else:
            # AWS S3 initialization with enhanced region detection
            region = bucket_data.get('region') or 'eu-west-2'
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=credentials.get('access_key_id'),
                aws_secret_access_key=credentials.get('secret_access_key'),
                region_name=region,
                endpoint_url=bucket_data.get('endpoint_url'),
                config=Config(signature_version='s3v4')
            )
            
            # Test and get actual bucket region
            try:
                location = s3_client.get_bucket_location(Bucket=bucket_name)
                actual_region = location['LocationConstraint'] or 'us-east-1'
                print(f"✅ Bucket region detected: {actual_region}")
                
                # If region mismatch, recreate client
                if actual_region != region and actual_region != 'us-east-1':
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=credentials.get('access_key_id'),
                        aws_secret_access_key=credentials.get('secret_access_key'),
                        region_name=actual_region,
                        endpoint_url=bucket_data.get('endpoint_url'),
                        config=Config(signature_version='s3v4')
                    )
                    region = actual_region
                    print(f"🔄 S3 client recreated for region: {actual_region}")
            except Exception as e:
                print(f"⚠️ Using default region: {region}")
            
            print("✅ S3 client initialized")
        
        # List objects in bucket
        response = requests.get(list_objects_endpoint, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        
        s3_files = []
        if isinstance(response_data, dict):
            if 'data' in response_data:
                s3_files = response_data['data']
            else:
                for key, value in response_data.items():
                    if isinstance(value, list) and len(value) > 0:
                        s3_files = value
                        break
        elif isinstance(response_data, list):
            s3_files = response_data
        
        # If thumbnail_path is specified, also get files from thumbnail path
        thumbnail_files_from_path = []
        if thumbnail_path:
            thumbnail_list_endpoint = f"{base_url}/settings/cloud_storage/list-folder-buckets/{user_id}?prefix={thumbnail_path}"
            try:
                response = requests.get(thumbnail_list_endpoint, headers=headers)
                response.raise_for_status()
                thumbnail_response_data = response.json()
                
                if isinstance(thumbnail_response_data, dict):
                    if 'data' in thumbnail_response_data:
                        thumbnail_files_from_path = thumbnail_response_data['data']
                    else:
                        for key, value in thumbnail_response_data.items():
                            if isinstance(value, list) and len(value) > 0:
                                thumbnail_files_from_path = value
                                break
                elif isinstance(thumbnail_response_data, list):
                    thumbnail_files_from_path = thumbnail_response_data
                
                print(f"Found {len(thumbnail_files_from_path)} files in thumbnail path: {thumbnail_path}")
            except Exception as e:
                print(f"⚠️ Could not access thumbnail path {thumbnail_path}: {e}")
        
        if not s3_files:
            print(f"❌ No files found with prefix: {folder_path}")
            builtins.print = original_print
            return False
        
        # Group files by folder and filter
        file_groups = {}
        for file_info in s3_files:
            if not isinstance(file_info, dict):
                continue
                
            key = file_info.get('key') or file_info.get('Key')
            if not key:
                continue
                
            parent_folder = os.path.dirname(key)
            if parent_folder not in file_groups:
                file_groups[parent_folder] = []
            file_groups[parent_folder].append(file_info)
        
        # Add thumbnail files from specified path to appropriate groups
        thumbnail_files_all = []
        if thumbnail_path and thumbnail_files_from_path:
            for file_info in thumbnail_files_from_path:
                if not isinstance(file_info, dict):
                    continue
                    
                key = file_info.get('key') or file_info.get('Key')
                if not key:
                    continue
                
                # Add to thumbnail files list
                thumbnail_files_all.append(file_info)
                
                # Also add to file groups for organization
                parent_folder = os.path.dirname(key)
                if parent_folder not in file_groups:
                    file_groups[parent_folder] = []
                file_groups[parent_folder].append(file_info)
        
        # Select appropriate file extensions
        if file_type == "VIDEO":
            target_extensions = VIDEO_EXTENSIONS.keys()
        else:
            target_extensions = IMAGE_EXTENSIONS.keys()
        
        # Collect all media files and thumbnail files to process
        all_media_files = []
        json_files_lookup = {}
        thumbnail_files_lookup = {}
        
        for folder, files in file_groups.items():
            # Filter media files based on type and base_file parameter
            if base_file:
                if file_type == "VIDEO":
                    media_files = [f for f in files 
                                 if any(f['key'].lower().endswith(ext) for ext in target_extensions)
                                 and f['key'].endswith(f"{base_file}.mp4")
                                 and not is_thumbnail_file(f['key'])]
                else:  # IMAGE
                    media_files = [f for f in files 
                                 if any(f['key'].lower().endswith(ext) for ext in target_extensions)
                                 and base_file in os.path.basename(f['key'])
                                 and not is_thumbnail_file(f['key'])]
            else:
                media_files = [f for f in files 
                             if any(f['key'].lower().endswith(ext) for ext in target_extensions)
                             and not is_thumbnail_file(f['key'])]
            
            # Find thumbnail files - check both local folder and _thumbnails subfolder
            thumbnail_files = []
            
            # Find thumbnails in the same folder
            local_thumbnails = [f for f in files 
                             if any(f['key'].lower().endswith(ext) for ext in target_extensions)
                             and is_thumbnail_file(f['key'])]
            thumbnail_files.extend(local_thumbnails)
            
            # Check for thumbnails in _thumbnails subfolder
            thumbnails_subfolder = f"{folder}/_thumbnails" if folder else "_thumbnails"
            thumbnails_in_subfolder = [f for f in files 
                                     if f['key'].startswith(thumbnails_subfolder)
                                     and any(f['key'].lower().endswith(ext) for ext in target_extensions)
                                     and is_thumbnail_file(f['key'])]
            thumbnail_files.extend(thumbnails_in_subfolder)
            
            # If thumbnail_path is specified, also search for thumbnails there
            if thumbnail_path and thumbnail_files_all:
                # Find thumbnails from the specified path that might match this folder
                for thumb_file in thumbnail_files_all:
                    if any(thumb_file['key'].lower().endswith(ext) for ext in target_extensions):
                        thumbnail_files.append(thumb_file)
            
            # Find JSON files
            json_files = [f for f in files if f['key'].lower().endswith('.json')]
            
            # Add media files to processing list
            all_media_files.extend(media_files)
            
            # Store thumbnail files for this folder
            thumbnail_files_lookup[folder] = thumbnail_files
            
            # Store first JSON file for this folder
            if json_files:
                json_files_lookup[folder] = json_files[0]['key']
        
        if not all_media_files:
            print(f"❌ No {file_type.lower()} files found to process")
            builtins.print = original_print
            return False
        
        # Count total thumbnails found
        total_thumbnails = sum(len(thumbs) for thumbs in thumbnail_files_lookup.values())
        
        total_files = len(all_media_files)
        
        # Check if we need to create thumbnails and separate files
        files_without_thumbnails = []
        files_with_thumbnails = []
        
        print(f"📊 ANALYZING FILES:")
        print(f"   📁 Total {file_type.lower()} files found: {total_files}")
        print(f"   🖼️  Total existing thumbnails: {total_thumbnails}")
        
        # Separate files with and without thumbnails
        for media_file in all_media_files:
            media_key = media_file['key']
            folder = os.path.dirname(media_key)
            thumbnail_key = find_matching_thumbnail(media_key, thumbnail_files_lookup.get(folder, []), thumbnail_path)
            
            if thumbnail_key:
                files_with_thumbnails.append(media_file)
            else:
                files_without_thumbnails.append(media_file)
        
        print(f"   ✅ Files with thumbnails: {len(files_with_thumbnails)}")
        print(f"   ⚠️  Files without thumbnails: {len(files_without_thumbnails)}")
        
        # Combine all files for batch processing
        all_files_to_process = files_with_thumbnails + files_without_thumbnails
        
        if not all_files_to_process:
            builtins.print = original_print
            return False
        
        total_files = len(all_files_to_process)
        total_batches = math.ceil(total_files / batch_size)
        
        print(f"\n📊 BATCH PROCESSING PLAN:")
        print(f"   📁 Total {file_type.lower()} files to process: {total_files}")
        print(f"   📦 Total batches: {total_batches}")
        print(f"   🔢 Files per batch: {batch_size}")
        if create_thumbnails and file_type == "IMAGE":
            print(f"   🖼️  Will create thumbnails per batch as needed")
        print("=" * 60)
        
        # Process files in batches with thumbnail creation per batch
        overall_successful = []
        overall_failed = []
        global_failed_items = []  # Track all failed items for final retry
        
        # Split files into batches of specified size
        file_batches = list(chunk_list(all_files_to_process, batch_size))
        
        for batch_num, batch_files in enumerate(file_batches, 1):
            
            print(f"\n{'='*60}")
            print(f"📦 BATCH {batch_num}/{total_batches} - Processing {len(batch_files)} files")
            print(f"{'='*60}")
            
            # Check which files in this batch need thumbnails
            batch_files_needing_thumbnails = []
            batch_files_with_thumbnails = []
            
            for media_file in batch_files:
                media_key = media_file['key']
                folder = os.path.dirname(media_key)
                thumbnail_key = find_matching_thumbnail(media_key, thumbnail_files_lookup.get(folder, []), thumbnail_path)
                
                if thumbnail_key:
                    batch_files_with_thumbnails.append(media_file)
                else:
                    batch_files_needing_thumbnails.append(media_file)
            
            print(f"   📊 Batch {batch_num} Analysis:")
            print(f"      ✅ Files with existing thumbnails: {len(batch_files_with_thumbnails)}")
            print(f"      🔄 Files needing thumbnails: {len(batch_files_needing_thumbnails)}")
            
            # Create thumbnails for files in this batch that need them
            if batch_files_needing_thumbnails and create_thumbnails and file_type == "IMAGE":
                print(f"\n   🔄 Creating thumbnails for batch {batch_num}...")
                
                # Prepare thumbnail creation tasks for this batch only
                thumbnail_tasks = []
                created_thumbnails = {}
                
                for media_file in batch_files_needing_thumbnails:
                    media_key = media_file['key']
                    file_name = os.path.basename(media_key)
                    base_name = os.path.splitext(file_name)[0]
                    folder = os.path.dirname(media_key)
                    
                    # Create unique thumbnail key for each image
                    if thumbnail_path:
                        # Use custom thumbnail path
                        thumbnail_key = f"{thumbnail_path}/{base_name}_thumbnail.jpg"
                    else:
                        # Create thumbnails in _thumbnails subfolder
                        thumbnail_folder = f"{folder}/_thumbnails" if folder else "_thumbnails"
                        thumbnail_key = f"{thumbnail_folder}/{base_name}_thumbnail.jpg"
                    
                    # Build presigned URL for media access
                    media_url = build_presigned_url(provider, bucket_name, media_key, credentials, region)
                    if media_url:
                        # Include region in task data for AWS S3
                        task_data = (media_url, thumbnail_key, provider, bucket_name, credentials, s3_client, file_name, region)
                        thumbnail_tasks.append(task_data)
                        created_thumbnails[media_key] = thumbnail_key
                
                if thumbnail_tasks:
                    print(f"      🚀 Creating {len(thumbnail_tasks)} thumbnails...")
                    
                    # Create thumbnails in parallel for this batch
                    successful_thumbnails, failed_tasks = image_processor.bulk_create_thumbnails(
                        thumbnail_tasks, max_workers=max_workers
                    )
                    
                    print(f"      ✅ Created: {len(successful_thumbnails)} thumbnails")
                    if failed_tasks:
                        print(f"      ❌ Failed: {len(failed_tasks)} thumbnails")
                        for task, error in failed_tasks:
                            print(f"         - {error}")
                    
                    # Update thumbnail lookup with newly created thumbnails for this batch
                    batch_successfully_processed_files = []
                    for media_file in batch_files_needing_thumbnails:
                        media_key = media_file['key']
                        folder = os.path.dirname(media_key)
                        
                        if media_key in created_thumbnails:
                            thumbnail_key = created_thumbnails[media_key]
                            
                            # Check if thumbnail was successfully created
                            if thumbnail_key in successful_thumbnails:
                                # Add to thumbnail lookup
                                if folder not in thumbnail_files_lookup:
                                    thumbnail_files_lookup[folder] = []
                                thumbnail_files_lookup[folder].append({'key': thumbnail_key})
                                
                                # Also add to the thumbnail folder lookup
                                thumbnail_folder = os.path.dirname(thumbnail_key)
                                if thumbnail_folder not in thumbnail_files_lookup:
                                    thumbnail_files_lookup[thumbnail_folder] = []
                                thumbnail_files_lookup[thumbnail_folder].append({'key': thumbnail_key})
                                
                                # Add to successfully processed files
                                batch_successfully_processed_files.append(media_file)
                    
                    # Update the batch files list to include files with newly created thumbnails
                    final_batch_files = batch_files_with_thumbnails + batch_successfully_processed_files
                    
                    print(f"      📊 Batch {batch_num} ready: {len(final_batch_files)} files with thumbnails")
                    
                else:
                    print(f"      ❌ No valid thumbnail tasks for batch {batch_num}")
                    final_batch_files = batch_files_with_thumbnails
            
            else:
                # No thumbnail creation needed or not enabled
                final_batch_files = batch_files_with_thumbnails
                print(f"      📊 Batch {batch_num} ready: {len(final_batch_files)} files")
            
            # Skip empty batches
            if not final_batch_files:
                print(f"      ⚠️  Batch {batch_num}: No files with thumbnails to process")
                continue
                
            # Process the current batch immediately
            batch_items = process_single_batch(
                final_batch_files, batch_num, total_batches, video_processor, image_processor,
                provider, bucket_name, credentials, s3_client, json_files_lookup, 
                thumbnail_files_lookup, file_type, thumbnail_path, region
            )
            
            if not batch_items:
                print(f"      ❌ Batch {batch_num}: No items to register")
                continue
            
            # Register this batch with API
            print(f"\n   🔄 Registering batch {batch_num} ({len(batch_items)} items) with API...")
            
            payload = {
                "project_id": project_id,
                "items": batch_items
            }
            
            batch_pbar = tqdm(total=100, desc=f"Batch {batch_num} API", leave=False)
            try:
                # Register batch
                response = requests.post(register_endpoint, json=payload, headers=headers)
                batch_pbar.update(30)
                response.raise_for_status()
                result = response.json()
                
                batch_id = result.get('batch_id')
                media_items = result.get('items', [])
                
                if batch_id and media_items:
                    print(f"      ✅ Registered batch {batch_num} with ID: {batch_id}")
                    batch_pbar.update(20)
                    
                    # Confirm each media item in this batch with retry logic
                    batch_successful = []
                    batch_failed = []
                    
                    confirm_pbar = tqdm(media_items, desc=f"Confirming batch {batch_num}", leave=False)
                    
                    for item in confirm_pbar:
                        media_id = item.get('media_id')
                        file_name = item.get('file_name')
                        
                        if not media_id:
                            continue
                        
                        confirm_pbar.set_description(f"Confirming: {file_name}")
                        confirm_url = confirm_media_endpoint.format(media_id)
                        
                        # Try confirmation with retries
                        success, error = retry_confirmation(confirm_url, headers, media_id, file_name)
                        
                        if success:
                            batch_successful.append({'name': file_name, 'id': media_id})
                        else:
                            batch_failed.append(file_name)
                            global_failed_items.append({
                                'media_id': media_id,
                                'file_name': file_name,
                                'confirm_url': confirm_url,
                                'error': error,
                                'batch_num': batch_num
                            })
                        
                        time.sleep(0.1)  # Brief delay between confirmations
                    
                    confirm_pbar.close()
                    batch_pbar.update(30)
                    
                    # Confirm the entire batch with retry logic
                    batch_url = batch_confirm_endpoint.format(batch_id)
                    batch_success, batch_error = retry_batch_confirmation(batch_url, headers, batch_id)
                    
                    if batch_success:
                        print(f"      ✅ Batch {batch_num} confirmed successfully!")
                        batch_pbar.update(20)
                        
                        # Add to overall results
                        overall_successful.extend(batch_successful)
                        overall_failed.extend(batch_failed)
                        
                    else:
                        print(f"      ❌ Failed to confirm batch {batch_num} after retries: {batch_error}")
                        overall_failed.extend([item['file_name'] for item in batch_items])
                        # Add all items from this batch to global failed items
                        for item in media_items:
                            if item.get('media_id') and item.get('file_name'):
                                global_failed_items.append({
                                    'media_id': item['media_id'],
                                    'file_name': item['file_name'],
                                    'confirm_url': confirm_media_endpoint.format(item['media_id']),
                                    'error': f"Batch confirmation failed: {batch_error}",
                                    'batch_num': batch_num
                                })
                
                else:
                    print(f"      ❌ Registration failed for batch {batch_num}")
                    failed_items_from_batch = [item['file_name'] for item in batch_items]
                    overall_failed.extend(failed_items_from_batch)
                    
                    # Add items to global failed list for final retry
                    for item in batch_items:
                        global_failed_items.append({
                            'media_id': f"unknown_{item['file_name']}",
                            'file_name': item['file_name'],
                            'confirm_url': None,
                            'error': "Registration returned no batch_id or media_items",
                            'batch_num': batch_num
                        })
            
            except Exception as e:
                print(f"      ❌ API request failed for batch {batch_num}: {str(e)}")
                failed_items_from_batch = [item['file_name'] for item in batch_items]
                overall_failed.extend(failed_items_from_batch)
                
                # Add items to global failed list for final retry
                for item in batch_items:
                    global_failed_items.append({
                        'media_id': f"unknown_{item['file_name']}",  # No media_id available
                        'file_name': item['file_name'],
                        'confirm_url': None,  # No URL available since registration failed
                        'error': f"Registration failed: {str(e)}",
                        'batch_num': batch_num
                    })
            
            batch_pbar.close()
            
            # Brief pause between batches
            if batch_num < total_batches:
                print(f"      ⏸️  Completed batch {batch_num}, moving to next batch...")
                time.sleep(0.05)
        
        # Final retry for all failed items
        if global_failed_items:
            print(f"\n{'='*60}")
            print(f"🔄 FINAL RETRY ATTEMPT")
            print(f"{'='*60}")
            print(f"📋 Attempting final retry for {len(global_failed_items)} failed items...")
            
            final_retry_successful = []
            final_retry_failed = []
            
            retry_pbar = tqdm(global_failed_items, desc="Final retry", leave=False)
            
            for failed_item in retry_pbar:
                media_id = failed_item['media_id']
                file_name = failed_item['file_name']
                confirm_url = failed_item['confirm_url']
                original_error = failed_item['error']
                batch_num = failed_item['batch_num']
                
                retry_pbar.set_description(f"Final retry: {file_name}")
                
                # Skip items where registration failed (no confirm_url)
                if not confirm_url or confirm_url is None:
                    final_retry_failed.append({
                        'name': file_name,
                        'id': media_id,
                        'original_error': original_error,
                        'final_retry_error': "Cannot retry - registration failed",
                        'batch_num': batch_num
                    })
                    continue
                
                # Single retry attempt for final retry
                try:
                    confirm_response = requests.post(confirm_url, headers=headers, timeout=30)
                    confirm_response.raise_for_status()
                    
                    final_retry_successful.append({
                        'name': file_name, 
                        'id': media_id,
                        'original_batch': batch_num
                    })
                    
                    # Remove from overall_failed and add to overall_successful
                    if file_name in overall_failed:
                        overall_failed.remove(file_name)
                    
                    # Check if already in successful list
                    if not any(item['name'] == file_name for item in overall_successful):
                        overall_successful.append({'name': file_name, 'id': media_id})
                    
                    print(f"      ✅ Final retry successful: {file_name}")
                    
                except Exception as e:
                    final_retry_failed.append({
                        'name': file_name,
                        'id': media_id,
                        'original_error': original_error,
                        'final_retry_error': str(e),
                        'batch_num': batch_num
                    })
                    print(f"      ❌ Final retry failed: {file_name} - {str(e)}")
                
                time.sleep(0.1)  # Brief delay
            
            retry_pbar.close()
            
            if final_retry_successful:
                print(f"\n🎉 Final retry recovered {len(final_retry_successful)} items!")
                for item in final_retry_successful:
                    print(f"   ✅ {item['name']} (from batch {item['original_batch']})")
            
            if final_retry_failed:
                print(f"\n❌ {len(final_retry_failed)} items failed final retry:")
                for item in final_retry_failed:
                    print(f"   ❌ {item['name']} (batch {item['batch_num']})")
                    print(f"      Original error: {item['original_error']}")
                    print(f"      Final retry error: {item['final_retry_error']}")
        
        else:
            print(f"\n✅ No failed items to retry - all confirmations succeeded!")

        # Final summary
        total_processed = len(overall_successful) + len(overall_failed)
        print(f"\n{'='*60}")
        print(f"🏁 PROCESSING COMPLETE WITH RETRY SYSTEM")
        print(f"{'='*60}")
        print(f"✅ Successful files: {len(overall_successful)}")
        print(f"❌ Failed files: {len(overall_failed)}")
        
        if global_failed_items:
            print(f"🔄 Items that needed retry: {len(global_failed_items)}")
            final_recovered = len([item for item in global_failed_items 
                                 if any(s.get('name') == item['file_name'] for s in overall_successful)])
            print(f"🎯 Items recovered on final retry: {final_recovered}")
        
        success_rate = (len(overall_successful) / total_processed) * 100 if total_processed > 0 else 0
        print(f"📈 Final Success Rate: {success_rate:.1f}%")
        
        if global_failed_items:
            retry_success_rate = len([item for item in global_failed_items 
                                    if any(s.get('name') == item['file_name'] for s in overall_successful)]) / len(global_failed_items) * 100
            print(f"🔄 Retry Recovery Rate: {retry_success_rate:.1f}%")
        
        builtins.print = original_print
        print(f"📄 Log saved to {log_filepath}")
        
        return len(overall_failed) == 0
        
    except Exception as e:
        builtins.print = original_print
        print(f"❌ An error occurred: {str(e)}")
        print(f"📄 Log saved to {log_filepath}")
        return False

def main():
    """Main function with batch processing and smart thumbnail handling"""
    parser = argparse.ArgumentParser(description='Batch S3 Media Registration with Smart Thumbnail Handling')
    
    parser.add_argument('--user_id', type=str, required=True, help='User ID for S3 access')
    parser.add_argument('--project_id', type=str, required=True, help='Project ID to register media to')
    parser.add_argument('--bucket_folder_path', type=str, required=True, help='S3 folder path in bucket')
    parser.add_argument('--base_url', type=str, default='http://127.0.0.1:8000', help='Base API URL')
    parser.add_argument('--token', type=str, required=True, help='API Authentication token')
    parser.add_argument('--base_file', type=str, help='Base file pattern to filter media')
    parser.add_argument('--file_type', type=str, choices=['VIDEO', 'IMAGE'], default='IMAGE', 
                       help='Type of files to process: VIDEO or IMAGE (default: IMAGE)')
    parser.add_argument('--thumbnail_path', type=str, help='Custom path for thumbnail files (optional)')
    parser.add_argument('--create_thumbnails', action='store_true', default=True,
                       help='Create thumbnails for images that don\'t have them (default: True)')
    parser.add_argument('--no_create_thumbnails', action='store_false', dest='create_thumbnails',
                       help='Skip thumbnail creation, only process files with existing thumbnails')
    parser.add_argument('--max_workers', type=int, default=8,
                       help='Maximum number of parallel workers for thumbnail creation (default: 8)')
    
    args = parser.parse_args()
    
    print(f"🚀 BATCH S3 {args.file_type} PROCESSOR WITH SMART THUMBNAILS")
    print("✅ Using existing thumbnail files when available")
    if args.create_thumbnails:
        print("✅ Auto-creating missing thumbnails with parallel processing")
        print(f"⚡ Using {args.max_workers} parallel workers for thumbnail creation")
    else:
        print("⚠️  Skipping thumbnail creation - only processing files with existing thumbnails")
    
    if args.thumbnail_path:
        print(f"📁 Custom thumbnail path: {args.thumbnail_path}")
    else:
        print(f"📁 Default thumbnail location: _thumbnails subfolders")
    
    # Show batch sizes
    if args.file_type == "IMAGE":
        print(f"📦 Processing 100 images per batch")
    else:
        print(f"📦 Processing 10 videos per batch")
    
    print("=" * 60)
    
    result = register_existing_s3_files(
        base_url=args.base_url,
        token=args.token,
        user_id=args.user_id,
        project_id=args.project_id,
        folder_path=args.bucket_folder_path,
        base_file=args.base_file,
        file_type=args.file_type,
        thumbnail_path=args.thumbnail_path,
        create_thumbnails=args.create_thumbnails,
        max_workers=args.max_workers
    )
    
    if result:
        print(f"\n🎉 All {args.file_type.lower()} batches processed successfully!")
        return 0
    else:
        print(f"\n⚠️ Some {args.file_type.lower()} batches encountered errors.")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)