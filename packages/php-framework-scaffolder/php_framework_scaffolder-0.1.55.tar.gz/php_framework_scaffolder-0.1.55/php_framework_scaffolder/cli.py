import typer
from pathlib import Path
from rich.console import Console
from php_framework_scaffolder.frameworks import get_framework_handler
from php_framework_detector.core.models import FrameworkType

console = Console()
app = typer.Typer(
    help="Generate Docker Compose environments for PHP web frameworks",
    add_completion=True
)

@app.command()
def setup(
    path: Path = typer.Option(
        ...,
        help="Path to the PHP application"
    ),
    framework: FrameworkType = typer.Option(
        ...,
        help="PHP framework of the application, e.g. laravel, symfony, etc."
    ),
):
    handler = get_framework_handler(framework)
    handler.setup(path)


if __name__ == "__main__":
    app()
