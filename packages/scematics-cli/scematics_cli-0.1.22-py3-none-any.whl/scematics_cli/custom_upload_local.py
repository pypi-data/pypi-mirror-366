import os
import shutil
from PIL import Image
import requests
from requests.exceptions import RequestException
import time
from pathlib import Path
import json
import argparse
from tqdm import tqdm, trange
import cv2
import math
from tabulate import tabulate  # Added for summary table
import builtins
import datetime


# Supported video file types
VIDEO_EXTENSIONS = {
    '.mp4': 'application/octet-stream',
    '.mov': 'application/octet-stream',
    '.avi': 'application/octet-stream',
    '.mkv': 'application/octet-stream',
    '.hevc': 'application/octet-stream'
}

# Global summary data storage
upload_summary = []

def is_video_file(file_path):
    """Check if the file is a video based on extension"""
    if hasattr(file_path, 'suffix'):
        extension = file_path.suffix.lower()
    else:
        extension = os.path.splitext(file_path)[1].lower() if isinstance(file_path, str) else ""
        
    return extension in VIDEO_EXTENSIONS.keys()

def is_json_file(file_path):
    """Check if the file is a JSON file"""
    if hasattr(file_path, 'suffix'):
        extension = file_path.suffix.lower()
    else:
        extension = os.path.splitext(file_path)[1].lower() if isinstance(file_path, str) else ""
        
    return extension.lower() == '.json'

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
            print(f"Cleaned up thumbnail folder")
    except Exception as e:
        print(f"Warning: Could not clean up thumbnail folder: {str(e)}")

def get_subdirectories(folder_path):
    """Get all subdirectories in the given folder"""
    return [f.path for f in os.scandir(folder_path) if f.is_dir() and not f.name.startswith('_')]

def get_files_in_directory(directory, file_filter_func):
    """Get all files in directory that match the filter function"""
    return [os.path.join(directory, f) for f in os.listdir(directory) 
            if os.path.isfile(os.path.join(directory, f)) and file_filter_func(f)]

def generate_video_thumbnail(video_path, thumbnail_path):
    """Generate thumbnail from the first frame of a video"""
    try:
        # Open the video file
        video = cv2.VideoCapture(str(video_path))
        
        # Check if video opened successfully
        if not video.isOpened():
            print(f"Could not open video {video_path}")
            return False
        
        # Read the first frame
        success, frame = video.read()
        if not success:
            print(f"Could not read first frame from {video_path}")
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
        print(f"Error generating thumbnail for {video_path}: {str(e)}")
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
        print(f"Error getting video dimensions for {video_path}: {str(e)}")
        return 0, 0

def retry_request(func, retries=10, delay=2, *args, **kwargs):
    """Retry function execution - 10 retries"""
    pbar = kwargs.pop('pbar', None)
    description = kwargs.pop('description', None)
    
    for attempt in range(retries):
        try:
            if pbar and description:
                pbar.set_description(f"Attempt {attempt + 1}/{retries}: {description}")
            result = func(*args, **kwargs)
            if result:
                return result
            # If function returns False, also retry
            if pbar:
                pbar.set_description(f"Attempt {attempt + 1} returned False, retrying...")
            if attempt < retries - 1:
                time.sleep(delay)
        except Exception as e:
            if pbar:
                pbar.set_description(f"Attempt {attempt + 1} failed: {str(e)[:30]}...")
            if attempt < retries - 1:
                time.sleep(delay)
    
    # If we get here, all attempts failed
    if pbar:
        pbar.set_description(f"Failed after {retries} attempts")
    return None

def add_to_summary(filename, status, details=""):
    """Add file upload result to summary data"""
    global upload_summary
    upload_summary.append({
        "filename": filename,
        "status": status,
        "details": details
    })

