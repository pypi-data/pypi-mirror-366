import os
import shutil
from PIL import Image
import requests
from requests.exceptions import RequestException
import time
from pathlib import Path
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn
)
from rich.console import Console
from rich.prompt import Prompt
from rich import print
import math
import cv2  # Add OpenCV for video processing

console = Console()

# Default batch size
DEFAULT_BATCH_SIZE = 10

# Supported file types
SUPPORTED_EXTENSIONS = {
    # Images
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.bmp': 'image/bmp',
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff',
    '.webp': 'image/webp',
    # Videos
    '.mp4': 'application/octet-stream',
    '.mov': 'application/octet-stream',
    '.avi': 'application/octet-stream',
    '.mkv': 'application/octet-stream',
    '.hevc': 'application/octet-stream',
    # Other formats
    '.dcm': 'application/octet-stream',
    '.gz': 'application/octet-stream',
    '.ndpi': 'application/octet-stream',
    '.nii': 'application/octet-stream',
    '.pdf': 'application/octet-stream',
    '.rvg': 'application/octet-stream',
    '.svs': 'application/octet-stream'
}

def convert_rgba_to_rgb(image):
    """Convert RGBA image to RGB with white background"""
    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'RGBA':
            background.paste(image, mask=image.split()[3])
        elif image.mode == 'LA':
            background.paste(image, mask=image.split()[1])
        else:
            background.paste(image, mask=image.info['transparency'])
        return background
    return image.convert('RGB')

def cleanup_thumbnails(folder_path):
    """Clean up thumbnail folder"""
    thumbnail_folder = os.path.join(folder_path, "_thumbnail")
    try:
        if os.path.exists(thumbnail_folder):
            shutil.rmtree(thumbnail_folder)
            print(f"[green]Cleaned up thumbnail folder[/green]")
    except Exception as e:
        print(f"[yellow]Warning: Could not clean up thumbnail folder: {str(e)}[/yellow]")

def retry_request(func, progress, task_id=None, retries=10, delay=2, *args, **kwargs):
    """Retry function execution with progress tracking - 10 retries"""
    for attempt in range(retries):
        try:
            if progress and task_id:
                progress.update(task_id, description=f"[cyan]Attempt {attempt + 1}/{retries}...")
            result = func(*args, **kwargs)
            if result:
                return result
            # If function returns False, also retry
            if progress and task_id:
                progress.update(task_id, description=f"[yellow]Attempt {attempt + 1} returned False, retrying...")
            if attempt < retries - 1:
                time.sleep(delay)
        except Exception as e:
            if progress and task_id:
                progress.update(task_id, description=f"[yellow]Attempt {attempt + 1} failed with error: {str(e)}")
            if attempt < retries - 1:
                time.sleep(delay)
    
    # If we get here, all attempts failed
    if progress and task_id:
        progress.update(task_id, description=f"[red]Failed after {retries} attempts")
    return None



def is_video_file(file_path):
    """Check if the file is a video based on extension"""
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.hevc']
    
    # Convert Path object to string if needed
    if hasattr(file_path, 'suffix'):
        extension = file_path.suffix.lower()
    else:
        extension = os.path.splitext(file_path)[1].lower() if isinstance(file_path, str) else ""
        
    return extension in video_extensions
def get_files_sorted_by_folder(folder_path):
    """Recursively collect and sort image and video files with proper numerical ordering"""
    folder = Path(folder_path)
    
    # Get all supported files
    files = [file for file in folder.rglob('*.*') 
             if file.suffix.lower() in SUPPORTED_EXTENSIONS.keys()]
    
    # Define a natural sort key function for frame_X style filenames
    def natural_sort_key(path):
        import re
        # Extract numbers from the filename
        numbers = re.findall(r'\d+', path.name)
        if numbers:
            # If we found numbers, use the first one for sorting
            try:
                return (0, int(numbers[0]), path.name)
            except (ValueError, IndexError):
                pass
        # Otherwise sort by filename
        return (1, 0, path.name)
    
    # Sort files using natural sorting
    return sorted(files, key=natural_sort_key)

