"""List command for bundle requests."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from leap_bundle.utils.api_client import APIClient
from leap_bundle.utils.config import is_logged_in

console = Console()


def list_requests(
    request_id: Optional[str] = typer.Argument(
        None, help="Optional request ID to get details for a specific request"
    ),
) -> None:
    """List bundle requests or get details for a specific request."""

    if not is_logged_in():
        console.print(
            "[red]✗[/red] You must be logged in. Run 'leap-bundle login' first."
        )
        raise typer.Exit(1)

    try:
        client = APIClient()

        if request_id:
            console.print(
                f"[blue]ℹ[/blue] Fetching details for request {request_id}..."
            )
            result = client.get_bundle_request(request_id)
            request = result["request"]

            console.print("[green]✓[/green] Request Details:")
            console.print(f"  ID:         {request['external_id']}")
            console.print(f"  Input Path: {request['input_path']}")
            console.print(f"  Status:     {request['status']}")
            console.print(f"  Creation:   {request['created_at']}")
            console.print(f"  Update:     {request['updated_at']}")
        else:
            console.print("[blue]ℹ[/blue] Fetching bundle requests...")
            result = client.list_bundle_requests()
            requests = result["requests"]

            if not requests:
                console.print("[yellow]⚠[/yellow] No bundle requests found.")
                return

            table = Table(title="Bundle Requests (50 most recent)")
            table.add_column("ID", style="cyan")
            table.add_column("Input Path", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Creation", style="blue")

            for request in requests:
                table.add_row(
                    str(request["external_id"]),
                    request["input_path"],
                    request["status"],
                    request["created_at"],
                )

            console.print(table)
            console.print(f"[green]✓[/green] Found {len(requests)} bundle requests.")

    except Exception as e:
        from leap_bundle.utils.api_client import handle_cli_exception

        handle_cli_exception(e)
