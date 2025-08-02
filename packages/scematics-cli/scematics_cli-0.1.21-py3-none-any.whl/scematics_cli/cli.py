import typer
import requests
from rich import print
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from pathlib import Path
from typing import Optional, List, Dict
import json
import os
import time
import csv
import zipfile
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from custom_upload import handle_folder_video_upload as video_uploader
from custom_upload_local import process_directory_structure as video_uploader
from custom_upload_buckets import register_existing_s3_files

app = typer.Typer(help="Scematics API Access CLI Tool")
console = Console()

class Config:
    def __init__(self):
        # Default URLs for different services
        self.DEFAULT_IM_SERVER_URL = "app.scematics.xyz"
        self.DEFAULT_EX_SERVER_URL = "app.scematics.xyz"
        self.DEFAULT_BASE_URL = "https://app.scematics.xyz/api/v1"
        self.DEFAULT_EXPORT_URL = "https://app-export.scematics.xyz/api/v1"
        self.DEFAULT_IMPORT_URL = "https://app-import.scematics.xyz/api/v1"
        
        # Initialize config with defaults
        self.config = {
            'base_url': os.getenv('SCEMATICS_API_URL', self.DEFAULT_BASE_URL),
            'get_im_server': os.getenv('DEFAULT_IM_SERVER_URL', self.DEFAULT_IM_SERVER_URL),
            'get_ex_server': os.getenv('DEFAULT_EX_SERVER_URL', self.DEFAULT_EX_SERVER_URL),
            'export_url': os.getenv('SCEMATICS_EXPORT_URL', self.DEFAULT_EXPORT_URL),
            'import_url': os.getenv('SCEMATICS_IMPORT_URL', self.DEFAULT_IMPORT_URL),
            'token': os.getenv('SCEMATICS_TOKEN', "")
        }

    def get_base_url(self):
        """Get base URL"""
        return self.config.get('base_url')
    
    def get_im_server(self):
        """Get base URL"""
        return self.config.get('get_im_server')
    
    def get_ex_server(self):
        """Get base URL"""
        return self.config.get('get_ex_server')

    def get_export_url(self):
        """Get export service URL"""
        return self.config.get('export_url')

    def get_import_url(self):
        """Get import service URL"""
        return self.config.get('import_url')

    def set_token(self, token):
        """Save token"""
        self.config['token'] = token

    def clear_token(self):
        """Clear token"""
        self.config['token'] = ""

    def validate_token(self):
        """Validate current token"""
        token = self.config.get('token')
        if not token:
            return False
            
        try:
            response = requests.get(
                f"{self.get_base_url()}/protected",
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.status_code == 200
        except:
            return False

    def handle_login(self):
        """Handle login process"""
        print("[yellow]Please choose your authentication method.[/yellow]")
        choice = Prompt.ask("Choose option (1: Login with credentials, 2: Use API key)", choices=["1", "2"], default="1")
        
        if choice == "1":
            username = Prompt.ask("Username")
            password = Prompt.ask("Password", password=True)
            try:
                response = requests.post(
                    f"{self.get_base_url()}/login",
                    data={"username": username, "password": password}
                )
                response.raise_for_status()
                token = response.json()["access_token"]
                self.set_token(token)
                print("[green]Login successful![/green]")
                return True
            except:
                print("[red]Login failed![/red]")
                return False
            
        else:  # API key option
            api_key = Prompt.ask("Enter your API key")
            self.set_token(api_key)
            if self.validate_token():
                print("[green]API key validated successfully![/green]")
                return True
            else:
                print("[red]Invalid API key![/red]")
                self.clear_token()
                return False

    def handle_request(self, method, url, **kwargs):
        """Handle requests with automatic token validation"""
        token = self.config.get('token')
        if not token:
            if not self.handle_login():
                raise typer.Exit(1)
            token = self.config.get('token')
        
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']["Authorization"] = f"Bearer {token}"
        
        try:
            response = method(url, **kwargs)
            
            if response.status_code == 401:
                print("[yellow]Authentication expired. Please login again...[/yellow]")
                self.clear_token()
                
                if self.handle_login():
                    kwargs['headers']["Authorization"] = f"Bearer {self.config['token']}"
                    response = method(url, **kwargs)
                    response.raise_for_status()
                    return response
                else:
                    raise Exception("Failed to refresh authentication")
                    
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"[red]Request failed: {str(e)}[/red]")
            raise

def get_config():
    """Get or create config instance"""
    try:
        return Config()
    except Exception as e:
        print(f"[red]Failed to initialize config: {str(e)}[/red]")
        raise typer.Exit(1)

def show_menu():
    """Display menu options"""
    print("\n+" + "-" * 50 + "+")
    print("|" + "Available Commands".center(50) + "|")
    print("+" + "-" * 50 + "+")
    
    options = [
        ("1", "List All Projects"),
        ("2", "Get Project Details"),
        ("3", "Upload Images (Local to App)"),
        ("4", "Export Annotations"),
        ("5", "Import Annotations"),
        ("6", "Upload Media (Local/Cloud to App)"),
        ("7", "Logout"),
        ("q", "Quit")
    ]
    
    for option, description in options:
        print(f"| {option:>4} | {description:<41} |")
    
    print("+" + "-" * 50 + "+")
    
    choice = Prompt.ask("\nEnter your choice", choices=["1", "2", "3", "4", "5", "6", "q"])
    return choice

