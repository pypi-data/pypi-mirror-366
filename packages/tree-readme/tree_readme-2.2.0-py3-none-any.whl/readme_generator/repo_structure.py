from pathlib import Path

from readme_generator.emoji_map import get_emoji

DEFAULT_EXCLUDE_DIRS: set[str] = {
    ".git",
    "__pycache__",
    ".idea",
    ".vscode",
    ".ipynb_checkpoints",
    ".egg-info",
    "dist",
    "_env",
    ".pytest_cache",
}
DEFAULT_EXCLUDE_FILES: set[str] = {".pyc", ".pyo", ".pyd", ".DS_Store"}


def walk_repo(
    root_dir: str,
    exclude_dirs: set[str] = None,
    exclude_files: set[str] = None,
    tree_style: bool = False,
) -> tuple[Path, str, str]:
    """
    Unified repository walker that yields items in the desired format.

    Args:
        root_dir (str): Path to root directory.
        exclude_dirs (set[str]): Directories to exclude.
        exclude_files (set[str]): Files to exclude.
        tree_style (bool): Whether to generate tree-style output.

    Yields:
        Tuple of (path, formatted_line, indent)
    """
    exclude_dirs = (exclude_dirs or set()) | DEFAULT_EXCLUDE_DIRS
    exclude_files = (exclude_files or set()) | DEFAULT_EXCLUDE_FILES
    root_path = Path(root_dir)

    def _walk(
        dir_path: Path, indent: str = "", is_last_stack: list[bool] = None
    ) -> tuple[Path, str, str]:
        """
        Recursive function to walk through the directory structure.

        Args:
            dir_path (Path): Current directory path.
            indent (str): Current indentation level.
            is_last_stack (list[bool]): Stack to track the last item in the current level.

        Yields:
            Tuple of (path, formatted_line, indent)
        """
        if is_last_stack is None:
            is_last_stack = []

        items = sorted(
            [
                p
                for p in dir_path.iterdir()
                if p.name.endswith(tuple(exclude_files)) is False
                and p.name.endswith(tuple(exclude_dirs)) is False
            ],
            key=lambda x: (not x.is_dir(), x.name.lower()),
        )

        for i, path in enumerate(items):
            is_last = i == len(items) - 1
            emoji = get_emoji(path)

            if tree_style:
                prefix = "┗━ " if is_last else "┣━ "
                new_indent = indent + ("   " if is_last else "┃  ")
                line = f"{indent}{prefix}{emoji} {path.name}"
            else:
                if indent == "":
                    new_indent = indent + "\t"
                    line = f"* {emoji} `{path.name}`:"
                else:
                    new_indent = indent + "\t"
                    line = f"{indent}- {emoji} `{path.name}`:"

            yield path, line, indent

            if path.is_dir():
                if tree_style and not any(
                    p
                    for p in path.iterdir()
                    if not (
                        p.name.endswith(tuple(exclude_dirs))
                        or p.name.endswith(tuple(exclude_files))
                    )
                ):
                    yield path, f"{new_indent}┗━ ...", new_indent
                else:
                    yield from _walk(path, new_indent, is_last_stack + [is_last])

    yield from _walk(root_path)
