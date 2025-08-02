import os
import shutil
import re
import math
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
    TimeRemainingColumn,
    MofNCompleteColumn
)
from rich.console import Console
from rich.prompt import Prompt
from rich import print

console = Console()

# Batch size configuration
BATCH_SIZE = 10

def get_mime_type(file_name):
    """Determine the correct MIME type based on file extension"""
    extension = os.path.splitext(file_name)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif'
    }
    return mime_types.get(extension, 'image/jpeg')  # Default to jpeg if unknown

def make_request_with_retry(method, url, max_retries=5, initial_delay=1, max_delay=8, **kwargs):
    """
    Make HTTP request with exponential backoff retry logic
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries):
        try:
            response = getattr(requests, method.lower())(url, **kwargs)
            
            # If response status is 503, treat it as a retriable error
            if response.status_code == 503:
                raise requests.exceptions.RequestException(f"Service Unavailable (503) on attempt {attempt + 1}")
                
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            last_exception = e
            
            if attempt == max_retries - 1:  # Last attempt
                raise
                
            # Calculate delay with exponential backoff
            sleep_time = min(delay * (2 ** attempt), max_delay)
            
            # Log retry attempt
            print(f"[yellow]Request failed: {str(e)}. Retrying in {sleep_time} seconds... (Attempt {attempt + 1}/{max_retries})[/yellow]")
            
            time.sleep(sleep_time)
    
    raise last_exception if last_exception else Exception("Max retries exceeded")

def natural_sort_key(s):
    """
    Sort strings with numbers in natural order.
    Example: ['img1.jpg', 'img2.jpg', 'img10.jpg'] instead of ['img1.jpg', 'img10.jpg', 'img2.jpg']
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', str(s))]

def convert_rgba_to_rgb(image):
    """
    Convert RGBA image to RGB with white background.
    Handles palette images with transparency properly.
    """
    # Handle palette images with transparency
    if image.mode == 'P':
        try:
            # Convert palette image to RGBA first
            image = image.convert('RGBA')
        except Exception as e:
            print(f"[yellow]Warning: Failed to convert palette image: {str(e)}[/yellow]")
            # If conversion fails, try direct RGB conversion
            return image.convert('RGB')

    # Handle RGBA images
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        try:
            background.paste(image, mask=image.split()[3])
        except Exception as e:
            print(f"[yellow]Warning: Failed to paste RGBA image: {str(e)}[/yellow]")
            # If paste fails, do direct conversion
            return image.convert('RGB')
        return background
    
    # Handle LA (grayscale with alpha) images
    elif image.mode == 'LA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        try:
            background.paste(image, mask=image.split()[1])
        except Exception as e:
            print(f"[yellow]Warning: Failed to paste LA image: {str(e)}[/yellow]")
            return image.convert('RGB')
        return background
    
    # For all other modes, convert directly to RGB
    return image.convert('RGB')

def cleanup_thumbnails(folder_path):
    """Clean up thumbnail folder"""
    thumbnail_folder = os.path.join(folder_path, "_thumbnail")
    try:
        if os.path.exists(thumbnail_folder):
            shutil.rmtree(thumbnail_folder)
            print(f"[green]Cleaned up thumbnails for {os.path.basename(folder_path)}[/green]")
    except Exception as e:
        print(f"[yellow]Warning: Could not clean up thumbnails: {str(e)}[/yellow]")

def process_batch(batch_files, folder_path, thumbnail_folder, batch_index, total_batches, progress, process_task):
    """Process a batch of images and prepare them for upload"""
    image_data_list = []
    thumbnail_paths = {}
    original_paths = {}
    
    for file_path in batch_files:
        folder_name = file_path.parent.name
        file_name = file_path.name
        tagged_name = f"{folder_name}_{file_name}"
        
        progress.update(process_task, 
                     description=f"[magenta]Processing Batch {batch_index+1}/{total_batches}",
                     filename=tagged_name)

        try:
            with Image.open(file_path) as img:
                width, height = img.size
                # Make a copy of the image before processing
                img_copy = img.copy()
                thumb_img = img_copy.copy()
                thumb_img.thumbnail((200, 200))
                
                # Convert RGBA to RGB for thumbnail
                thumb_img = convert_rgba_to_rgb(thumb_img)
                
                thumb_path = os.path.join(
                    thumbnail_folder, 
                    f"{os.path.splitext(tagged_name)[0]}_thumbnail.jpg"
                )
                thumb_img.save(thumb_path, "JPEG", quality=85)
                
                image_data_list.append({
                    "file_name": tagged_name,
                    "width": width,
                    "height": height
                })
                
                thumbnail_paths[tagged_name] = thumb_path
                original_paths[tagged_name] = str(file_path)
        except Exception as e:
            progress.log(f"[red]Failed to process {tagged_name}: {str(e)}[/red]")
        finally:
            # Ensure we clean up any image objects
            if 'img_copy' in locals():
                img_copy.close()
            if 'thumb_img' in locals():
                thumb_img.close()
        
        progress.advance(process_task)
    
    return image_data_list, thumbnail_paths, original_paths