def handle_list_projects(config):
    """Handle list projects with simplified column display"""
    try:
        # Get user input for parameters
        limit = Prompt.ask("Enter limit (press Enter for default 30)", default="30")
        skip = Prompt.ask("Enter skip (press Enter for default 0)", default="0")
        search = Prompt.ask("Enter search term (press Enter to skip)", default="")
        
        try:
            limit = int(limit)
            skip = int(skip)
            if limit < 1:
                print("[yellow]Invalid limit. Using default 30[/yellow]")
                limit = 30
            if skip < 0:
                print("[yellow]Invalid skip. Using default 0[/yellow]")
                skip = 0
        except ValueError:
            print("[yellow]Invalid numeric input. Using defaults[/yellow]")
            limit = 30
            skip = 0

        params = {
            "is_archived": 0,
            "skip": skip,
            "limit": limit
        }
        
        if search.strip():
            params["search"] = search.strip()

        response = config.handle_request(
            requests.get,
            f"{config.get_base_url()}/project/all",
            params=params
        )
        
        projects = response.json().get('data', [])
        
        if not projects:
            print("[yellow]No projects found[/yellow]")
            return

        # Print table header
        print("\n+" + "-" * 100 + "+")
        print("|" + "Projects List".center(100) + "|")
        print("+" + "-" * 100 + "+")
        print("|" + "Name".ljust(30) + "|" + "ID".ljust(45) + "|" + "Progress".center(21) + "|")
        print("+" + "-" * 100 + "+")
        
        # Print project rows
        for project in projects:
            name = project.get('project_name', 'N/A')
            project_id = project.get('project_id', 'N/A')
            progress = f"{project.get('progress', 0)}.0%"
            
            print(
                f"|{name.ljust(30)}"
                f"|{project_id.ljust(45)}"
                f"|{progress.rjust(21)}|"
            )
        
        print("+" + "-" * 100 + "+")
        print(f"\n[blue]Total projects shown: {len(projects)}[/blue]")
        
        # Navigation options
        if len(projects) == limit or skip > 0:
            print("\nNavigation:")
            options = ["q"]
            if skip > 0:
                print("p - Previous page")
                options.append("p")
            if len(projects) == limit:
                print("n - Next page")
                options.append("n")
            print("q - Return to menu")
            
            choice = Prompt.ask("Choose option", choices=options, default="q")
            if choice == "n" and len(projects) == limit:
                handle_list_projects(config)
            elif choice == "p" and skip > 0:
                skip = max(0, skip - limit)
                handle_list_projects(config)
                
    except Exception as e:
        print(f"[red]Failed to fetch projects: {str(e)}[/red]")

def handle_get_project(config):
    """Get detailed project view using project ID"""
    try:
        project_id = Prompt.ask("Enter project ID")
        
        # Get all projects to find the one we want
        response = config.handle_request(
            requests.get,
            f"{config.get_base_url()}/project/all",
            params={"limit": 100, "is_archived": 0}
        )
        
        projects = response.json().get('data', [])
        
        # Find the project with matching ID
        project = next((p for p in projects if p.get('project_id') == project_id), None)
        
        if not project:
            print("[red]Project not found[/red]")
            return
            
        # Display detailed information
        print("\n+" + "-" * 100 + "+")
        print("|" + "Project Details".center(100) + "|")
        print("+" + "-" * 100 + "+")
        
        # Get the specific fields
        total_count = project.get('goal', {}).get('total_count', 0)
        completed_count = project.get('goal', {}).get('completed_count', 0)
        
        # Create a list of fields to display
        fields = [
            ("Project Name", project.get('project_name', 'N/A')),
            ("Project ID", project.get('project_id', 'N/A')),
            ("Description", project.get('description', 'N/A')),
            ("Progress", f"{project.get('progress', 0)}.0%"),
            ("Total Images", str(total_count)),
            ("Completed Images", str(completed_count))
        ]
        
        # Display fields in table format
        for key, value in fields:
            print(f"| {key:<20} | {str(value):<75} |")
        
        print("+" + "-" * 100 + "+")
        
    except Exception as e:
        print(f"[red]Failed to fetch project details: {str(e)}[/red]")
        
def show_upload_menu():
    """Display image upload options menu (local only)"""
    print("\n+" + "-" * 52 + "+")
    print("|" + "Upload Images (Local to App)".center(52) + "|")
    print("+" + "-" * 52 + "+")

    options = [
        ("1", "Upload Images (Single/Multiple)"),
        ("2", "Upload Image Folder (Project-wise)"),
        ("3", "Upload with Tags (Local Images)"),
        ("b", "Back to Main Menu"),
    ]

    for option, description in options:
        print(f"| {option:>4} | {description:<45} |")

    print("+" + "-" * 52 + "+")
    
    return Prompt.ask("\nEnter your choice", choices=["1", "2", "3", "b"])

def show_video_upload_menu():
    """Display media upload options menu (local/cloud to app)"""
    print("\n+" + "-" * 52 + "+")
    print("|" + "Upload Media (Image/Video from Local/Cloud)".center(52) + "|")
    print("+" + "-" * 52 + "+")

    options = [
        ("1", "Upload Folder (Local Image/Video)"),
        ("2", "Quick Upload (Local to App)"),
        ("3", "Upload from Custom Storage (S3/GCP/Azure)"),
        ("b", "Back to Main Menu"),
    ]

    for option, description in options:
        print(f"| {option:>4} | {description:<43} |")

    print("+" + "-" * 52 + "+")
    
    return Prompt.ask("\nEnter your choice", choices=["1", "2", "3", "b"])