def generate_video_thumbnail(video_path, thumbnail_path):
    """Generate thumbnail from the first frame of a video"""
    try:
        # Open the video file
        video = cv2.VideoCapture(str(video_path))
        
        # Check if video opened successfully
        if not video.isOpened():
            print(f"[red]Could not open video {video_path}[/red]")
            return False
        
        # Read the first frame
        success, frame = video.read()
        if not success:
            print(f"[red]Could not read first frame from {video_path}[/red]")
            return False
        
        # Convert BGR to RGB (OpenCV uses BGR by default)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create PIL Image from the frame
        img = Image.fromarray(frame_rgb)
        
        # Resize for thumbnail
        img.thumbnail((200, 200))
        
        # Save thumbnail
        img.save(thumbnail_path, "JPEG", quality=85)
        
        # Release video
        video.release()
        
        return True
    except Exception as e:
        print(f"[red]Error generating thumbnail for {video_path}: {str(e)}[/red]")
        return False

def get_video_dimensions(video_path):
    """Get video width and height"""
    try:
        video = cv2.VideoCapture(str(video_path))
        if not video.isOpened():
            return 0, 0
            
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        video.release()
        return width, height
    except Exception as e:
        print(f"[red]Error getting video dimensions for {video_path}: {str(e)}[/red]")
        return 0, 0

