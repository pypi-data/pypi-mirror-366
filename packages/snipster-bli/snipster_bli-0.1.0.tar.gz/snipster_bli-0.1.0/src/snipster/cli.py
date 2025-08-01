import asyncio
from functools import wraps
from typing import Callable, List

import typer
from decouple import config
from rich import print
from rich.console import Console, Group
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from sqlmodel import Session, create_engine
from typer import Typer
from typing_extensions import Annotated

from .exceptions import SnippetNotFoundError
from .models import Language, Snippet, SQLModel
from .repo import DBSnippetRepo
from .util import GistCreationError, RunCodeError, create_gist, run_code

app = Typer()


def generate_panel(
    snippet: Snippet,
    theme: str = "one-dark",
    show_line_numbers: bool = False,
) -> Panel:
    title = f"{snippet.title} ({snippet.language.value})"
    if snippet.favorite:
        title += " :star:"
    title_text = Text.from_markup(f"[bold]{title}[/bold]")

    content_elements = []

    if snippet.description:
        content_elements.append(Text(snippet.description, style="dim"))
        content_elements.append(Text())  # blank line for spacing

    code_block = Syntax(
        snippet.code, snippet.language, theme=theme, line_numbers=show_line_numbers
    )
    content_elements.append(code_block)

    if snippet.tags:
        tags_line = " ".join(f"@{t.name}" for t in snippet.tags)
        content_elements.append(Text(tags_line, style="dim"))

    body = Group(*content_elements)

    panel = Panel.fit(body, title=title_text, border_style="cyan")

    return panel


def print_panel(snippet: Snippet, console: Console | None = None) -> None:
    console = console or Console()
    panel = generate_panel(snippet)
    console.print(panel)


def success_message(message: str) -> None:
    print(f"[bold green]\u2705 {message}[/bold green]")


def error_message(text: str) -> None:
    print(f"[red]{text}[/]")


@app.callback()
def init(ctx: typer.Context):
    database_url = config("DATABASE_URL", default="sqlite:///snipster.db")
    engine = create_engine(database_url, echo=False)
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    repo = DBSnippetRepo(session)
    ctx.obj = {"engine": engine, "session": session, "repo": repo}