def handle_image_uploads(config):
    """Main image upload handler"""
    while True:
        choice = show_upload_menu()
        
        if choice == "1":
                # Get the required values from config before passing
                base_url = config.get_base_url()
                token = config.config.get('token', '')
                
                project_id = Prompt.ask("Enter project ID")
                folder_path = Prompt.ask("Enter folder path containing data")
                
                # Show media type selection menu
                print("\n[bold blue]Select media type:[/bold blue]")
                print("[1] IMAGE - Process only image files")
                print("[2] VIDEO - Process only video files")
                
                # Get media type selection
                media_type_choice = Prompt.ask(
                    "Select media type", 
                    choices=["1", "2"], 
                    default="3"
                )
                
                use_metadata = True
                if media_type_choice == "1":
                    media_type = "IMAGE"
                    print("[cyan]Selected media type: IMAGE[/cyan]")
                elif media_type_choice == "2":
                    media_type = "VIDEO"
                    # For videos, show metadata options
                    print("\n[bold blue]Metadata options for videos:[/bold blue]")
                    print("[y] Yes - Use JSON metadata files with matching names (default)")
                    print("[n] No - Skip metadata processing")
                    
                    # For videos, ask about metadata
                    metadata_choice = Prompt.ask(
                        "Use metadata for videos?",
                        choices=["y", "n"],
                        default="y"
                    )
                    use_metadata = metadata_choice.lower() == "y"
                    print(f"[cyan]Selected media type: VIDEO (Metadata: {'Enabled' if use_metadata else 'Disabled'})[/cyan]")
                else:
                    media_type = "AUTO"  # Auto-detect based on file extension
                    print("[cyan]Selected media type: AUTO (detect from file extension)[/cyan]")
                
                print(f"\n[cyan]Starting upload process:[/cyan]")
                print(f"[cyan]- Project ID: {project_id}[/cyan]")
                print(f"[cyan]- Folder: {folder_path}[/cyan]")
                print(f"[cyan]- Media Type: {media_type}[/cyan]")
                if media_type == "VIDEO" or media_type == "AUTO":
                    print(f"[cyan]- Metadata for videos: {'Enabled' if use_metadata else 'Disabled'}[/cyan]")
                
                from direct_upload import handle_direct_upload as direct_uploader
                direct_uploader(base_url, token, project_id, folder_path, media_type=media_type, use_metadata=use_metadata)
        elif choice == "2":
                base_url = config.get_base_url()
                token = config.config.get('token', '')
            
                folder_path = Prompt.ask("Enter main folder path ")
        
                from .folder_uploads import handle_folder_upload as folder_uploader
                folder_uploader(base_url, token, folder_path)
        elif choice == "3":
                # Get the required values from config before passing
                base_url = config.get_base_url()
                token = config.config.get('token', '')
                
                project_id = Prompt.ask("Enter project ID")
                folder_path = Prompt.ask("Enter folder path containing data")
                
                print(f"\n[cyan]Starting upload process:[/cyan]")
                print(f"[cyan]- Project ID: {project_id}[/cyan]")
                print(f"[cyan]- Folder: {folder_path}[/cyan]")
                
                from .tag_uploads import handle_tag_based_upload as tag_uploader
                tag_uploader(base_url, token, project_id, folder_path)
        elif choice == "b":
            break
            
        input("\nPress Enter to continue...")
def handle_custom_video_uploads(config):
    """Main image upload handler"""
    while True:
        choice = show_video_upload_menu()
        if choice == "1":
                # Get the required values from config before passing
                base_url = config.get_base_url()
                token = config.config.get('token', '')
                
                project_id = Prompt.ask("Enter project ID")
                folder_path = Prompt.ask("Enter folder path containing data")
                # base_filename = Prompt.ask("filter name")
                
                print(f"\n[cyan]Starting upload process:[/cyan]")
                print(f"[cyan]- Project ID: {project_id}[/cyan]")
                print(f"[cyan]- Folder: {folder_path}[/cyan]")
                # print(f"[cyan]- Base Filename: {base_filename}[/cyan]")
                
                video_uploader(base_url, token, project_id, folder_path)
        
        elif choice == "2":
            # Get the required values from config before passing
            base_url = config.get_base_url()
            token = config.config.get('token', '')
            
            project_id = Prompt.ask("Enter project ID")
            folder_path = Prompt.ask("Enter folder path containing data")
            # base_filename = Prompt.ask("filter name")
            
            print(f"\n[cyan]Starting upload process:[/cyan]")
            print(f"[cyan]- Project ID: {project_id}[/cyan]")
            print(f"[cyan]- Folder: {folder_path}[/cyan]")
            # print(f"[cyan]- Base Filename: {base_filename}[/cyan]")
            
            video_uploader(base_url, token, project_id, folder_path)
        
        elif choice == "3":
            # Get the required values from config before passing
            base_url = config.get_base_url()
            token = config.config.get('token', '')

            project_id = Prompt.ask("Enter project ID")
            folder_path = Prompt.ask("Enter folder path")
            thumbnail_path = Prompt.ask("Enter thumbnail path")
            base_filename = Prompt.ask("filter name")
            file_type = Prompt.ask(
                "File type", 
                choices=["IMAGE", "VIDEO"], 
                default="IMAGE"
            )

            # Get all cloud storage buckets
            response = config.handle_request(
                requests.get,
                f"{base_url}/settings/cloud_storage/list",
            )

            buckets_list = response.json().get('data', [])

            # Print simple ASCII table header
            print("+" + "-" * 90 + "+")
            print(f"| {'ID':<5} | {'Storage Name':<20} | {'Resource Name':<30} | {'Provider':<20} |")
            print("+" + "-" * 90 + "+")

            # Print each row of the table
            for bucket in buckets_list:
                print(f"| {str(bucket.get('id', '')):<5} | "
                      f"{bucket.get('storage_name', ''):<20} | "
                      f"{bucket.get('resource_name', ''):<30} | "
                      f"{bucket.get('provider', ''):<20} |")

            print("+" + "-" * 90 + "+")

            # Prompt user to select a bucket
            bucket_id = Prompt.ask("Enter bucket ID")

            # Print basic upload info
            print("\nStarting upload process:")
            print(f"- Project ID: {project_id}")
            print(f"- Folder: {folder_path}")
            print(f"[cyan]- Base Filename: {base_filename}[/cyan]")

            # Import and call upload function
            register_existing_s3_files(base_url, token, bucket_id, project_id, folder_path, base_filename,file_type,thumbnail_path)
            
        elif choice == "b":
            break
            
        input("\nPress Enter to continue...")