def process_folder_videos(base_url, token, project_id, folder_path, json_files):
    """Process all videos in a folder with JSON metadata files"""
    # Create thumbnail folder in the parent directory
    parent_dir = os.path.dirname(folder_path)
    thumbnail_folder = os.path.join(parent_dir, "_thumbnail")
    os.makedirs(thumbnail_folder, exist_ok=True)
    
    # Set up API endpoints
    presigned_url_endpoint = f"{base_url}/uploads/generate-presigned-url/{{media_id}}"
    confirm_upload_endpoint = f"{base_url}/uploads/confirm-upload/{{media_id}}"
    batch_confirm_endpoint = f"{base_url}/uploads/batch-confirm/{{batch_id}}"
    
    # Get all video files in the folder
    video_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and is_video_file(f)]
    
    if not video_files:
        print(f"No video files found in {folder_path}")
        return False
    
    # Display found videos
    print(f"Found {len(video_files)} videos in {folder_path}:")
    for video in video_files[:5]:
        print(f"  - {video}")
    if len(video_files) > 5:
        print(f"  - ... and {len(video_files) - 5} more")
    
    # Get JSON files (passed from parent function)
    if not json_files:
        print(f"No JSON files found in {folder_path}")
        # We'll generate them later
    else:
        print(f"Found {len(json_files)} JSON files in {folder_path}:")
        for json_file in json_files[:3]:
            print(f"  - {os.path.basename(json_file)}")
        if len(json_files) > 3:
            print(f"  - ... and {len(json_files) - 3} more")
    
    # Create a map of JSON files by basename (without extension) for easy lookup
    json_map = {}
    for json_file in json_files:
        # Get the base name without extension
        json_basename = os.path.splitext(os.path.basename(json_file))[0]
        json_map[json_basename] = json_file
    
    folder_name = os.path.basename(folder_path)
    
    # Prepare data for API request
    file_data_list = []
    
    # Process each video file with tqdm progress bar
    scan_pbar = tqdm(video_files, desc=f"Processing folder: {folder_name}", unit="file")
    for video_file in scan_pbar:
        file_name = video_file
        video_path = os.path.join(folder_path, file_name)
        
        scan_pbar.set_description(f"Processing {file_name}")
        
        try:
            # Find matching JSON file for this video
            video_basename = os.path.splitext(file_name)[0]
            matching_json = None
            
            # Check if there are any JSON files in this folder
            if json_files:
                # If there's only one JSON file in the folder, use it for all videos
                if len(json_files) == 1:
                    matching_json = os.path.basename(json_files[0])
                    print(f"Using the only JSON file in folder for {file_name}: {matching_json}")
                else:
                    # Check for exact match first
                    if video_basename in json_map:
                        matching_json = os.path.basename(json_map[video_basename])
                    
                    # If no exact match, try more complex matching patterns
                    if not matching_json:
                        for json_basename, json_path in json_map.items():
                            # Check if JSON basename contains the video basename (or vice versa)
                            if video_basename in json_basename or json_basename in video_basename:
                                matching_json = os.path.basename(json_path)
                                break
                        
                        # If still no match, just use the first JSON file
                        if not matching_json:
                            matching_json = os.path.basename(json_files[0])
                            print(f"No name match found. Using first JSON file for {file_name}: {matching_json}")
            
            # Generate thumbnail
            thumbnail_path = os.path.join(thumbnail_folder, f"{os.path.splitext(file_name)[0]}_thumbnail.jpeg")
            success = generate_video_thumbnail(video_path, thumbnail_path)
            
            if not success:
                print(f"Warning: Could not generate thumbnail for {file_name}, using placeholder")
                # Create a blank thumbnail with text
                img = Image.new('RGB', (200, 200), color=(100, 100, 100))
                img.save(thumbnail_path, "JPEG", quality=85)
            
            # Get video dimensions
            width, height = get_video_dimensions(video_path)
            
            # Add file data
            file_data = {
                "file_name": file_name,
                "width": width,
                "height": height,
                "media_type": "VIDEO",
                "folder_path": folder_path
            }
            
            # Add metadata JSON if we found a match
            if matching_json:
                file_data["meta_data"] = matching_json
                print(f"Found matching JSON for {file_name}: {matching_json}")
            else:
                file_data["needs_metadata_generation"] = True
                print(f"No matching JSON found for {file_name}")
            
            file_data_list.append(file_data)
            
        except Exception as e:
            print(f"Failed to process {file_name}: {str(e)}")
            add_to_summary(file_name, "FAILED", f"Processing error: {str(e)[:100]}")
    
    # Skip further processing if no files were processed
    if not file_data_list:
        print(f"No files were successfully processed in {folder_path}")
        return False
    
    # Prepare headers
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # Video API endpoint
        video_api_endpoint = f"{base_url}/uploads/entry-datas?media_type=VIDEO"
        
        # Remove custom metadata flag before sending to server
        for item in file_data_list:
            if "needs_metadata_generation" in item:
                del item["needs_metadata_generation"]
            if "folder_path" in item:
                del item["folder_path"]
                
        payload = {
            "project_id": project_id,
            "items": file_data_list
        }
        
        # Use retry for the request
        max_retries = 5
        response_json = None
        
        api_pbar = tqdm(total=max_retries, desc=f"Sending VIDEO data to server for folder: {folder_name}", unit="attempt")
        for attempt in range(max_retries):
            api_pbar.update(1)
            try:
                api_pbar.set_description(f"Sending VIDEO data to server (attempt {attempt+1}/{max_retries})")
                response = requests.post(video_api_endpoint, json=payload, headers=headers)
                response.raise_for_status()
                response_json = response.json()
                api_pbar.set_description(f"Successfully sent data to server")
                break
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    api_pbar.set_description(f"API request failed: {str(e)[:30]}... Retrying")
                    time.sleep(3)
                else:
                    api_pbar.set_description(f"API request failed after {max_retries} attempts")
                    # Add all files to summary as failed
                    for item in file_data_list:
                        add_to_summary(item["file_name"], "FAILED", f"API request failed: {str(e)[:100]}")
                    raise
        api_pbar.close()
        
        if not response_json:
            print(f"Failed to get response from server for folder: {folder_name}")
            return False
        
        # Get batch ID
        batch_id = response_json.get('batch_id')
        if not batch_id:
            print(f"Batch ID not found in response for folder: {folder_name}")
            return False
        
        # Add original data back to items for upload phase
        for i, item in enumerate(response_json.get('items', [])):
            file_name = item['file_name']
            # Find original item data
            original_item = next((x for x in file_data_list if x['file_name'] == file_name), None)
            if original_item:
                # Add folder path back
                item['folder_path'] = folder_path
                # Add metadata json path if available
                if 'meta_data' in original_item:
                    item['meta_data'] = original_item['meta_data']
                    # Find the full path to the JSON file
                    json_name = original_item['meta_data']
                    json_path = None
                    for j in json_files:
                        if os.path.basename(j) == json_name:
                            json_path = j
                            break
                    if json_path:
                        item['json_file_path'] = json_path
        
        failed_files = []
        
        # Upload files with tqdm progress bar
        upload_pbar = tqdm(response_json.get('items', []), desc=f"Uploading files from {folder_name}", unit="file")
        
        # Process each item
        for item in upload_pbar:
            media_id = item['media_id']
            file_name = item['file_name']
            folder_path = item.get('folder_path', folder_path)
            
            upload_pbar.set_description(f"Uploading {file_name}")
            
            # Get JSON file path if available
            json_file_path = item.get('json_file_path', None)
            needs_metadata_generation = not json_file_path
            
            # Get presigned URLs and upload
            success = retry_request(
                request_presigned_urls,
                retries=10,
                delay=2,
                media_id=media_id,
                file_name=file_name,
                token=token,
                folder_path=folder_path,
                thumbnail_folder=thumbnail_folder,
                presigned_url_endpoint=presigned_url_endpoint,
                confirm_upload_endpoint=confirm_upload_endpoint,
                json_file_path=json_file_path,
                needs_metadata_generation=needs_metadata_generation,
                pbar=upload_pbar,
                description=f"Getting presigned URLs for {file_name}"
            )
            
            if success:
                upload_pbar.set_description(f"Confirming {file_name}")
                confirm_success = retry_request(
                    confirm_upload,
                    retries=10,
                    delay=2,
                    media_id=media_id,
                    token=token,
                    confirm_upload_endpoint=confirm_upload_endpoint,
                    pbar=upload_pbar,
                    description=f"Confirming upload for {file_name}"
                )
                if confirm_success:
                    # Add to summary with success status
                    add_to_summary(file_name, "SUCCESS", "Upload completed successfully")
                else:
                    failed_files.append(file_name)
                    add_to_summary(file_name, "FAILED", "Failed to confirm upload")
            else:
                failed_files.append(file_name)
                add_to_summary(file_name, "FAILED", "Failed to upload file")
        
        upload_pbar.close()
        
        # Log any failed files
        if failed_files:
            print(f"Warning: {len(failed_files)} files failed in folder {folder_name}")
            print(f"Failed files: {', '.join(failed_files[:5])}{'...' if len(failed_files) > 5 else ''}")
        
        # Confirm the batch
        if confirm_batch_upload(batch_id, token, batch_confirm_endpoint):
            print(f"Folder {folder_name} processed successfully!")
            return True
        else:
            print(f"Folder {folder_name} had confirmation errors")
            return False
        
    except Exception as e:
        print(f"Error during upload process for folder {folder_name}: {str(e)}")
        # Add all files to summary as failed if we have an exception
        for item in file_data_list:
            add_to_summary(item["file_name"], "FAILED", f"Error during upload: {str(e)[:100]}")
        return False
        