def process_images_and_send_request(base_url, token, project_id, folder_path, files_batch=None, batch_index=0, total_batches=1, use_metadata=False, media_type="IMAGE"):
    """Process images and videos with progress tracking"""
    # Set up API endpoints based on media type
    # Will be determined for each item individually during processing
    presigned_url_endpoint = f"{base_url}/uploads/generate-presigned-url/{{media_id}}"
    confirm_upload_endpoint = f"{base_url}/uploads/confirm-upload/{{media_id}}"
    batch_confirm_endpoint = f"{base_url}/uploads/batch-confirm/{{batch_id}}"

    try:
        # Create thumbnail folder
        thumbnail_folder = os.path.join(folder_path, "_thumbnail")
        os.makedirs(thumbnail_folder, exist_ok=True)

        # If no specific batch is provided, use all files (for backwards compatibility)
        if files_batch is None:
            files_batch = get_files_sorted_by_folder(folder_path)
            if not files_batch:
                print("[red]No supported files found in the specified folder[/red]")
                return None
            
            # Apply media type filter if specified
            if media_type == "VIDEO":
                files_batch = [f for f in files_batch if is_video_file(f)]
                if not files_batch:
                    print("[red]No video files found in the specified folder[/red]")
                    return None
            elif media_type == "IMAGE":
                files_batch = [f for f in files_batch if not is_video_file(f)]
                if not files_batch:
                    print("[red]No image files found in the specified folder[/red]")
                    return None

        file_data_list = []
        batch_num = batch_index + 1
        
        # Create progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            expand=True
        ) as progress:
            # Add main tasks
            batch_display = f" (Batch {batch_num}/{total_batches})" if total_batches > 1 else ""
            scan_task = progress.add_task(f"[cyan]Processing files{batch_display}...", total=len(files_batch))
            
            # Process each file
            for file_path in files_batch:
                file_name = os.path.basename(file_path)
                progress.update(scan_task, description=f"[cyan]Processing {file_name}")

                try:
                    # Check if it's a video file
                    is_video = is_video_file(file_path)
                    file_media_type = "VIDEO" if is_video else "IMAGE"
                    
                    # Skip if it doesn't match the specified media type filter
                    if media_type != "AUTO" and file_media_type != media_type:
                        print(f"[yellow]Skipping {file_name} - not matching media type filter: {media_type}[/yellow]")
                        progress.advance(scan_task)
                        continue
                    
                    if is_video:
                        # Generate thumbnail from first frame
                        thumbnail_path = os.path.join(thumbnail_folder, 
                                                    f"{os.path.splitext(file_name)[0]}_thumbnail.jpeg")
                        success = generate_video_thumbnail(file_path, thumbnail_path)
                        
                        if not success:
                            print(f"[yellow]Warning: Could not generate thumbnail for {file_name}, using placeholder[/yellow]")
                            # Create a blank thumbnail with text
                            img = Image.new('RGB', (200, 200), color=(100, 100, 100))
                            img.save(thumbnail_path, "JPEG", quality=85)
                        
                        # Get video dimensions
                        width, height = get_video_dimensions(file_path)
                    else:
                        # Handle image files as before
                        with Image.open(file_path) as img:
                            width, height = img.size
                            
                            # Create a copy for thumbnail
                            thumb_img = img.copy()
                            thumb_img.thumbnail((200, 200))
                            
                            # Convert RGBA to RGB before saving as JPEG
                            thumb_img = convert_rgba_to_rgb(thumb_img)
                            
                            thumbnail_path = os.path.join(thumbnail_folder, 
                                                       f"{os.path.splitext(file_name)[0]}_thumbnail.jpeg")
                            thumb_img.save(thumbnail_path, "JPEG", quality=85)
                    
                    # Add file data with media_type
                    file_data = {
                        "file_name": file_name,
                        "width": width,
                        "height": height,
                        "media_type": file_media_type
                    }
                    
                    # Only include metadata if enabled - specially important for videos
                    if use_metadata:
                        # Look for associated metadata JSON file
                        meta_data_filename = None
                        base_name = os.path.splitext(file_name)[0]
                        
                        # First check for a JSON file with the same base name
                        potential_json_path = os.path.join(folder_path, f"{base_name}.json")
                        if os.path.exists(potential_json_path):
                            meta_data_filename = os.path.basename(potential_json_path)
                            print(f"[cyan]Found matching JSON metadata file: {meta_data_filename}[/cyan]")
                        
                        # If not found and not a video, search for any JSON file in the folder
                        if not meta_data_filename and not is_video:
                            # Get all JSON files in the folder
                            json_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.json')]
                            if json_files:
                                meta_data_filename = json_files[0]
                                print(f"[cyan]Using JSON metadata file: {meta_data_filename}[/cyan]")
                        
                        # Add metadata filename if available
                        if meta_data_filename:
                            file_data["meta_data"] = meta_data_filename
                        elif is_video and media_type == "VIDEO":
                            # For videos with media_type=VIDEO and use_metadata=True, 
                            # we need to track that we will be generating a JSON file
                            # Mark this for auto-generation in the upload step
                            print(f"[yellow]No matching JSON file found for video: {file_name}. Will generate one.[/yellow]")
                            file_data["needs_metadata_generation"] = True
                    
                    file_data_list.append(file_data)
                        
                except Exception as e:
                    print(f"[red]Failed to process {file_name}: {str(e)}[/red]")
                    
                progress.advance(scan_task)

            # Skip further processing if no files were processed
            if not file_data_list:
                print("[red]No files were successfully processed[/red]")
                return None

            # Send initial request
            batch_info = f" for batch {batch_num}/{total_batches}" if total_batches > 1 else ""
            progress.update(scan_task, description=f"[cyan]Sending metadata to server{batch_info}...")
            
            # Group items by media type
            image_items = [item for item in file_data_list if item["media_type"] == "IMAGE"]
            video_items = [item for item in file_data_list if item["media_type"] == "VIDEO"]
            
            # Prepare headers
            headers = {'Authorization': f'Bearer {token}'}
            
            # Initialize response_json and batch_id
            response_json = {"items": []}
            batch_id = None
            
            try:
                # Process image items if any exist
                if image_items:
                    image_api_endpoint = f"{base_url}/uploads/entry-datas?media_type=IMAGE"
                    image_payload = {
                        "project_id": project_id,
                        "items": image_items
                    }
                    
                    # Use retry for the image request
                    max_retries = 5
                    for attempt in range(max_retries):
                        try:
                            progress.update(scan_task, description=f"[cyan]Sending IMAGE data to server{batch_info}...")
                            response = requests.post(image_api_endpoint, json=image_payload, headers=headers)
                            response.raise_for_status()
                            image_response_json = response.json()
                            
                            # Store batch_id from first response (images)
                            if 'batch_id' in image_response_json and batch_id is None:
                                batch_id = image_response_json['batch_id']
                            
                            # Combine items
                            response_json["items"].extend(image_response_json.get("items", []))
                            break
                        except requests.exceptions.RequestException as e:
                            if attempt < max_retries - 1:
                                print(f"[yellow]IMAGE API request attempt {attempt + 1}/{max_retries} failed: {str(e)}. Retrying...[/yellow]")
                                time.sleep(3)
                            else:
                                raise
                
                # Process video items if any exist
                if video_items:
                    video_api_endpoint = f"{base_url}/uploads/entry-datas?media_type=VIDEO"
                    
                    # Remove our custom metadata flag before sending to server
                    for item in video_items:
                        if "needs_metadata_generation" in item:
                            del item["needs_metadata_generation"]
                            
                    video_payload = {
                        "project_id": project_id,
                        "items": video_items
                    }
                    
                    # Use retry for the video request
                    max_retries = 5
                    for attempt in range(max_retries):
                        try:
                            progress.update(scan_task, description=f"[cyan]Sending VIDEO data to server{batch_info}...")
                            response = requests.post(video_api_endpoint, json=video_payload, headers=headers)
                            response.raise_for_status()
                            video_response_json = response.json()
                            
                            # Store batch_id if not already set (from videos if no images)
                            if 'batch_id' in video_response_json and batch_id is None:
                                batch_id = video_response_json['batch_id']
                            
                            # Combine items
                            response_json["items"].extend(video_response_json.get("items", []))
                            break
                        except requests.exceptions.RequestException as e:
                            if attempt < max_retries - 1:
                                print(f"[yellow]VIDEO API request attempt {attempt + 1}/{max_retries} failed: {str(e)}. Retrying...[/yellow]")
                                time.sleep(3)
                            else:
                                raise
                
                # Check if we have a batch_id
                if batch_id is None:
                    print(f"[red]Batch ID not found in any response{batch_info}[/red]")
                    return None
                    
                # Add batch_id to response_json
                response_json["batch_id"] = batch_id
                
                failed_files = []
                
                # Create upload tasks
                upload_task = progress.add_task(
                    f"[cyan]Uploading files{batch_info}...",
                    total=len(response_json['items']) * 2  # *2 for main files and thumbnails
                )
                
                # Add information about metadata generation back to items for the upload phase
                for i, item in enumerate(response_json['items']):
                    file_name = item['file_name']
                    # Find the original item data that might have needs_metadata_generation flag
                    original_item = next((x for x in file_data_list if x['file_name'] == file_name), None)
                    if original_item and original_item.get('needs_metadata_generation', False):
                        item['needs_metadata_generation'] = True
                
                # Process each item
                for item in response_json['items']:
                    media_id = item['media_id']
                    file_name = item['file_name']
                    needs_metadata_generation = item.get('needs_metadata_generation', False)
                    
                    progress.update(upload_task, description=f"[cyan]Uploading {file_name}")
                    
                    # Get presigned URLs and upload
                    success = retry_request(
                        request_presigned_urls,
                        progress,
                        upload_task,
                        media_id=media_id,
                        file_name=file_name,
                        token=token,
                        folder_path=folder_path,
                        thumbnail_folder=thumbnail_folder,
                        presigned_url_endpoint=presigned_url_endpoint,
                        confirm_upload_endpoint=confirm_upload_endpoint,
                        use_metadata=use_metadata,
                        needs_metadata_generation=needs_metadata_generation
                    )
                    
                    if success:
                        progress.update(upload_task, description=f"[cyan]Confirming {file_name}")
                        confirm_success = retry_request(
                            confirm_upload,
                            progress,
                            upload_task,
                            media_id=media_id,
                            token=token,
                            confirm_upload_endpoint=confirm_upload_endpoint
                        )
                        if not confirm_success:
                            failed_files.append(file_name)
                    else:
                        failed_files.append(file_name)
                    
                    progress.advance(upload_task, 2)
                
                # Log any failed files for this batch
                if failed_files:
                    print(f"[yellow]Warning: {len(failed_files)} files failed in batch {batch_num}[/yellow]")
                    print(f"[yellow]Failed files: {', '.join(failed_files[:5])}{'...' if len(failed_files) > 5 else ''}[/yellow]")
                    
                return batch_id, batch_confirm_endpoint
                
            except Exception as e:
                print(f"[red]Error during upload process{batch_info}: {str(e)}[/red]")
                return None, None
    finally:
        # Only clean up thumbnails if this is the last batch or not using batches
        if batch_index == total_batches - 1 or total_batches == 1:
            cleanup_thumbnails(folder_path)