def handle_export_annotations(config):
    """Handle annotation export with improved WebSocket monitoring and aligned summary table"""
    
    import requests
    import zipfile
    import csv
    import json
    import threading
    import asyncio
    import websockets
    import time
    import tqdm
    from pathlib import Path
    from typing import List, Dict
    
    def get_project_id(project_name, config):
        """Get project_id using direct project name endpoint."""
        try:
            response = config.handle_request(
                requests.get,
                f"{config.get_base_url()}/project/by_project_name/{project_name}",
            )
            data = response.json().get("data", {})
            return data.get("id") if data else None
        except Exception as e:
            print(f"Error resolving project name: {e}")
            return None
    
    def get_export_listing(project_id, config, max_retries=5, delay=2):
        """Get export listing for a project with retry logic."""
        for attempt in range(max_retries):
            try:
                response = config.handle_request(
                    requests.get,
                    f"{config.get_export_url()}/export/listing/{project_id}",
                )
                data = response.json().get("data", [])
                return data
            except Exception as e:
                print(f"Error getting export listing (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 1.5  # Exponential backoff
        return []
    
    def extract_zip(zip_path: Path, extract_path: Path) -> bool:
        """Extract zip file to specified path and delete the zip if successful"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Attempt to delete the zip file after successful extraction
            try:
                zip_path.unlink()
                return True
            except Exception as delete_error:
                print(f"Warning: Extracted files kept but failed to delete ZIP - {str(delete_error)}")
                return False
                
        except Exception as e:
            print(f"Error extracting {zip_path}: {str(e)}")
            return False

    def get_projects(formats_data: List[Dict]) -> List[Dict]:
        """Get list of projects from user via text input or CSV"""
        print("\nChoose input method:")
        print("1. Text input (comma-separated project names)")
        print("2. CSV template\n")
        
        while True:
            input_method = input("Choose input method [1/2] (default: 1): ").strip() or "1"
            if input_method in ["1", "2"]:
                break
            print("Please enter 1 or 2")
        
        if input_method == "1":
            projects_input = input("Enter project names (comma-separated): ")
            return [{'project_name': name.strip(), 'format_name': None} 
                    for name in projects_input.split(",") if name.strip()]
        else:
            # Display available formats in a table
            print("\nAvailable Export Formats:")
            print("+" + "-" * 60 + "+")
            print(f"|{'ID':^10}|{'Format Name':^48}|")
            print("+" + "-" * 60 + "+")
            
            for fmt in formats_data:
                print(f"|{str(fmt['id']):^10}|{fmt['format']:<48}|")
            
            print("+" + "-" * 60 + "+\n")
            
            # Show CSV template
            print("CSV Template Format:")
            print("project_name,format_name  # Use exact format names from table above")
            
            csv_path = input("Enter path to CSV file: ")
            projects = []
            try:
                with open(csv_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        project_name = row.get('project_name', '').strip()
                        format_name = row.get('format_name', '').strip()
                        if not project_name or not format_name:
                            print(f"Skipping invalid row: {row}")
                            continue
                        projects.append({
                            'project_name': project_name,
                            'format_name': format_name
                        })
                return projects
            except Exception as e:
                print(f"Error reading CSV: {str(e)}")
                return []

    async def monitor_websocket(ws_url, export_id, pbar=None, timeout=600):
        """
        WebSocket monitor with heartbeat support and tqdm progress tracking
        
        Args:
            ws_url (str): WebSocket URL to connect to
            export_id (int): Export ID being monitored
            pbar (tqdm.tqdm): Optional progress bar to update
            timeout (int): Maximum time to wait in seconds
            
        Returns:
            dict: Final export status with download URL if successful
        """
        start_time = time.time()
        last_message_time = start_time
        export_status = {
            "status": None, 
            "progress": 0, 
            "error": None, 
            "download_url": None,
            "export_id": export_id
        }
        export_complete = threading.Event()
        heartbeat_interval = 10  # seconds
        
        # Create progress bar if none provided, with position parameter to ensure it stays in place
        if pbar is None:
            pbar = tqdm.tqdm(
                total=100, 
                desc=f"Export {export_id} progress", 
                unit="%",
                position=0,
                leave=True  # Ensures it stays after completion
            )
        
        async def send_heartbeats(websocket):
            """Send periodic heartbeats to keep connection alive"""
            try:
                while True:
                    await asyncio.sleep(heartbeat_interval)
                    await websocket.send(json.dumps({"type": "heartbeat"}))
            except (asyncio.CancelledError, websockets.exceptions.ConnectionClosed):
                pass
            except Exception as e:
                print(f"Heartbeat error: {str(e)}")
        
        try:
            async with websockets.connect(ws_url, ping_interval=20, ping_timeout=30) as websocket:
                # Update description instead of printing to console
                pbar.set_description(f"WebSocket connected (export {export_id})")
                
                # Start heartbeat task
                heartbeat_task = asyncio.create_task(send_heartbeats(websocket))
                
                while not export_complete.is_set() and (time.time() - start_time) < timeout:
                    try:
                        # Use a shorter timeout to check overall completion periodically
                        response = await asyncio.wait_for(websocket.recv(), timeout=5)
                        last_message_time = time.time()
                        
                        try:
                            data = json.loads(response)
                            
                            # Update progress if available
                            new_progress = None
                            if "progress" in data:
                                new_progress = float(data["progress"])
                            elif "percentage" in data:
                                new_progress = float(data["percentage"])
                                
                            if new_progress is not None:
                                # Handle progress updates correctly
                                if new_progress > export_status["progress"]:
                                    # Calculate delta for tqdm (only positive updates)
                                    progress_delta = new_progress - export_status["progress"]
                                    export_status["progress"] = new_progress
                                    
                                    # Update tqdm progress bar
                                    pbar.update(progress_delta)
                                
                            # Update status if available
                            if "status" in data:
                                export_status["status"] = data["status"]
                                # Update description rather than printing
                                pbar.set_description(f"Export {export_id}: {data['status']}")
                                
                                if data["status"] in ["SUCCESS", "COMPLETED", "DONE"]:
                                    export_status["download_url"] = data.get("download_url")
                                    # Make sure progress bar is at 100%
                                    remaining = max(0, 100 - export_status["progress"])
                                    if remaining > 0:
                                        pbar.update(remaining)
                                    export_complete.set()
                                elif data["status"] in ["ERROR", "FAILED"]:
                                    export_status["error"] = data.get("error", "Unknown error")
                                    export_complete.set()
                                    
                        except json.JSONDecodeError:
                            # Update description instead of printing
                            pbar.set_description(f"Export {export_id}: received non-JSON response")
                            
                    except asyncio.TimeoutError:
                        # Check if we've been waiting too long for a message
                        if (time.time() - last_message_time) > 60:  # No messages for 1 minute
                            # Update description instead of printing
                            pbar.set_description(f"Export {export_id}: no updates for >1min")
                            # Reset the timer to avoid spamming the warning
                            last_message_time = time.time()
                    except websockets.exceptions.ConnectionClosed:
                        # Update description instead of printing
                        pbar.set_description(f"Export {export_id}: WebSocket closed")
                        export_complete.set()
                
                # Cancel heartbeat task
                heartbeat_task.cancel()
                
                # Check if we timed out
                if not export_complete.is_set():
                    # Update description instead of printing
                    pbar.set_description(f"Export {export_id}: monitoring timed out")
                    export_status["status"] = "TIMEOUT"
                    export_status["error"] = "Monitoring timed out"
                
                return export_status
                
        except Exception as e:
            # Update description instead of printing
            if pbar:
                pbar.set_description(f"Export {export_id}: connection error")
            export_status["status"] = "ERROR"
            export_status["error"] = str(e)
            return export_status

    def wait_for_export_completion(project_id, export_id, config, max_wait_time=300, interval=5):
        """Wait for export to complete by periodically checking the export listing"""
        print(f"Waiting for export {export_id} to complete...")
        
        # Use position parameter to ensure the progress bar stays in place
        progress_bar = tqdm.tqdm(
            total=100,  # Change total from max_wait_time to 100 to represent percentage completion
            desc="Export status: IN-PROGRESS", 
            unit="%",   # Change unit from "s" to "%"
            position=0,
            leave=True,  # Ensures it stays after completion
            bar_format="{l_bar}{bar}| {n:.1f}/{total:.1f} [{elapsed}<{remaining}]"
        )
        
        start_time = time.time()
        current_progress = 0
        
        while time.time() - start_time < max_wait_time:
            # Get export listing
            export_listing = get_export_listing(project_id, config)
            
            # Find matching export
            for export in export_listing:
                if export.get("id") == export_id:
                    status = export.get("export_status")
                    # Update progress description
                    progress_bar.set_description(f"Export status: {status}")
                    
                    if status == "SUCCESS":
                        # Force progress to 100% when success is detected
                        remaining = 100 - current_progress
                        if remaining > 0:
                            progress_bar.update(remaining)
                        progress_bar.close()
                        return {
                            "status": "SUCCESS",
                            "download_url": export.get("download_url"),
                            "total_images": export.get("total_images"),
                            "total_annotations": export.get("total_annotations"),
                            "total_labels": export.get("total_labels"),
                            "export_id": export_id
                        }
                    elif status in ["ERROR", "FAILED"]:
                        progress_bar.close()
                        return {
                            "status": "ERROR",
                            "error": "Export failed according to listing",
                            "export_id": export_id
                        }
            
            # Update progress bar - increment by a small percentage each check
            # This creates a more natural progress feel while waiting
            progress_increment = min(5, 100 - current_progress)  # Max 5% at a time, don't exceed 100%
            if progress_increment > 0:
                progress_bar.update(progress_increment)
                current_progress += progress_increment
            
            time.sleep(interval)
        
        progress_bar.close()
        return {
            "status": "TIMEOUT",
            "error": "Export didn't complete within the wait time",
            "export_id": export_id
        }

    def process_single_export(project: Dict, format_id: int, format_name: str, output_folder: Path) -> Dict:
        """Process export for a single project with tqdm progress tracking"""
        project_name = project['project_name']
        try:
            print(f"\nResolving project: {project_name}")
            project_id = get_project_id(project_name, config)
            
            if not project_id:
                print(f"Project not found: {project_name}")
                return {
                    "status": "ERROR",
                    "project_name": project_name,
                    "error": "Project not found",
                    "export_id": "N/A",
                    "location": "N/A",
                    "total_images": "N/A", 
                    "total_annotations": "N/A",
                    "total_labels": "N/A"
                }

            # Create filesystem-safe name with project ID
            safe_project_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in project_name)
            project_folder = output_folder / f"{safe_project_name}"
            project_folder.mkdir(parents=True, exist_ok=True)

            # Initiate export
            print(f"Starting export for {project_name}")
            export_payload = {
                "format_id": format_id,
                "zip_name": safe_project_name,
                "pid": project_id
            }
            
            response = config.handle_request(
                requests.post,
                f"{config.get_export_url()}/export/dataset",
                json=export_payload
            )
            
            export_data = response.json()
            if "export_id" not in export_data:
                raise Exception("Export initialization failed - no export ID received")
                
            export_id = export_data["export_id"]
            print(f"Export {export_id} started")

            # Set up WebSocket connection for real-time progress
            base_url = config.get_export_url()
            
            # Prepare WebSocket URL
            if base_url.startswith('https://'):
                ws_protocol = 'wss://'
                base_domain = base_url.replace('https://', '')
            else:
                ws_protocol = 'ws://'
                base_domain = base_url.replace('http://', '')
            
            # Use the direct format that worked in your output
            ws_url = f"{ws_protocol}{base_domain}/export/export-progress/{export_id}"
            
            # Create progress bar for this export - using position=0 to ensure it stays in place
            export_pbar = tqdm.tqdm(
                total=100, 
                desc=f"Exporting {project_name}", 
                unit="%", 
                position=0,
                leave=True,  # Ensures it stays after completion
                bar_format="{l_bar}{bar}| {n:.1f}/{total:.1f} [{elapsed}<{remaining}]"
            )
            
            # Run the WebSocket monitoring in the event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            export_status = loop.run_until_complete(monitor_websocket(ws_url, export_id, export_pbar))
            loop.close()
            
            # Close the progress bar
            export_pbar.close()
            
            # If WebSocket failed, fall back to polling
            if not export_status or export_status.get("status") not in ["SUCCESS", "COMPLETED", "DONE"]:
                print("WebSocket monitoring unsuccessful, switching to polling...")
                export_status = wait_for_export_completion(project_id, export_id, config)
            
            # Handle export status results
            if export_status and export_status.get("status") == "SUCCESS":
                # Check if we have a download URL
                download_url = export_status.get("download_url")
                
                # If not, try to get it from the export listing
                if not download_url:
                    print(f"No download URL found, fetching from export listing...")
                    export_listing = get_export_listing(project_id, config)
                    
                    # Find the export with matching ID
                    matching_export = None
                    for export in export_listing:
                        if export.get("id") == export_id:
                            matching_export = export
                            break
                    
                    if matching_export and matching_export.get("download_url"):
                        download_url = matching_export["download_url"]
                        print(f"Found download URL from export listing")
                        
                        # Update export status with additional metadata
                        export_status["total_images"] = matching_export.get("total_images")
                        export_status["total_annotations"] = matching_export.get("total_annotations")
                        export_status["total_labels"] = matching_export.get("total_labels")
                    else:
                        print("Could not find matching export in listing")
                
                if not download_url:
                    print("No download URL available")
                    return {
                        "status": "ERROR",
                        "project_name": project_name,
                        "project_id": project_id,
                        "export_id": export_id,
                        "error": "No download URL provided",
                        "location": "N/A",
                        "total_images": "N/A", 
                        "total_annotations": "N/A",
                        "total_labels": "N/A"
                    }
                    
                # Download the export with progress bar - using position=0 to keep it in place
                print("Downloading archive...")
                download_pbar = tqdm.tqdm(
                    desc="Downloading", 
                    unit="B", 
                    unit_scale=True, 
                    unit_divisor=1024,
                    position=0,
                    leave=True  # Ensures it stays after completion
                )
                
                zip_file = project_folder / f"{safe_project_name}.zip"
                
                # Stream the download with progress
                with requests.get(download_url, stream=True) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))
                    download_pbar.total = total_size
                    
                    with open(zip_file, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                download_pbar.update(len(chunk))
                
                download_pbar.close()

                # Extract with progress bar if possible - using position=0 to keep it in place
                print("Extracting files...")
                try:
                    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                        # Create extract progress bar
                        file_list = zip_ref.namelist()
                        extract_pbar = tqdm.tqdm(
                            total=len(file_list), 
                            desc="Extracting", 
                            unit="files",
                            position=0,
                            leave=True  # Ensures it stays after completion
                        )
                        
                        # Extract each file with progress
                        for file in file_list:
                            zip_ref.extract(file, path=project_folder)
                            extract_pbar.update(1)
                        
                        extract_pbar.close()
                    
                    # Delete zip after extraction
                    try:
                        zip_file.unlink()
                        extraction_success = True
                        print(f"Export complete for {project_name}!")
                    except Exception as delete_error:
                        print(f"Warning: Extracted files kept but failed to delete ZIP - {str(delete_error)}")
                        extraction_success = False
                        
                except Exception as e:
                    print(f"Error extracting {zip_file}: {str(e)}")
                    extraction_success = False
                
                # Handle extraction results
                if extraction_success:
                    status_code = "SUCCESS"
                else:
                    # Determine if extraction failed or just cleanup
                    if zip_file.exists():
                        print(f"Extraction failed for {project_name}")
                        status_code = "ERROR"
                    else:
                        print(f"Extracted but ZIP cleanup failed for {project_name}")
                        status_code = "WARNING"
                
                return {
                    "status": status_code,
                    "project_name": project_name,
                    "project_id": project_id,
                    "export_id": export_id,
                    "location": str(project_folder),
                    "total_images": export_status.get("total_images", "N/A"),
                    "total_annotations": export_status.get("total_annotations", "N/A"),
                    "total_labels": export_status.get("total_labels", "N/A")
                }
            else:
                # Handle error or timeout
                error_message = export_status.get("error", "Unknown error") if export_status else "Failed to monitor export"
                print(f"Export failed for {project_name}: {error_message}")
                return {
                    "status": "ERROR",
                    "project_name": project_name,
                    "project_id": project_id,
                    "export_id": export_id,
                    "error": error_message,
                    "location": "N/A",
                    "total_images": "N/A",
                    "total_annotations": "N/A",
                    "total_labels": "N/A"
                }
            
        except Exception as e:
            print(f"Error exporting {project_name}: {str(e)}")
            return {
                "status": "ERROR",
                "project_name": project_name,
                "error": str(e),
                "export_id": "N/A",
                "location": "N/A",
                "total_images": "N/A",
                "total_annotations": "N/A",
                "total_labels": "N/A"
            }
    
    def display_summary_table(results):
        """Display a properly aligned summary table of export results"""
        print("\nExport Process Complete!")
        print("\nSummary:")
        
        # Calculate column widths based on content plus padding
        p_width = max(15, max(len(str(r.get("project_name", ""))) for r in results) + 2)
        e_width = 10
        i_width = 8
        a_width = 12
        l_width = 8
        loc_width = max(20, max(len(str(r.get("location", ""))) for r in results) + 2)
        s_width = 9  # Fixed width for STATUS column
        
        # Create horizontal separator with proper width
        separator = "+" + "-" * p_width + "+" + "-" * e_width + "+" + "-" * i_width + "+" + "-" * a_width + "+" + "-" * l_width + "+" + "-" * loc_width + "+" + "-" * s_width + "+"
        
        # Print the table header
        print(separator)
        header = f"|{'Project Name':^{p_width}}|{'Export ID':^{e_width}}|{'Images':^{i_width}}|{'Annotations':^{a_width}}|{'Labels':^{l_width}}|{'Location':^{loc_width}}|{'Status':^{s_width}}|"
        print(header)
        print(separator)
        
        # Print each row with proper alignment
        success_count = 0
        for result in results:
            status = result.get("status", "N/A")
            if status == "SUCCESS":
                success_count += 1
            
            project_name = result.get('project_name', 'Unknown')
            export_id = str(result.get("export_id", "N/A"))
            total_images = str(result.get("total_images", "N/A"))
            total_annotations = str(result.get("total_annotations", "N/A"))
            total_labels = str(result.get("total_labels", "N/A"))
            location = str(result.get("location", "N/A"))
            
            # Truncate location if too long and add "..." indicator
            if len(location) > loc_width - 3:
                location = location[:loc_width - 5] + "..."
            
            # Create the row with proper alignment
            row = f"|{project_name:<{p_width}}|{export_id:^{e_width}}|{total_images:^{i_width}}|{total_annotations:^{a_width}}|{total_labels:^{l_width}}|{location:<{loc_width}}|{status:^{s_width}}|"
            print(row)
        
        # Print bottom separator and summary
        print(separator)
        print(f"\nSuccessfully exported {success_count} out of {len(results)} projects")
        
        # Find and print the base output folder
        base_folders = set()
        for result in results:
            if result.get("location", "N/A") != "N/A":
                path = Path(result.get("location"))
                base_folders.add(str(path.parent))
        
        if base_folders:
            print(f"Base output folder: {next(iter(base_folders))}")
    
    try:
        # Fetch available export formats
        print("Fetching available export formats...")
        formats_response = config.handle_request(
            requests.get,
            f"{config.get_base_url()}/export/formats/list"
        )
        
        formats_data = formats_response.json().get("data", [])
        if not formats_data:
            raise Exception("No export formats available")
            
        # Create format name to ID mapping (case-insensitive)
        format_name_to_id = {fmt['format'].lower(): fmt['id'] for fmt in formats_data}
            
        # Get projects with format information
        projects = get_projects(formats_data)
        if not projects:
            raise Exception("No valid projects provided")
            
        # Determine if using CSV formats or single format
        using_csv_formats = all('format_name' in project and project['format_name'] is not None for project in projects)
        
        if using_csv_formats:
            # Validate all format names
            for project in projects:
                format_name = project['format_name'].strip().lower()
                if format_name not in format_name_to_id:
                    raise Exception(f"Invalid format '{project['format_name']}' for project '{project['project_name']}'")
                project['format_id'] = format_name_to_id[format_name]
        else:
            # Display formats table
            print("\n+" + "-" * 60 + "+")
            print(f"|{'ID':^10}|{'Format':^48}|")
            print("+" + "-" * 60 + "+")
            
            for fmt in formats_data:
                print(f"|{str(fmt['id']):^10}|{fmt['format']:<48}|")
            
            print("+" + "-" * 60 + "+\n")
            
            # Select single format
            while True:
                try:
                    format_id_input = input("Choose format ID from the list above: ")
                    format_id = int(format_id_input)
                    if format_id in [fmt['id'] for fmt in formats_data]:
                        break
                    print("Please enter a valid format ID from the list")
                except ValueError:
                    print("Please enter a valid number")
            
            format_name = next(fmt['format'] for fmt in formats_data if fmt['id'] == format_id)
            
            # Assign format to all projects
            for project in projects:
                project['format_id'] = format_id
        
        output_folder = Path(input("Enter output folder path (default: exports): ").strip() or "exports")
        output_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"\nStarting export process for {len(projects)} projects:")
        print(f"Output folder: {output_folder}\n")
        
        # Process exports with tqdm progress tracking
        results = []
        
        # Create overall progress bar
        overall_pbar = tqdm.tqdm(
            total=len(projects), 
            desc="Overall Progress", 
            position=1,  # Position below the current export progress bar
            leave=True   # Ensures it stays after completion
        )
        
        for project in projects:
            result = process_single_export(
                project,
                project['format_id'],
                next(fmt['format'] for fmt in formats_data if fmt['id'] == project['format_id']),
                output_folder
            )
            results.append(result)
            overall_pbar.update(1)
            
        overall_pbar.close()
        
        # Display summary table with proper alignment
        display_summary_table(results)
        
        # Ask user to press Enter to continue
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"Failed to process exports: {str(e)}")
        print("You can check individual export statuses using the list exports command")
        input("\nPress Enter to continue...")
        
def handle_import_annotations(config):
    """
    Streamlined import annotation workflow:
    1. Get project_id from project name
    2. Send POST request to import data (get import_id)
    3. Monitor progress via WebSocket until completion
    """
    import csv
    from pathlib import Path
    import requests
    import websocket
    import json
    import threading
    from tqdm import tqdm
    import time

    def get_project_id(project_name, config):
        """Get project_id using direct project name endpoint."""
        try:
            response = config.handle_request(
                requests.get,
                f"{config.get_base_url()}/project/by_project_name/{project_name}"
            )
            data = response.json().get("data", {})
            return data.get("id") if data else None
        except Exception as e:
            print(f"Error resolving project name: {e}")
            return None

    def import_file(project_id, format_id, file_path, config):
        """Send file to import API and return import_id."""
        try:
            if not file_path.exists():
                print(f"File '{file_path}' does not exist.")
                return None

            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f)}
                response = config.handle_request(   
                    requests.post,
                    f"{config.get_import_url()}/imports/dataset/{project_id}",
                    params={"format_id": format_id},
                    files=files
                )
                
                if response.status_code == 200:
                    import_id = response.json().get("import_id")
                    return import_id
                else:
                    print(f"Error importing file: {response.text}")
                    return None
        except Exception as e:
            print(f"Error importing file: {e}")
            return None
    
    def monitor_import_progress(project_id, import_id, file_path, format_id):
        """Monitor import progress via WebSocket."""
        # Create result object
        result = {
            "project_id": project_id,
            "import_id": import_id,
            "file_path": str(file_path),
            "format_id": format_id,
            "status": "IN-PROGRESS",
            "message": "Importing file...",
            "processed_items": 0,
            "total_items": 0
        }
        
        # WebSocket URL
        #ws_url = f"ws://127.0.0.1:7502/api/v1/imports/import-progress/{import_id}"
        ws_url = f"ws://app-import.scematics.xyz/api/v1/imports/import-progress/{import_id}"
        print(f"Using WebSocket URL: {ws_url}")
        
        # Create progress bar
        pbar = tqdm(
            total=100,
            desc=f"Import {import_id}: IN-PROGRESS",
            bar_format="{desc}: {percentage:3.0f}%|{bar}|",
            leave=True
        )
        
        # Completion flag and WebSocket control
        is_completed = False
        should_reconnect = True
        
        def on_message(ws, message):
            nonlocal is_completed, should_reconnect
            
            try:
                data = json.loads(message)
                status = data.get("status")
                message_text = data.get("message", "")
                
                # Only update on SUCCESS
                if status == "SUCCESS":
                    # Update progress bar to 100%
                    pbar.update(100 - pbar.n)
                    pbar.set_description(f"Import {import_id}: SUCCESS")
                    
                    # Update import info
                    is_completed = True
                    should_reconnect = False
                    
                    result.update({
                        "status": "SUCCESS",
                        "message": message_text or "Import successful",
                        "processed_items": data.get("processed_items", 0),
                        "total_items": data.get("total_items", 0),
                        "processing_time": data.get("processing_time", "N/A")
                    })
                    
                    # Close WebSocket
                    ws.close()
                
                # Handle error states
                elif status in ["ERROR", "FAILED"]:
                    is_completed = True
                    should_reconnect = False
                    
                    result.update({
                        "status": status,
                        "message": message_text or f"Import {status.lower()}"
                    })
                    
                    ws.close()
            
            except json.JSONDecodeError:
                pass
        
        def on_error(ws, error):
            print(f"WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            nonlocal should_reconnect
            
            # Only attempt to reconnect if not completed
            if not is_completed and should_reconnect:
                # print(f"WebSocket disconnected, attempting to reconnect...")
                time.sleep(2)
                connect_websocket()
        
        def on_open(ws):
            pass
            # print(f"WebSocket connection established")
        
        def connect_websocket():
            """Create and connect WebSocket."""
            if is_completed or not should_reconnect:
                return
                
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            # Start in thread
            ws_thread = threading.Thread(
                target=lambda: ws.run_forever(ping_interval=30, ping_timeout=15)
            )
            ws_thread.daemon = True
            ws_thread.start()
            
            return ws_thread
        
        # Start WebSocket
        ws_thread = connect_websocket()
        
        # Wait for completion or timeout
        max_wait_time = 600  # 10 minutes max
        start_time = time.time()
        
        while not is_completed and (time.time() - start_time) < max_wait_time:
            time.sleep(1)
        
        # Handle timeout
        if not is_completed:
            result.update({
                "status": "TIMEOUT",
                "message": "Import monitoring timed out"
            })
            should_reconnect = False
        
        # Finalize
        pbar.close()
        
        # Print result
        print_result(result)
        
        # Return the result
        return result
    
    def print_result(result):
        """Print import result summary."""
        print("\nImport Result Summary:")
        separator = "-" * 80
        print(separator)
        
        file_path = result.get("file_path", "N/A")
        import_id = result.get("import_id", "N/A")
        status = result.get("status", "N/A")
        message = result.get("message", "N/A")
        
        # Format status with color
        status_display = status
        if status == "SUCCESS":
            status_display = f"\033[92m{status}\033[0m"  # Green
        elif status in ["ERROR", "FAILED"]:
            status_display = f"\033[91m{status}\033[0m"  # Red
        elif status == "IN-PROGRESS":
            status_display = f"\033[94m{status}\033[0m"  # Blue
        
        # Format items info
        processed = result.get("processed_items", 0)
        total = result.get("total_items", 0)
        processing_time = result.get("processing_time", "N/A")
        
        if total > 0:
            items = f"{processed} annotations in {processing_time} seconds"
        else:
            items = "N/A"
        
        # Print result
        print(f"File: {file_path}")
        print(f"Import ID: {import_id}")
        print(f"Status: {status_display}")
        print(f"Message: {message}")
        print(f"Items: {items}")
        print(separator)
    
    def display_formats(formats_data):
        """Display available export formats in a simple table."""
        print("\nAvailable Export Formats:")
        print("-" * 40)
        print(f"{'Format ID':<10} {'Format Name':<30}")
        print("-" * 40)
        
        for format in formats_data:
            print(f"{format['id']:<10} {format['format']:<30}")
        
        print("-" * 40)
    
    # Main execution flow
    try:
        # Fetch available export formats
        print("Fetching available export formats...")
        formats_response = config.handle_request(
            requests.get,
            f"{config.get_base_url()}/export/formats/list"
        )
        formats_data = formats_response.json().get("data", [])
        if not formats_data:
            raise Exception("No export formats available")

        # Display available formats
        display_formats(formats_data)

        # Get user input
        project_name = input("Enter project name: ").strip()
        file_path = Path(input("Enter file path: "))
        format_id = input("Enter format ID: ")
        
        # Step 1: Get project ID
        print(f"Getting project ID for '{project_name}'...")
        project_id = get_project_id(project_name, config)
        if not project_id:
            print(f"Error: Project '{project_name}' not found")
            return
        
        # Step 2: Import file (get import_id)
        print(f"Importing file '{file_path}'...")
        import_id = import_file(project_id, format_id, file_path, config)
        if not import_id:
            print("Error: Failed to import file")
            return
        
        # Step 3: Monitor progress via WebSocket
        print(f"Monitoring import progress for ID: {import_id}...")
        result = monitor_import_progress(project_id, import_id, file_path, format_id)
        
        return result
        
    except Exception as e:
        print(f"Error during import: {e}")
        return {"status": "ERROR", "error": str(e)}
    
def interactive_menu(config):
    """Main interactive menu loop"""
    while True:
        choice = show_menu()
        
        if choice == "1":
            handle_list_projects(config)
        elif choice == "2":
            handle_get_project(config)
        elif choice == "3":
            handle_image_uploads(config)
        elif choice == "4":
            handle_export_annotations(config)
        elif choice == "5":
            handle_import_annotations(config)
        elif choice == "6":
            handle_custom_video_uploads(config)
        elif choice == "7":
            config.clear_token()
            print("[yellow]Logged out successfully[/yellow]")
            break
        elif choice.lower() == "q":
            print("[yellow]Goodbye![/yellow]")
            raise typer.Exit()
            
        input("\nPress Enter to continue...")

@app.command()
def start():
    """Start the CLI tool"""
    try:
        config = get_config()
        
        if not config.validate_token():
            if not config.handle_login():
                return
        
        print("[green]Starting application...[/green]")
        interactive_menu(config)
    except Exception as e:
        print(f"[red]Error starting application: {str(e)}[/red]")
        raise typer.Exit(1)

def main():
    """Entry point for the application"""
    start()
if __name__ == "__main__":
    app()