def request_presigned_urls(media_id, file_name, token, folder_path, thumbnail_folder, presigned_url_endpoint, 
                          confirm_upload_endpoint, json_file_path=None, needs_metadata_generation=False):
    """Request presigned URLs and upload files"""
    formatted_presigned_url = presigned_url_endpoint.format(media_id=media_id)
    
    # Determine correct file type based on extension
    extension = os.path.splitext(file_name)[1].lower()
    file_type = VIDEO_EXTENSIONS.get(extension, 'application/octet-stream')
    
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
    
    # Debug information
    print(f"Uploading main file: {file_path}")
    success_main = upload_file_to_s3(file_path, main_url, file_type=file_type)
    
    #print(f"Uploading thumbnail: {thumbnail_path}")
    success_thumb = upload_file_to_s3(thumbnail_path, thumbnail_url, file_type='image/jpeg')
    
    # Handle metadata JSON upload
    success_meta = True  # Default to True if no metadata URL
    
    if meta_data_url:
        try:
            # If a specific JSON file is provided, use that
            if json_file_path:
                print(f"Uploading JSON metadata file: {json_file_path}")
                success_meta = upload_file_to_s3(json_file_path, meta_data_url, file_type='application/json')
                if success_meta:
                    print(f"Successfully uploaded metadata file for {file_name}")
                else:
                    print(f"Failed to upload metadata file for {file_name}")
                    # Retry with generated metadata if the JSON upload failed
                    print(f"Attempting to generate and upload basic metadata instead")
                    success_meta = generate_and_upload_metadata(file_name, file_type, folder_path, thumbnail_folder, meta_data_url)
            
            # If we need to generate metadata (no JSON file provided)
            else:
                print(f"No JSON metadata file provided, creating a basic one for {file_name}")
                success_meta = generate_and_upload_metadata(file_name, file_type, folder_path, thumbnail_folder, meta_data_url)
        
        except Exception as e:
            print(f"Error handling metadata for {file_name}: {str(e)}")
            print(f"Attempting to generate and upload basic metadata instead")
            success_meta = generate_and_upload_metadata(file_name, file_type, folder_path, thumbnail_folder, meta_data_url)
    
    return success_main and success_thumb and success_meta

