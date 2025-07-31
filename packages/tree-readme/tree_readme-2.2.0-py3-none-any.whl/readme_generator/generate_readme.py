from pathlib import Path
import typer
from typing_extensions import Annotated
from readme_generator.readme_builder import build_readme


def generate(
    repo_path: Annotated[
        str,
        typer.Option(
            help="Ścieżka do repozytorium.",
        ),
    ] = "",
    overview: Annotated[
        str,
        typer.Option(
            help="Tekst wprowadzający do README.",
        ),
    ] = "",
    exclude_dirs: Annotated[
        list[str],
        typer.Option(
            help="Katalogi do wykluczenia z drzewa folderów. Może być użyte wielokrotnie.",
            show_default=False,
            rich_help_panel="Opcje drzewa folderów",
        ),
    ] = [],
    exclude_files: Annotated[
        list[str],
        typer.Option(
            help="Rozszerzenia plików do wykluczenia z drzewa folderów. Może być użyte wielokrotnie.",
            show_default=False,
            rich_help_panel="Opcje drzewa folderów",
        ),
    ] = [],
) -> None:
    """
    Generuj README.md dla repozytorium.

    Args:
        repo_path (str): Ścieżka do repozytorium.
        overview (str): Tekst wprowadzający do README.
        exclude_dirs (list[str]): Katalogi do wykluczenia z drzewa folderów.
        exclude_files (list[str]): Pliki do wykluczenia z drzewa folderów.
    """
    if not repo_path:
        repo_path = str(Path.cwd())
    readme_content = build_readme(
        repo_path,
        overview_text=overview,
        exclude_dirs=set(exclude_dirs),
        exclude_files=set(exclude_files),
    )
    readme_path = Path(repo_path) / "README.md"
    if readme_path.exists():
        try:
            typer.echo(
                f"⚠️ README.md już istnieje w podanej ścieżce {readme_path.resolve()}. Zapisywanie jako README_generated.md."
            )
        except:
            typer.echo(
                f"WARNING: README.md już istnieje w podanej ścieżce {readme_path.resolve()}. Zapisywanie jako README_generated.md."
            )
        readme_path = readme_path.with_name("README_generated.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    try:
        typer.echo(
            f"✅ {readme_path.name} zostało wygenerowane w ścieżce {readme_path.resolve()}"
        )
    except:
        typer.echo(
            f"{readme_path.name} wygenerowane w ścieżce {readme_path.resolve()}."
        )


if __name__ == "__main__":
    typer.run(generate)