def cleanup_db_resources(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(ctx: typer.Context, *args, **kwargs):
        engine = ctx.obj["engine"]
        session: Session = ctx.obj["session"]

        try:
            return func(ctx, *args, **kwargs)
        finally:
            session.close()
            engine.dispose()

    return wrapper


@app.command()
@cleanup_db_resources
def add(
    ctx: typer.Context,
    title: Annotated[str, typer.Argument(help="Title of the code snippet")],
    code: Annotated[str, typer.Argument(help="Code written as text")],
    language: Annotated[Language, typer.Argument(help="Language of the code")],
    description: Annotated[
        str | None, typer.Option(help="Brief description of what code does")
    ] = None,
):
    """Add a code snippet."""
    repo: DBSnippetRepo = ctx.obj["repo"]
    snippet = Snippet.create(
        title=title,
        code=code,
        description=description,
        language=language,
    )
    repo.add(snippet)
    success_message(f"Snippet '{snippet.title}' added with ID {snippet.id}.")


@app.command()
@cleanup_db_resources
def list(ctx: typer.Context):
    """List all code snippets."""
    repo: DBSnippetRepo = ctx.obj["repo"]
    snippets = repo.list()
    if snippets:
        for snippet in snippets:
            print_panel(snippet)
    else:
        error_message("No snippets found.")


@app.command()
@cleanup_db_resources
def get(
    ctx: typer.Context,
    snippet_id: Annotated[int, typer.Argument(help="ID of snippet")],
):
    """Get a code snippet by its ID."""
    repo: DBSnippetRepo = ctx.obj["repo"]
    snippet = repo.get(snippet_id)
    if snippet:
        print_panel(snippet)
    else:
        error_message(f"No snippet found with ID {snippet_id}.")
        raise typer.Exit(code=1)


@app.command()
@cleanup_db_resources
def delete(
    ctx: typer.Context,
    snippet_id: Annotated[int, typer.Argument(help="ID of snippet to delete")],
):
    """Delete a code snippet by its ID."""
    repo: DBSnippetRepo = ctx.obj["repo"]
    try:
        repo.delete(snippet_id)
        success_message(f"Snippet {snippet_id} is deleted.")
    except SnippetNotFoundError:
        error_message(f"Snippet {snippet_id} not found.")
        raise typer.Exit(code=1)


@app.command()
@cleanup_db_resources
def search(
    ctx: typer.Context,
    term: Annotated[
        str,
        typer.Argument(
            help="Term to search title, code, description and tag of snippets"
        ),
    ],
    language: Annotated[
        Language | None, typer.Option(help="Filter results by language")
    ] = None,
    fuzzy: Annotated[
        bool, typer.Option(help="Perform fuzzy search instead of strict matching")
    ] = False,
):
    """Search snippets by term with optional language filter and fuzzy matching."""
    repo: DBSnippetRepo = ctx.obj["repo"]
    try:
        results = repo.search(term, language=language, fuzzy=fuzzy)
        if results:
            for snippet in results:
                print_panel(snippet)
        else:
            error_message("No snippets found.")
    except ValueError as e:
        error_message(str(e))
        typer.Exit(code=1)


@app.command()
@cleanup_db_resources
def toggle_favorite(
    ctx: typer.Context,
    snippet_id: Annotated[int, typer.Argument(help="ID of snippet to toggle")],
):
    """Toggle the favorite status of a code snippet by its ID."""
    repo: DBSnippetRepo = ctx.obj["repo"]
    try:
        repo.toggle_favorite(snippet_id)
        snippet = repo.get(snippet_id)
        print_panel(snippet)
    except SnippetNotFoundError:
        error_message(f"Snippet {snippet_id} not found.")
        raise typer.Exit(code=1)


@app.command()
@cleanup_db_resources
def tag(
    ctx: typer.Context,
    snippet_id: Annotated[int, typer.Argument(help="ID of snippet to tag or untag")],
    tags: Annotated[List[str], typer.Argument(help="Tags to add or remove")],
    remove: Annotated[
        bool, typer.Option("--remove", help="Remove tag instead of adding")
    ] = False,
):
    """Add or remove tags from a code snippet by its ID."""
    repo: DBSnippetRepo = ctx.obj["repo"]
    try:
        repo.tag(snippet_id, *tags, remove=remove)
        snippet = repo.get(snippet_id)
        print_panel(snippet)
    except SnippetNotFoundError:
        error_message(f"Snippet {snippet_id} not found.")
        raise typer.Exit(code=1)


@app.command()
@cleanup_db_resources
def run(
    ctx: typer.Context,
    snippet_id: Annotated[int, typer.Argument(help="ID of the snippet to run")],
):
    """Wrapper to run the async runner with asyncio.run"""
    asyncio.run(_run(ctx, snippet_id))


async def _run(ctx: typer.Context, snippet_id: int):
    """Run the code of a snippet using the Piston API."""
    repo: DBSnippetRepo = ctx.obj["repo"]
    snippet = repo.get(snippet_id)
    if snippet is None:
        error_message(f"Snippet with ID {snippet_id} not found.")
        raise typer.Exit(1)

    print_panel(snippet)

    try:
        result = await run_code(snippet)
        print("\n[bold]Output:[/bold]")
        print(result.output)
    except RunCodeError as e:
        error_message(str(e))
        raise typer.Exit(1)


@app.command()
@cleanup_db_resources
def gist(
    ctx: typer.Context,
    snippet_id: Annotated[int, typer.Argument(help="ID of the snippet to export")],
    public: Annotated[
        bool, typer.Option("--public", help="Secret or public gist")
    ] = False,
):
    """Wrapper to run the async gister with asyncio.run"""
    asyncio.run(_gist(ctx, snippet_id, public))


async def _gist(ctx: typer.Context, snippet_id: int, public: bool):
    """Export a snippet as a gist."""
    repo: DBSnippetRepo = ctx.obj["repo"]
    snippet = repo.get(snippet_id)
    if snippet is None:
        error_message(f"Snippet with ID {snippet_id} not found.")
        raise typer.Exit(1)

    try:
        result = await create_gist(snippet, public)
        success_message(result.output)
    except GistCreationError as e:
        error_message(str(e))
        raise typer.Exit(1)