def generate_and_upload_metadata(file_name, file_type, folder_path, thumbnail_folder, meta_data_url):
    """Generate and upload basic metadata for a file"""
    try:
        # Create a new JSON file
        base_name = os.path.splitext(file_name)[0]
        meta_file_name = f"{base_name}_metadata.json"
        meta_file_path = os.path.join(thumbnail_folder, meta_file_name)
        
        # Create simple metadata JSON
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
        
        print(f"Generated metadata file: {meta_file_path}")
        
        # Upload metadata JSON
        success = upload_file_to_s3(meta_file_path, meta_data_url, file_type='application/json')
        
        # Clean up metadata file
        try:
            os.remove(meta_file_path)
        except Exception as e:
            print(f"Warning: Could not remove temporary metadata file: {str(e)}")
            
        return success
    except Exception as e:
        print(f"Error generating and uploading metadata: {str(e)}")
        return False

def upload_file_to_s3(file_path, presigned_url, file_type='image/jpeg'):
    
    """Upload single file to S3 or Azure Blob with intelligent header handling."""
    max_attempts = 5
    upload_pbar = tqdm(total=max_attempts, desc=f"Uploading {os.path.basename(file_path)}", leave=False, unit="attempt")

    for attempt in range(max_attempts):
        upload_pbar.update(1)
        try:
            if not os.path.exists(file_path):
                upload_pbar.set_description(f"File not found: {os.path.basename(file_path)}")
                upload_pbar.close()
                return False

            file_size = os.path.getsize(file_path)
            upload_pbar.set_description(f"Uploading {os.path.basename(file_path)} ({file_size} bytes)")

            with open(file_path, 'rb') as file_data:
                # Default headers
                headers = {'Content-Type': file_type}

                # 💡 Add 'x-ms-blob-type' only if URL looks like Azure
                if "blob.core.windows.net" in presigned_url:
                    headers['x-ms-blob-type'] = 'BlockBlob'

                response = requests.put(presigned_url, data=file_data, headers=headers)

                if response.status_code == 503:
                    upload_pbar.set_description(f"503 Service Unavailable - retry {attempt + 1}/{max_attempts}")
                    if attempt < max_attempts - 1:
                        time.sleep(5)
                        continue

                if response.status_code >= 400:
                    print(response.text)
                    upload_pbar.set_description(f"HTTP error {response.status_code} - retry {attempt + 1}/{max_attempts}")
                    if attempt < max_attempts - 1:
                        time.sleep(3)
                        continue

                response.raise_for_status()
                upload_pbar.set_description(f"Successfully uploaded {os.path.basename(file_path)}")
                upload_pbar.close()
                return True

        except requests.exceptions.RequestException as e:
            if "503" in str(e):
                upload_pbar.set_description(f"503 Service Unavailable - retry {attempt + 1}/{max_attempts}")
            else:
                upload_pbar.set_description(f"Failed: {str(e)[:30]}... - retry {attempt + 1}/{max_attempts}")

            if attempt < max_attempts - 1:
                time.sleep(3)

    upload_pbar.set_description(f"Failed after {max_attempts} attempts")
    upload_pbar.close()
    return False

