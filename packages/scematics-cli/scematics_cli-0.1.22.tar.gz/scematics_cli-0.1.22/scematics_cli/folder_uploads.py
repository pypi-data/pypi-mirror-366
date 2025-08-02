import os
import shutil
from PIL import Image
import requests
from requests.exceptions import RequestException
import time
from pathlib import Path
import re
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console
from rich.prompt import Prompt
from rich import print
import math

console = Console()

# Batch size configuration - number of images per batch
BATCH_SIZE = 5

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

def make_request_with_retry(method, url, max_retries=3, initial_delay=1, max_delay=8, **kwargs):
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

def convert_rgba_to_rgb(image):
    """Convert RGBA image to RGB with white background"""
    # First convert palette images with transparency to RGBA
    if image.mode == 'P' and 'transparency' in image.info:
        image = image.convert('RGBA')
    
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        return background
    elif image.mode == 'LA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[1])
        return background
    
    return image.convert('RGB')

def natural_sort_key(s):
    """Convert string with numbers into tuple for proper numerical sorting
    
    This ensures folders and files with numeric patterns like:
    folder1, folder2, folder10, folder11 
    are sorted as: folder1, folder2, folder10, folder11 (not lexicographically)
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def cleanup_thumbnails(folder_path):
    """Clean up thumbnail folder"""
    thumbnail_folder = os.path.join(folder_path, "_thumbnail")
    try:
        if os.path.exists(thumbnail_folder):
            shutil.rmtree(thumbnail_folder)
            print(f"[green]Cleaned up thumbnails for {os.path.basename(folder_path)}[/green]")
    except Exception as e:
        print(f"[yellow]Warning: Could not clean up thumbnails for {os.path.basename(folder_path)}: {str(e)}[/yellow]")

def handle_folder_upload(base_url, token, base_dir):
    """Main handler for folder upload with numerical sorting and batch processing"""
    try:
        # Set up API endpoints
        project_create_endpoint = f"{base_url}/project/create"
        api_endpoint = f"{base_url}/uploads/entry-datas"
        presigned_url_endpoint = f"{base_url}/uploads/generate-presigned-url/{{media_id}}"
        confirm_upload_endpoint = f"{base_url}/uploads/confirm-upload/{{media_id}}"
        batch_confirm_endpoint = f"{base_url}/uploads/batch-confirm/{{batch_id}}"

        # Find and sort folders numerically (order is important)
        folders = sorted([f for f in os.listdir(base_dir) 
                        if os.path.isdir(os.path.join(base_dir, f))],
                        key=natural_sort_key)
        
        print(f"[cyan]Folders will be processed in this order: {', '.join(folders)}[/cyan]")

        if not folders:
            print("[yellow]No folders found[/yellow]")
            return False

        # Calculate total files to process
        total_files = 0
        folder_file_counts = {}
        print("[cyan]Scanning folders...[/cyan]")
        
        for folder_name in folders:
            folder_path = os.path.join(base_dir, folder_name)
            files = sorted([f for f in os.listdir(folder_path)
                          if os.path.isfile(os.path.join(folder_path, f)) and
                          f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))],
                          key=natural_sort_key)
            folder_file_counts[folder_name] = len(files)
            total_files += len(files)

        print(f"\n[cyan]Found {len(folders)} folders with {total_files} total images[/cyan]")
        
        # Process each folder
        processed_count = 0
        failed_count = 0
        processed_folders = []
        failed_folders = []
        total_processed_files = 0
        folder_batch_stats = {}  # To track batch stats per folder

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("•"),
            TextColumn("[cyan]{task.fields[filename]}"),
        ) as progress:
            overall_task = progress.add_task(
                "[cyan]Overall Progress", 
                total=total_files,
                filename=""
            )

            # Process each folder
            for folder_name in folders:
                folder_path = os.path.join(base_dir, folder_name)
                folder_files = folder_file_counts[folder_name]
                
                progress.log(f"\n[cyan]Processing folder: {folder_name} ({folder_files} files)[/cyan]")
                
                try:
                    # Create project
                    headers = {
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    }
                    payload = {
                        "project_name": folder_name,
                        "description": folder_name
                    }
                    
                    response = make_request_with_retry('post', project_create_endpoint, json=payload, headers=headers)
                    project_id = response.json().get('id')

                    if not project_id:
                        progress.log(f"[red]Failed to create project for {folder_name}[/red]")
                        failed_folders.append(folder_name)
                        failed_count += 1
                        continue

                    progress.log(f"[green]Created project {folder_name} with ID: {project_id}[/green]")

                    # Create thumbnail folder
                    thumbnail_folder = os.path.join(folder_path, "_thumbnail")
                    os.makedirs(thumbnail_folder, exist_ok=True)

                    try:
                        # Get numerically sorted image files (order is critical)
                        image_files = sorted([f for f in os.listdir(folder_path)
                                           if os.path.isfile(os.path.join(folder_path, f)) and
                                           f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))],
                                           key=natural_sort_key)
                        
                        # Print first few images to confirm order
                        sample_files = image_files[:min(5, len(image_files))]
                        progress.log(f"[cyan]Images will be processed in order. First few: {', '.join(sample_files)}...[/cyan]")

                        if not image_files:
                            progress.log(f"[yellow]No images found in {folder_name}[/yellow]")
                            cleanup_thumbnails(folder_path)
                            failed_folders.append(folder_name)
                            failed_count += 1
                            continue

                        # Process images in batches
                        total_batches = math.ceil(len(image_files) / BATCH_SIZE)
                        folder_batch_stats[folder_name] = {
                            "total_images": len(image_files),
                            "total_batches": total_batches,
                            "successful_batches": 0
                        }
                        
                        progress.log(f"[cyan]Folder will be processed in {total_batches} batches (max {BATCH_SIZE} images per batch)[/cyan]")
                        
                        folder_task = progress.add_task(
                            f"[cyan]Processing {folder_name}", 
                            total=len(image_files),
                            filename=""
                        )

                        # Process in batches
                        for batch_index in range(total_batches):
                            start_idx = batch_index * BATCH_SIZE
                            end_idx = min(start_idx + BATCH_SIZE, len(image_files))
                            batch_files = image_files[start_idx:end_idx]
                            
                            progress.log(f"[cyan]Processing batch {batch_index + 1}/{total_batches} for {folder_name} ({len(batch_files)} images)[/cyan]")
                            
                            # Process images in this batch (maintaining exact order)
                            # It's crucial we process them in the correct order
                            progress.log(f"[cyan]Processing batch {batch_index + 1} files in order: {', '.join(batch_files[:min(3, len(batch_files))])}...[/cyan]")
                            image_data_list = []
                            thumbnail_paths = {}  # To store thumbnail paths for each file
                            
                            for file_name in batch_files:
                                progress.update(folder_task, 
                                            description=f"[cyan]Processing {folder_name} (Batch {batch_index + 1}/{total_batches})",
                                            filename=file_name)
                                
                                file_path = os.path.join(folder_path, file_name)
                                try:
                                    with Image.open(file_path) as img:
                                        width, height = img.size
                                        # Convert to RGB before creating thumbnail
                                        rgb_img = convert_rgba_to_rgb(img)
                                        rgb_img.thumbnail((200, 200))
                                        thumb_path = os.path.join(thumbnail_folder, 
                                                                f"{os.path.splitext(file_name)[0]}_thumbnail.jpg")
                                        rgb_img.save(thumb_path, "JPEG", quality=85)
                                        
                                        image_data_list.append({
                                            "file_name": file_name,
                                            "width": width,
                                            "height": height
                                        })
                                        thumbnail_paths[file_name] = thumb_path
                                except Exception as e:
                                    progress.log(f"[red]Failed to process {file_name}: {str(e)}[/red]")
                                
                                progress.advance(folder_task)
                                progress.advance(overall_task)
                                total_processed_files += 1
                                progress.update(overall_task, 
                                            description=f"[cyan]Overall Progress ({total_processed_files}/{total_files})",
                                            filename=f"{folder_name}/{file_name}")

                            # Send batch request
                            if not image_data_list:
                                progress.log(f"[red]No valid images processed in batch {batch_index + 1} for {folder_name}[/red]")
                                continue

                            try:
                                payload = {
                                    "project_id": project_id,
                                    "items": image_data_list
                                }

                                progress.log(f"[cyan]Uploading {len(image_data_list)} images for {folder_name} (Batch {batch_index + 1})...[/cyan]")
                                response = make_request_with_retry('post', api_endpoint, json=payload, headers=headers)
                                response_data = response.json()
                                
                                if 'batch_id' not in response_data:
                                    raise Exception("No batch ID received")
                                    
                                batch_id = response_data['batch_id']
                                
                                # Upload files
                                upload_task = progress.add_task(
                                    f"[cyan]Uploading {folder_name} (Batch {batch_index + 1})", 
                                    total=len(response_data['items']) * 2,
                                    filename=""
                                )
                                
                                for item in response_data['items']:
                                    media_id = item['media_id']
                                    file_name = item['file_name']
                                    
                                    progress.update(upload_task, 
                                                description=f"[cyan]Uploading {folder_name} (Batch {batch_index + 1})",
                                                filename=file_name)
                                    
                                    # Get presigned URLs - use correct MIME type based on file extension
                                    formatted_url = presigned_url_endpoint.format(media_id=media_id)
                                    file_mime_type = get_mime_type(file_name)
                                    payload = {
                                        "file_key": file_name,
                                        "file_type": file_mime_type
                                    }
                                    
                                    response = make_request_with_retry('post', formatted_url, json=payload, headers=headers)
                                    urls = response.json()
                                    
                                    # Upload files
                                    file_path = os.path.join(folder_path, file_name)
                                    thumb_path = thumbnail_paths.get(file_name)
                                    
                                    # Prepare headers for file upload
                                    headers = {'Content-Type': file_mime_type}
                                    if "blob.core.windows.net" in urls['upload_url']:
                                        headers['x-ms-blob-type'] = 'BlockBlob'

                                    # Upload the main file
                                    with open(file_path, 'rb') as f:
                                        make_request_with_retry('put', urls['upload_url'], data=f, headers=headers)

                                    # Upload the thumbnail (always a JPEG)
                                    if thumb_path and os.path.exists(thumb_path):
                                        thumb_headers = {'Content-Type': 'image/jpeg'}
                                        if "blob.core.windows.net" in urls['thumbnail_url']:
                                            thumb_headers['x-ms-blob-type'] = 'BlockBlob'
                                        
                                        with open(thumb_path, 'rb') as f:
                                            make_request_with_retry('put', urls['thumbnail_url'], data=f, headers=thumb_headers)
                                    
                                    # Confirm upload
                                    url = confirm_upload_endpoint.format(media_id=media_id)
                                    make_request_with_retry('post', url, headers=headers)
                                    
                                    progress.advance(upload_task, 2)

                                # Confirm batch
                                url = batch_confirm_endpoint.format(batch_id=batch_id)
                                make_request_with_retry('post', url, headers=headers)
                                
                                progress.log(f"[green]Successfully processed batch {batch_index + 1}/{total_batches} for {folder_name}[/green]")
                                folder_batch_stats[folder_name]["successful_batches"] += 1
                                
                            except Exception as e:
                                progress.log(f"[red]Error processing batch {batch_index + 1} for {folder_name}: {str(e)}[/red]")
                        
                        # Check if at least one batch was successful
                        if folder_batch_stats[folder_name]["successful_batches"] > 0:
                            progress.log(f"[green]Successfully processed {folder_name} - {folder_batch_stats[folder_name]['successful_batches']}/{total_batches} batches completed[/green]")
                            processed_folders.append(folder_name)
                            processed_count += 1
                        else:
                            progress.log(f"[red]Failed to process any batches for {folder_name}[/red]")
                            failed_folders.append(folder_name)
                            failed_count += 1

                    finally:
                        cleanup_thumbnails(folder_path)

                except Exception as e:
                    progress.log(f"[red]Error processing {folder_name}: {str(e)}[/red]")
                    failed_folders.append(folder_name)
                    failed_count += 1
                    cleanup_thumbnails(folder_path)

        # Print summary with numerical sorting and batch statistics
        print("\n[cyan]Upload Process Summary:[/cyan]")
        print(f"[green]Successfully processed: {processed_count} folders ({total_processed_files} files)[/green]")
        
        for folder in sorted(processed_folders, key=natural_sort_key):
            stats = folder_batch_stats.get(folder, {})
            total_batches = stats.get("total_batches", 0)
            successful_batches = stats.get("successful_batches", 0)
            total_images = stats.get("total_images", folder_file_counts[folder])
            
            print(f"[green]✓ {folder} ({total_images} files) - {successful_batches}/{total_batches} batches completed[/green]")
            
        if failed_folders:
            print(f"\n[red]Failed to process: {failed_count} folders[/red]")
            for folder in sorted(failed_folders, key=natural_sort_key):
                stats = folder_batch_stats.get(folder, {})
                total_batches = stats.get("total_batches", 0)
                successful_batches = stats.get("successful_batches", 0)
                total_images = stats.get("total_images", folder_file_counts[folder])
                
                if folder in folder_batch_stats:
                    print(f"[red]✗ {folder} ({total_images} files) - {successful_batches}/{total_batches} batches completed[/red]")
                else:
                    print(f"[red]✗ {folder} ({folder_file_counts[folder]} files) - Failed before batch processing[/red]")

        return processed_count > 0

    except Exception as e:
        print(f"[red]Error during folder upload process: {str(e)}[/red]")
        return False
