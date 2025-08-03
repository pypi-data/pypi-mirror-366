from rich.console import Console
from rich.text import Text
from string import Template
from pathlib import Path
import importlib.resources
import typer
from marksum.llm_provider import summarize_with_gemini
from rich.markdown import Markdown
from marksum import __version__

app = typer.Typer(help="Marksum: A CLI tool to summarize Markdown files using LLMs like Gemini.")

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to Markdown file or directory"),
    summary: bool = typer.Option(False, help="Generate TL;DR summary"),
    bullets: bool = typer.Option(False, help="Generate bullet points"),
    output: str = typer.Option(None, help="Output file (for single input) or output directory (for folders)"),
    version: bool = typer.Option(False, "--version", "-v", help="Show the version and exit", is_eager=True)
):
    if version:
        print(f"marksum v{__version__}")
        raise typer.Exit()

    console = Console()
    console.rule(f"[bold blue]Marksum: Markdown Summarizer[/bold blue]")
    console.print(f"[cyan]Path:[/cyan] {path}")
    console.print(f"[cyan]Options:[/cyan] summary={summary}, bullets={bullets}, output={output}")

    input_path = Path(path)
    if input_path.is_dir():
        markdown_files = list(input_path.rglob("*.md"))
        if not markdown_files:
            console.print(f"[bold yellow]Warning:[/bold yellow] No Markdown files found in directory.")
            raise typer.Exit()
    elif input_path.is_file():
        markdown_files = [input_path]
    else:
        console.print(f"[bold red]Error:[/bold red] Path not found: {path}")
        raise typer.Exit(code=1)

    for file_path in markdown_files:
        try:
            markdown_text = file_path.read_text(encoding="utf-8").strip()
            if not markdown_text:
                console.print(f"[yellow]Skipping empty file:[/yellow] {file_path}")
                continue
            console.print(f"[green]✓ Loaded {len(markdown_text.split())} words from [bold]{file_path.name}[/bold][/green]")

            template_name = "bullets.txt" if bullets else "default.txt"
            try:
                template_str = importlib.resources.read_text("marksum.prompts", template_name, encoding="utf-8")
            except (FileNotFoundError, ModuleNotFoundError) as e:
                console.print(f"[bold red]Error:[/bold red] Prompt template not found: {e}")
                raise typer.Exit(code=1)
            prompt = Template(template_str).substitute(markdown=markdown_text)

            try:
                summary_text = summarize_with_gemini(prompt)
            except Exception as e:
                console.print(f"[bold red]Gemini API Error while processing {file_path.name}:[/bold red] {e}")
                continue

            if output:
                output_path = Path(output)
                if output_path.suffix == ".md" and len(markdown_files) > 1:
                    console.print(f"[bold red]Error:[/bold red] Cannot write multiple summaries to a single file.")
                    raise typer.Exit(code=1)
                if len(markdown_files) == 1:
                    output_path.write_text(summary_text, encoding="utf-8")
                    console.print(f"[bold green]✓ Summary saved to [italic]{output_path}[/italic][/bold green]")
                else:
                    relative = file_path.relative_to(input_path)
                    out_file = output_path / relative.with_suffix(".summary.md")
                    out_file.parent.mkdir(parents=True, exist_ok=True)
                    out_file.write_text(summary_text, encoding="utf-8")
                    console.print(f"[green]✓ Saved:[/green] {out_file}")
            else:
                console.rule(f"[bold magenta]Summary for {file_path.name}[/bold magenta]")
                console.print(Markdown(summary_text))

        except Exception as e:
            console.print(f"[bold red]Error processing {file_path.name}:[/bold red] {e}")

if __name__ == "__main__":
    app()