def confirm_upload(media_id, token, confirm_upload_endpoint):
    """Confirm single media upload"""
    url = confirm_upload_endpoint.format(media_id=media_id)
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    time.sleep(30)
    return True

def confirm_batch_upload(batch_id, token, batch_confirm_endpoint):
    """Confirm entire batch upload"""
    try:
        url = batch_confirm_endpoint.format(batch_id=batch_id)
        headers = {'Authorization': f'Bearer {token}'}
        
        confirm_pbar = tqdm(total=1, desc=f"Confirming batch {batch_id}", unit="request")
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        confirm_pbar.set_description(f"Batch {batch_id} confirmed successfully!")
        confirm_pbar.close()
        return True
    except Exception as e:
        print(f"Failed to confirm batch {batch_id}: {str(e)}")
        return False

def find_leaf_folders(root_path):
    """Find all leaf folders (folders without subdirectories) in the directory tree"""
    leaf_folders = []
    
    print(f"Scanning directory structure for video folders...")
    
    for root, dirs, files in tqdm(os.walk(root_path), desc="Scanning directories", unit="dir"):
        # Skip hidden folders
        dirs[:] = [d for d in dirs if not d.startswith('_')]
        
        # If this folder has no subdirectories, it's a leaf
        if not dirs:
            # Check if it has video files
            has_videos = any(is_video_file(f) for f in files)
            if has_videos:
                leaf_folders.append(root)
    
    return leaf_folders