def upload_batch(image_data_list, thumbnail_paths, original_paths, base_url, token, project_id, 
                batch_index, total_batches, progress):
    """Upload a batch of processed images"""
    if not image_data_list:
        progress.log(f"[red]No images to upload in batch {batch_index+1}[/red]")
        return False
    
    # Setup endpoints
    api_endpoint = f"{base_url}/uploads/entry-datas?folder_as_tags=true"
    presigned_url_endpoint = f"{base_url}/uploads/generate-presigned-url/{{media_id}}"
    confirm_upload_endpoint = f"{base_url}/uploads/confirm-upload/{{media_id}}"
    batch_confirm_endpoint = f"{base_url}/uploads/batch-confirm/{{batch_id}}"
    
    # Upload process
    payload = {
        "project_id": project_id,
        "items": image_data_list
    }

    headers = {'Authorization': f'Bearer {token}'}
    
    progress.log(f"[cyan]Uploading batch {batch_index+1}/{total_batches} ({len(image_data_list)} images)...[/cyan]")
    
    try:
        response = make_request_with_retry('post', api_endpoint, json=payload, headers=headers)
        response_data = response.json()
        
        batch_id = response_data.get('batch_id')
        if not batch_id:
            raise Exception(f"No batch ID received for batch {batch_index+1}")

        # Upload files
        upload_task = progress.add_task(
            f"[yellow]Uploading Batch {batch_index+1}/{total_batches}",
            total=len(response_data['items']) * 2,
            filename=""
        )

        for item in response_data['items']:
            media_id = item['media_id']
            tagged_filename = item['file_name']
            
            progress.update(upload_task, 
                         description=f"[yellow]Uploading Batch {batch_index+1}/{total_batches}",
                         filename=tagged_filename)
            
            original_path = original_paths.get(tagged_filename)
            if not original_path or not os.path.exists(original_path):
                progress.log(f"[red]Could not find original file: {original_path}[/red]")
                continue

            # Get presigned URLs with correct MIME type
            formatted_url = presigned_url_endpoint.format(media_id=media_id)
            # Extract the original filename part after the folder prefix
            _, file_name = tagged_filename.split('_', 1)
            file_mime_type = get_mime_type(file_name)
            
            payload = {
                "file_key": tagged_filename,
                "file_type": file_mime_type
            }
            
            response = make_request_with_retry('post', formatted_url, json=payload, headers=headers)
            urls = response.json()

            # Handle file upload based on type
            if original_path.lower().endswith('.png') and 'png' in file_mime_type:
                with Image.open(original_path) as img:
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        # Convert PNG with transparency to RGB
                        converted_img = convert_rgba_to_rgb(img)
                        # Save temporarily
                        temp_folder = os.path.dirname(thumbnail_paths.get(tagged_filename, ''))
                        temp_path = os.path.join(temp_folder, f"temp_{tagged_filename}.jpg")
                        converted_img.save(temp_path, "JPEG", quality=95)
                        
                        # Prepare headers for file upload
                        headers = {'Content-Type': file_mime_type}
                        if "blob.core.windows.net" in urls['upload_url']:
                            headers['x-ms-blob-type'] = 'BlockBlob'

                        # Upload converted file
                        with open(temp_path, 'rb') as f:
                            make_request_with_retry('put', urls['upload_url'], data=f,
                                                headers=headers)
                        
                        # Clean up temp file
                        os.remove(temp_path)
                    else:
                        # Prepare headers for file upload
                        headers = {'Content-Type': file_mime_type}
                        if "blob.core.windows.net" in urls['upload_url']:
                            headers['x-ms-blob-type'] = 'BlockBlob'

                        # Upload as PNG if no transparency
                        with open(original_path, 'rb') as f:
                            make_request_with_retry('put', urls['upload_url'], data=f,
                                                headers=headers)
            else:
                # Prepare headers for file upload
                headers = {'Content-Type': file_mime_type}
                if "blob.core.windows.net" in urls['upload_url']:
                    headers['x-ms-blob-type'] = 'BlockBlob'

                # Upload with correct MIME type
                with open(original_path, 'rb') as f:
                    make_request_with_retry('put', urls['upload_url'], data=f,
                                        headers=headers)

            # Prepare headers for file upload
            headers = {'Content-Type': file_mime_type}
            if "blob.core.windows.net" in urls['upload_url']:
                headers['x-ms-blob-type'] = 'BlockBlob'
            # Upload thumbnail (always JPEG)
            thumb_path = thumbnail_paths.get(tagged_filename)
            if thumb_path and os.path.exists(thumb_path):
                with open(thumb_path, 'rb') as f:
                    make_request_with_retry('put', urls['thumbnail_url'], data=f,
                                        headers=headers)
            else:
                progress.log(f"[yellow]Warning: Missing thumbnail for {tagged_filename}[/yellow]")

            # Confirm upload
            url = confirm_upload_endpoint.format(media_id=media_id)
            make_request_with_retry('post', url, headers=headers)
            
            progress.advance(upload_task, 2)

        # Confirm batch
        url = batch_confirm_endpoint.format(batch_id=batch_id)
        make_request_with_retry('post', url, headers=headers)
        
        progress.log(f"[green]Successfully completed batch {batch_index+1}/{total_batches}[/green]")
        return True
        
    except Exception as e:
        progress.log(f"[red]Error uploading batch {batch_index+1}: {str(e)}[/red]")
        return False