def request_presigned_urls(media_id, file_name, token, folder_path, thumbnail_folder, presigned_url_endpoint, confirm_upload_endpoint, use_metadata=False, needs_metadata_generation=False):
    """Request presigned URLs and upload files"""
    formatted_presigned_url = presigned_url_endpoint.format(media_id=media_id)
    
    # Determine correct file type based on extension
    extension = os.path.splitext(file_name)[1].lower()
    file_type = SUPPORTED_EXTENSIONS.get(extension, 'application/octet-stream')
    
    # Check if this is a video file
    is_video = is_video_file(file_name)
    
    payload = {
        "file_key": file_name,
        "file_type": file_type
    }
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.post(formatted_presigned_url, json=payload, headers=headers)
    response.raise_for_status()

    presigned_urls = response.json()

    main_url = presigned_urls['upload_url']
    thumbnail_url = presigned_urls['thumbnail_url']
    meta_data_url = presigned_urls.get('meta_data_url')  # Get metadata URL if available
    
    # Upload files
    file_path = os.path.join(folder_path, file_name)
    thumbnail_path = os.path.join(thumbnail_folder, f"{os.path.splitext(file_name)[0]}_thumbnail.jpeg")
    
    # For main file, if it's a PNG with transparency, handle conversion
    if file_name.lower().endswith('.png'):
        with Image.open(file_path) as img:
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                temp_path = os.path.join(thumbnail_folder, f"temp_{file_name}.jpeg")
                converted_img = convert_rgba_to_rgb(img)
                converted_img.save(temp_path, "JPEG", quality=95)
                success_main = upload_file_to_s3(temp_path, main_url, file_type='image/jpeg')
                os.remove(temp_path)  # Clean up temp file
            else:
                success_main = upload_file_to_s3(file_path, main_url, file_type=file_type)
    else:
        success_main = upload_file_to_s3(file_path, main_url, file_type=file_type)
    
    success_thumb = upload_file_to_s3(thumbnail_path, thumbnail_url, file_type='image/jpeg')
    
    # Handle metadata JSON upload if URL is provided and metadata is enabled
    success_meta = True  # Default to True if no metadata URL or metadata disabled
    if meta_data_url and use_metadata:
        try:
            # Get base name for looking up matching JSON files
            base_name = os.path.splitext(file_name)[0]
            json_file_path = None
            
            # For video files, prioritize finding a JSON file with the same base name
            if is_video:
                # Check for a JSON file with the same base name (mandatory for videos)
                potential_json_path = os.path.join(folder_path, f"{base_name}.json")
                if os.path.exists(potential_json_path):
                    json_file_path = potential_json_path
                    print(f"[cyan]Found matching JSON metadata file for video: {os.path.basename(json_file_path)}[/cyan]")
                elif needs_metadata_generation:
                    # For videos, we create a new JSON file if one doesn't exist with the same name
                    print(f"[yellow]Creating a basic metadata JSON for video {file_name}[/yellow]")
                    meta_file_name = f"{base_name}.json"
                    meta_file_path = os.path.join(thumbnail_folder, meta_file_name)
                    
                    # Create simple metadata JSON for video
                    import json
                    metadata = {
                        "filename": file_name,
                        "upload_timestamp": time.time(),
                        "file_type": file_type,
                        "media_type": "VIDEO",
                        "path": str(folder_path)
                    }
                    
                    # Save metadata JSON file
                    with open(meta_file_path, 'w') as f:
                        json.dump(metadata, f, indent=4)
                    
                    json_file_path = meta_file_path
                    print(f"[cyan]Created metadata JSON file: {os.path.basename(json_file_path)}[/cyan]")
            else:
                # For non-video files, try matching name first, then fall back to any JSON
                potential_json_path = os.path.join(folder_path, f"{base_name}.json")
                if os.path.exists(potential_json_path):
                    json_file_path = potential_json_path
                    print(f"[cyan]Found matching JSON metadata file: {os.path.basename(json_file_path)}[/cyan]")
                
                # If not found for images, search for any JSON file in the folder as fallback
                if not json_file_path:
                    # Get all JSON files in the folder
                    json_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.json')]
                    if json_files:
                        json_file_path = os.path.join(folder_path, json_files[0])
                        print(f"[cyan]Using JSON metadata file: {os.path.basename(json_file_path)}[/cyan]")
            
            # Upload the JSON file (either found or created)
            if json_file_path:
                success_meta = upload_file_to_s3(json_file_path, meta_data_url, file_type='application/json')
                if success_meta:
                    print(f"[green]Successfully uploaded metadata file for {file_name}[/green]")
                else:
                    print(f"[yellow]Failed to upload metadata file for {file_name}[/yellow]")
                
                # Clean up temporary metadata file if we created one
                if json_file_path.startswith(thumbnail_folder):
                    try:
                        os.remove(json_file_path)
                    except Exception as e:
                        print(f"[yellow]Warning: Could not remove temporary metadata file: {str(e)}[/yellow]")
            else:
                # Create a new JSON file if none exists (for non-video files)
                print(f"[yellow]No JSON metadata file found, creating a basic one for {file_name}[/yellow]")
                meta_file_name = f"{base_name}_metadata.json"
                meta_file_path = os.path.join(thumbnail_folder, meta_file_name)
                
                # Create simple metadata JSON
                import json
                metadata = {
                    "filename": file_name,
                    "upload_timestamp": time.time(),
                    "file_type": file_type,
                    "media_type": "IMAGE",
                    "path": str(folder_path)
                }
                
                # Save metadata JSON file
                with open(meta_file_path, 'w') as f:
                    json.dump(metadata, f, indent=4)
                
                # Upload metadata JSON
                success_meta = upload_file_to_s3(meta_file_path, meta_data_url, file_type='application/json')
                
                # Clean up metadata file
                try:
                    os.remove(meta_file_path)
                except Exception as e:
                    print(f"[yellow]Warning: Could not remove temporary metadata file: {str(e)}[/yellow]")
        except Exception as e:
            print(f"[red]Error handling metadata for {file_name}: {str(e)}[/red]")
            success_meta = False
    
    return success_main and success_thumb and success_meta