def is_video_directory(directory):
    """Check if the directory contains video files"""
    if not os.path.isdir(directory):
        return False
        
    return any(is_video_file(f) for f in os.listdir(directory) 
               if os.path.isfile(os.path.join(directory, f)))

def cleanup_all_thumbnails(root_path):
    """Find and clean up all _thumbnail folders under the given path"""
    thumbnail_folders = []
    
    # First, find all _thumbnail folders
    #print("Searching for thumbnail folders to clean up...")
    for root, dirs, files in os.walk(root_path):
        if os.path.basename(root) == "_thumbnail":
            thumbnail_folders.append(root)
    
    # Then remove them
    if thumbnail_folders:
        for folder in tqdm(thumbnail_folders, desc="Cleaning thumbnail folders", unit="folder"):
            try:
                shutil.rmtree(folder)
            except Exception as e:
                print(f"Error cleaning up thumbnail folder {folder}: {str(e)}")
        
        #print(f"Cleaned up {len(thumbnail_folders)} thumbnail folders")
    else:
        pass
        #print(f"No thumbnail folders found to clean up")

def print_upload_summary():
    """Print a summary table of all upload results"""
    global upload_summary
    
    if not upload_summary:
        print("No upload data available for summary")
        return
    
    print("\n\n" + "="*80)
    print(" "*30 + "UPLOAD SUMMARY REPORT")
    print("="*80)
    
    # Count successes and failures
    success_count = sum(1 for item in upload_summary if item["status"] == "SUCCESS")
    failure_count = sum(1 for item in upload_summary if item["status"] == "FAILED")
    
    print(f"Total files processed: {len(upload_summary)}")
    print(f"Successfully uploaded: {success_count}")
    print(f"Failed uploads: {failure_count}")
    print("-"*80)
    
    # Format table data
    table_data = []
    for item in upload_summary:
        status_display = "✓" if item["status"] == "SUCCESS" else "✗"
        table_data.append([
            item["filename"],
            status_display,
            item["status"],
            item["details"][:50] + ("..." if len(item["details"]) > 50 else "")
        ])
    
    # Print the table
    headers = ["Filename", "", "Status", "Details"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print("="*80)

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description='Video Upload Script for Nested Directory Structures')
    
    # Required arguments
    parser.add_argument('--project_id', type=str, help='Project ID to upload videos to')
    parser.add_argument('--folder', type=str, help='Path to the folder containing videos or subfolders with videos')
    
    # Optional arguments
    parser.add_argument('--base_url', type=str, default='https://api.example.com/v1', help='Base API URL')
    parser.add_argument('--token', type=str, help='API Authentication token')
    
    args = parser.parse_args()
    
    # Instead of using Rich prompts, use input() for simplicity
    if not args.project_id:
        args.project_id = input("Enter project ID: ")
    
    if not args.folder:
        args.folder = input("Enter folder path: ")
    
    if not args.token:
        import getpass
        args.token = getpass.getpass("Enter API token: ")
    
    # Display configuration
    print(f"\nConfiguration:")
    print(f"- Project ID: {args.project_id}")
    print(f"- Folder: {args.folder}")
    print(f"- Base URL: {args.base_url}")
    
    # Run the upload process
    result = process_directory_structure(args.base_url, args.token, args.project_id, args.folder)
    
    if result:
        print("Upload process completed successfully!")
        return 0
    else:
        print("Upload process encountered errors.")
        return 1

