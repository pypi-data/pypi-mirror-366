"""
Authentication commands for darkfield CLI
"""

import click
import webbrowser
import time
import keyring
from urllib.parse import urlencode
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..config import DARKFIELD_API_URL, DARKFIELD_AUTH_URL

console = Console()

@click.group()
def auth():
    """Manage authentication and API keys"""
    pass

@auth.command()
def login():
    """Authenticate with darkfield"""
    console.print("\n[cyan]Starting authentication flow...[/cyan]")
    
    # Generate device code for OAuth device flow
    import requests
    import secrets
    
    device_code = secrets.token_urlsafe(32)
    
    # Start device authorization
    params = {
        "client_id": "darkfield-cli",
        "scope": "api:full billing:read",
        "device_code": device_code
    }
    
    auth_url = f"{DARKFIELD_AUTH_URL}/device/authorize?{urlencode(params)}"
    
    console.print(f"\n[yellow]Please visit:[/yellow] {auth_url}")
    console.print("[yellow]Or press Enter to open in your browser automatically...[/yellow]")
    
    if click.confirm("Open browser?", default=True):
        webbrowser.open(auth_url)
    
    # Poll for authorization
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Waiting for authentication...", total=None)
        
        start_time = time.time()
        timeout = 300  # 5 minutes
        
        while time.time() - start_time < timeout:
            try:
                # Check if user has authorized
                response = requests.post(f"{DARKFIELD_API_URL}/auth/device/token", json={
                    "device_code": device_code,
                    "client_id": "darkfield-cli"
                })
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Store credentials securely
                    keyring.set_password("darkfield-cli", "api_key", data["api_key"])
                    keyring.set_password("darkfield-cli", "user_email", data["email"])
                    keyring.set_password("darkfield-cli", "user_id", data["user_id"])
                    
                    progress.stop()
                    console.print(f"\n[green]✓[/green] Successfully authenticated as {data['email']}")
                    console.print(f"[green]✓[/green] API tier: {data['tier'].upper()}")
                    
                    # Show initial setup instructions
                    if data.get("is_new_user"):
                        console.print("\n[cyan]Welcome to darkfield![/cyan]")
                        console.print("Get started with: [bold]darkfield analyze --help[/bold]")
                        if data["tier"] == "free":
                            console.print("\n[yellow]Note: You're on the free tier.[/yellow]")
                            console.print("Upgrade for higher limits: [bold]darkfield billing upgrade[/bold]")
                    
                    return
                    
                elif response.status_code == 403:
                    progress.stop()
                    console.print("\n[red]✗[/red] Authentication denied")
                    return
                    
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        progress.stop()
        console.print("\n[red]✗[/red] Authentication timed out. Please try again.")

@auth.command()
def logout():
    """Log out from darkfield"""
    try:
        # Get current user for confirmation
        email = keyring.get_password("darkfield-cli", "user_email")
        
        if email and click.confirm(f"Log out from {email}?"):
            # Revoke API key on server
            api_key = keyring.get_password("darkfield-cli", "api_key")
            if api_key:
                import requests
                try:
                    requests.post(f"{DARKFIELD_API_URL}/auth/revoke", 
                                headers={"X-API-Key": api_key})
                except:
                    pass  # Best effort
            
            # Clear local credentials
            keyring.delete_password("darkfield-cli", "api_key")
            keyring.delete_password("darkfield-cli", "user_email")
            keyring.delete_password("darkfield-cli", "user_id")
            
            console.print("[green]✓[/green] Successfully logged out")
        else:
            console.print("[yellow]Logout cancelled[/yellow]")
            
    except keyring.errors.PasswordDeleteError:
        console.print("[yellow]Not currently logged in[/yellow]")

@auth.command()
def status():
    """Show current authentication status"""
    try:
        email = keyring.get_password("darkfield-cli", "user_email")
        api_key = keyring.get_password("darkfield-cli", "api_key")
        
        if email and api_key:
            # Verify API key is still valid
            import requests
            response = requests.get(f"{DARKFIELD_API_URL}/auth/verify",
                                  headers={"X-API-Key": api_key})
            
            if response.status_code == 200:
                data = response.json()
                console.print(f"[green]✓[/green] Authenticated as: {email}")
                console.print(f"API Tier: {data['tier'].upper()}")
                console.print(f"Rate Limit: {data['rate_limit']} requests/minute")
                
                # Show API key preview (last 4 chars only for security)
                key_preview = f"...{api_key[-4:]}"
                console.print(f"API Key: {key_preview}")
            else:
                console.print("[red]✗[/red] API key is no longer valid")
                console.print("Please run: [bold]darkfield auth login[/bold]")
        else:
            console.print("[yellow]Not authenticated[/yellow]")
            console.print("Run: [bold]darkfield auth login[/bold]")
            
    except Exception as e:
        console.print(f"[red]Error checking auth status: {e}[/red]")

@auth.command()
@click.option('--name', required=True, help='Name for this API key')
@click.option('--scopes', default='api:full', help='Comma-separated scopes')
def create_key(name, scopes):
    """Create a new API key for programmatic access"""
    api_key = keyring.get_password("darkfield-cli", "api_key")
    
    if not api_key:
        console.print("[red]Not authenticated. Please login first.[/red]")
        return
    
    import requests
    
    console.print(f"Creating API key '{name}' with scopes: {scopes}")
    
    response = requests.post(f"{DARKFIELD_API_URL}/auth/keys", 
                           headers={"X-API-Key": api_key},
                           json={"name": name, "scopes": scopes.split(",")})
    
    if response.status_code == 201:
        data = response.json()
        console.print(f"\n[green]✓[/green] API key created successfully")
        console.print(f"\n[yellow]Save this key securely - it won't be shown again:[/yellow]")
        console.print(f"\n[bold]{data['api_key']}[/bold]\n")
        console.print(f"Key ID: {data['key_id']}")
        console.print(f"Created: {data['created_at']}")
    else:
        console.print(f"[red]Failed to create API key: {response.json().get('error')}[/red]")

@auth.command()
def list_keys():
    """List all API keys for your account"""
    api_key = keyring.get_password("darkfield-cli", "api_key")
    
    if not api_key:
        console.print("[red]Not authenticated. Please login first.[/red]")
        return
    
    import requests
    from rich.table import Table
    
    response = requests.get(f"{DARKFIELD_API_URL}/auth/keys",
                          headers={"X-API-Key": api_key})
    
    if response.status_code == 200:
        keys = response.json()["keys"]
        
        table = Table(title="API Keys", show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Key ID", style="dim")
        table.add_column("Created", style="dim")
        table.add_column("Last Used")
        table.add_column("Status", style="green")
        
        for key in keys:
            status = "[green]Active[/green]" if key["is_active"] else "[red]Revoked[/red]"
            last_used = key.get("last_used_at", "Never")
            table.add_row(key["name"], key["id"][:8], key["created_at"][:10], last_used, status)
        
        console.print(table)
    else:
        console.print(f"[red]Failed to list keys: {response.json().get('error')}[/red]")