def upload_file_to_s3(file_path, presigned_url, file_type='image/jpeg'):
    """Upload single file to S3 with improved error handling"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            with open(file_path, 'rb') as file_data:
                headers = {'Content-Type': file_type}
                if "blob.core.windows.net" in presigned_url:
                    headers['x-ms-blob-type'] = 'BlockBlob'
                response = requests.put(presigned_url, data=file_data, headers=headers)
                
                # Check for 503 error specifically
                if response.status_code == 503:
                    print(f"[yellow]Attempt {attempt + 1}/{max_attempts}: 503 Service Unavailable for {os.path.basename(file_path)}[/yellow]")
                    if attempt < max_attempts - 1:
                        # Wait longer for 503 errors (server is overloaded)
                        time.sleep(5)  # 5 second wait before retry
                        continue
                
                # For other errors
                response.raise_for_status()
                return True
                
        except requests.exceptions.RequestException as e:
            if "503" in str(e):
                print(f"[yellow]Attempt {attempt + 1}/{max_attempts}: 503 Service Unavailable for {os.path.basename(file_path)}[/yellow]")
            else:
                print(f"[red]Attempt {attempt + 1}/{max_attempts}: Failed to upload {os.path.basename(file_path)}: {str(e)}[/red]")
            
            if attempt < max_attempts - 1:
                time.sleep(3)  # Wait before retry
    
    # If we reach here, all attempts failed
    print(f"[red]Failed to upload {os.path.basename(file_path)} after {max_attempts} attempts[/red]")
    # Return False but don't fail the entire process
    return False

def confirm_upload(media_id, token, confirm_upload_endpoint):
    """Confirm single media upload"""
    url = confirm_upload_endpoint.format(media_id=media_id)
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return True

def confirm_batch_upload(batch_id, token, batch_confirm_endpoint):
    """Confirm entire batch upload"""
    try:
        url = batch_confirm_endpoint.format(batch_id=batch_id)
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        print(f"[green]Batch {batch_id} confirmed successfully![/green]")
        return True
    except Exception as e:
        print(f"[red]Failed to confirm batch {batch_id}: {str(e)}[/red]")
        return False

def handle_direct_upload(base_url, token, project_id=None, folder_path=None, media_type="AUTO", use_metadata=True):
    """Main CLI handler for direct uploads (now with batch support)"""
    try:
        # Get required inputs if not provided
        if project_id is None:
            project_id = Prompt.ask("Enter project ID")
        if folder_path is None:    
            folder_path = Prompt.ask("Enter folder path containing data")
        
        # Always use batch mode with default size of 5
        batch_size = 25
        
        # Validate folder path
        if not os.path.exists(folder_path):
            print(f"[red]Folder {folder_path} does not exist[/red]")
            return False
        
        # Get all image and video files
        sorted_files = get_files_sorted_by_folder(folder_path)
        if not sorted_files:
            print("[red]No supported files found in the specified folder[/red]")
            return False
        
        # Filter files based on media_type if not AUTO
        if media_type == "VIDEO":
            sorted_files = [f for f in sorted_files if is_video_file(str(f))]
            if not sorted_files:
                print("[red]No video files found in the specified folder[/red]")
                return False
        elif media_type == "IMAGE":
            sorted_files = [f for f in sorted_files if not is_video_file(f)]
            if not sorted_files:
                print("[red]No image files found in the specified folder[/red]")
                return False
        
        # Count video and image files
        video_files = [f for f in sorted_files if is_video_file(f)]
        image_files = [f for f in sorted_files if not is_video_file(f)]
        
        # Display initial info
        print(f"\n[cyan]Starting upload process:[/cyan]")
        print(f"[cyan]- Project ID: {project_id}[/cyan]")
        print(f"[cyan]- Folder: {folder_path}[/cyan]")
        print(f"[cyan]- Media type filter: {media_type}[/cyan]")
        print(f"[cyan]- Total files: {len(sorted_files)}[/cyan]")
        print(f"[cyan]- Video files: {len(video_files)}[/cyan]")
        print(f"[cyan]- Image files: {len(image_files)}[/cyan]")
        print(f"[cyan]- Metadata usage: {'Enabled' if use_metadata else 'Disabled'}[/cyan]")
        
        # If metadata is enabled, check for JSON files for videos
        if use_metadata and video_files:
            # Check for matching JSON files for each video
            videos_with_json = 0
            for video_file in video_files:
                base_name = os.path.splitext(os.path.basename(video_file))[0]
                potential_json_path = os.path.join(folder_path, f"{base_name}.json")
                if os.path.exists(potential_json_path):
                    videos_with_json += 1
            
            print(f"[cyan]- Videos with matching JSON: {videos_with_json}/{len(video_files)}[/cyan]")
            if videos_with_json < len(video_files):
                print(f"[yellow]Warning: {len(video_files) - videos_with_json} videos don't have matching JSON files[/yellow]")
                print(f"[yellow]Auto-generated metadata will be created for these videos[/yellow]")
        
        # Determine if we're using batches
        if batch_size and batch_size > 0:
            total_batches = math.ceil(len(sorted_files) / batch_size)
            print(f"[cyan]- Batch mode: Yes (size: {batch_size}, total batches: {total_batches})[/cyan]")
            print("[cyan]- Using sequential frame ordering for uploads[/cyan]")
            print("[cyan]- Will retry failed uploads up to 10 times[/cyan]")
            
            successful_batches = 0
            
            # Process files in batches
            for batch_index in range(total_batches):
                batch_num = batch_index + 1
                print(f"\n[yellow]Processing batch {batch_num} of {total_batches}[/yellow]")
                
                # Get current batch of files
                start_idx = batch_index * batch_size
                end_idx = min(start_idx + batch_size, len(sorted_files))
                current_batch = sorted_files[start_idx:end_idx]
                
                # Process this batch
                result = process_images_and_send_request(
                    base_url, 
                    token, 
                    project_id, 
                    folder_path,
                    files_batch=current_batch,
                    batch_index=batch_index,
                    total_batches=total_batches,
                    use_metadata=use_metadata,
                    media_type=media_type
                )
                
                if result:
                    batch_id, batch_confirm_endpoint = result
                    # Confirm batch upload
                    if confirm_batch_upload(batch_id, token, batch_confirm_endpoint):
                        print(f"[green]Batch {batch_num}/{total_batches} completed successfully![/green]")
                        successful_batches += 1
                    else:
                        print(f"[red]Batch {batch_num}/{total_batches} had confirmation errors[/red]")
                else:
                    print(f"[red]Batch {batch_num}/{total_batches} processing failed[/red]")
                
                # Add a small delay between batches
                if batch_index < total_batches - 1:
                    print(f"[yellow]Pausing before next batch...[/yellow]")
                    time.sleep(3)  # 3 second pause between batches
            
            # Final report
            print(f"\n[green]Upload process completed![/green]")
            print(f"[green]- Successfully processed {successful_batches} out of {total_batches} batches[/green]")
            
            if successful_batches == total_batches:
                print("[green]All batches uploaded successfully![/green]")
                return True
            else:
                print(f"[yellow]Some batches had issues ({total_batches - successful_batches} out of {total_batches})[/yellow]")
                print("[yellow]Note: Batches may show as successful even with some failed files[/yellow]")
                return True  # Still return True since most files likely uploaded
                
        else:
            # Original non-batched mode (for backwards compatibility)
            print(f"[cyan]- Batch mode: No (processing all files at once)[/cyan]")
            
            # Process all images at once
            result = process_images_and_send_request(base_url, token, project_id, folder_path, use_metadata=use_metadata,media_type=media_type)
            
            if result:
                batch_id, batch_confirm_endpoint = result
                # Confirm batch upload
                if confirm_batch_upload(batch_id, token, batch_confirm_endpoint):
                    print("[green]Upload process completed successfully![/green]")
                    return True
                else:
                    print("[red]Upload process completed with some errors[/red]")
                    return False
            else:
                print("[red]Upload process failed[/red]")
                return False
            
    except Exception as e:
        print(f"[red]Error during upload process: {str(e)}[/red]")
        cleanup_thumbnails(folder_path)
        return False