def handle_tag_based_upload(base_url, token, project_id, folder_path):
    """Main handler for tag-based upload with batch processing"""
    try:
        if not os.path.exists(folder_path):
            print(f"[red]Folder {folder_path} does not exist[/red]")
            return False

        # Create thumbnail folder
        thumbnail_folder = os.path.join(folder_path, "_thumbnail")
        os.makedirs(thumbnail_folder, exist_ok=True)

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TextColumn("•"),
                TextColumn("[cyan]{task.fields[filename]:<30}"),
                TimeRemainingColumn(),
            ) as progress:
                progress.log("[cyan]Scanning folders for images...[/cyan]")
                
                # Get all subfolders and sort them naturally
                subfolders = sorted([f.path for f in os.scandir(folder_path) 
                                  if f.is_dir() and not f.name.startswith('_')],
                                  key=natural_sort_key)
                
                if not subfolders:
                    print("[yellow]No subfolders found[/yellow]")
                    return False

                # Get all image files with their folder names as tags
                total_files = 0
                all_files = []
                folder_counts = {}

                for subfolder in subfolders:
                    # Use natural sorting for files
                    files = sorted([f for f in Path(subfolder).glob('*.*')
                                  if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']],
                                  key=lambda x: natural_sort_key(x.name))
                    folder_name = os.path.basename(subfolder)
                    folder_counts[folder_name] = len(files)
                    total_files += len(files)
                    all_files.extend(files)

                if not total_files:
                    print("[yellow]No image files found in subfolders[/yellow]")
                    return False

                progress.log(f"[cyan]Found {total_files} images in {len(subfolders)} folders[/cyan]")
                # Sort folder counts by natural sort
                for folder, count in sorted(folder_counts.items(), key=lambda x: natural_sort_key(x[0])):
                    progress.log(f"[cyan]- {folder}: {count} images[/cyan]")

                # Calculate total batches
                total_batches = math.ceil(total_files / BATCH_SIZE)
                progress.log(f"[cyan]Will process in {total_batches} batches (max {BATCH_SIZE} images per batch)[/cyan]")

                # Setup overall progress tracking
                process_task = progress.add_task(
                    "[magenta]Processing Images",
                    total=total_files,
                    filename=""
                )

                # Process in batches
                successful_batches = 0
                for batch_index in range(total_batches):
                    start_idx = batch_index * BATCH_SIZE
                    end_idx = min(start_idx + BATCH_SIZE, len(all_files))
                    batch_files = all_files[start_idx:end_idx]
                    
                    progress.log(f"[cyan]Processing batch {batch_index+1}/{total_batches} ({len(batch_files)} images)[/cyan]")
                    
                    # Process this batch
                    image_data_list, thumbnail_paths, original_paths = process_batch(
                        batch_files, folder_path, thumbnail_folder, 
                        batch_index, total_batches, progress, process_task
                    )
                    
                    # Upload this batch
                    if upload_batch(
                        image_data_list, thumbnail_paths, original_paths,
                        base_url, token, project_id, batch_index, total_batches, progress
                    ):
                        successful_batches += 1
                    
                    # Small delay between batches to avoid overwhelming the server
                    if batch_index < total_batches - 1:
                        progress.log("[yellow]Pausing before next batch...[/yellow]")
                        time.sleep(2)  # 2 second pause between batches
                
                # Print summary
                progress.log("\n[cyan]Upload Summary:[/cyan]")
                progress.log(f"[green]Successfully processed {len(subfolders)} folders[/green]")
                progress.log(f"[green]Completed {successful_batches}/{total_batches} batches[/green]")
                for folder, count in sorted(folder_counts.items(), key=lambda x: natural_sort_key(x[0])):
                    progress.log(f"[green]- {folder}: {count} images[/green]")
                
                return successful_batches > 0

        finally:
            cleanup_thumbnails(folder_path)

    except Exception as e:
        print(f"[red]Error during tag-based upload: {str(e)}[/red]")
        return False