def process_directory_structure(base_url, token, project_id, input_path):
    """Process directory structure starting from the input path"""

    # Set up log file
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    log_filename = f"{timestamp}_uploads_log.txt"
    os.makedirs('logs', exist_ok=True)
    log_filepath = os.path.join('logs', log_filename)

    # Custom print that also writes to log file
    original_print = builtins.print

    def tee_print(*args, **kwargs):
        original_print(*args, **kwargs)
        with open(log_filepath, "a", encoding="utf-8") as f:
            f.write(" ".join(map(str, args)) + "\n")

    builtins.print = tee_print

    print("Starting upload process:")
    print(f"- Project ID: {project_id}")
    print(f"- Folder: {input_path}")

    if not os.path.exists(input_path):
        print(f"Path {input_path} does not exist")
        return False

    if os.path.isfile(input_path):
        print(f"Input is a file, using its parent directory instead")
        input_path = os.path.dirname(input_path)

    if is_video_directory(input_path):
        print(f"Found videos in {input_path}. Processing this directory only.")
        json_files = [os.path.join(input_path, f) for f in os.listdir(input_path)
                      if os.path.isfile(os.path.join(input_path, f)) and is_json_file(f)]
        result = process_folder_videos(base_url, token, project_id, input_path, json_files)
        cleanup_all_thumbnails(input_path)
        return result

    print(f"Scanning {input_path} for directories containing videos...")
    print("Scanning directory structure for video folders...")
    leaf_folders = find_leaf_folders(input_path)

    if not leaf_folders:
        print(f"No directories with videos found under {input_path}")
        return False

    print(f"Found {len(leaf_folders)} directories with videos:")
    for folder in leaf_folders[:5]:
        print(f"  - {folder}")
    if len(leaf_folders) > 5:
        print(f"  - ... and {len(leaf_folders) - 5} more")

    successful_folders = []
    failed_folders = []

    folder_pbar = tqdm(enumerate(leaf_folders), total=len(leaf_folders),
                       desc="Processing folders", unit="folder")

    for folder_index, folder in folder_pbar:
        folder_name = os.path.basename(folder)
        folder_pbar.set_description(f"Processing: {folder_name}")

        json_files = [os.path.join(folder, f) for f in os.listdir(folder)
                      if os.path.isfile(os.path.join(folder, f)) and is_json_file(f)]

        try:
            result = process_folder_videos(base_url, token, project_id, folder, json_files)
        except Exception as e:
            print(f"Exception in processing folder {folder_name}: {e}")
            result = False

        if result:
            print(f"Folder {folder_name} processed successfully.")
            successful_folders.append(folder_name)
        else:
            print(f"Folder {folder_name} failed to process.")
            failed_folders.append(folder_name)

        if folder_index < len(leaf_folders) - 1:
            time.sleep(3)

    folder_pbar.close()
    cleanup_all_thumbnails(input_path)

    print("\n=== Final Summary ===")
    print(f"Total folders processed: {len(leaf_folders)}")
    print(f"Successful folders ({len(successful_folders)}):")
    for name in successful_folders:
        print(f"  - {name}")
    print(f"Failed folders ({len(failed_folders)}):")
    for name in failed_folders:
        print(f"  - {name}")

    builtins.print = original_print  # Restore original print
    return True