import sys
from pathlib import Path
from typing import Any
import importlib.resources as pkg_resources
from agent_handler_sdk import __version__ as sdk_version

# Use str() to convert Traversable to string path
TEMPLATE_DIR = Path(str(pkg_resources.files("agent_handler_sdk"))) / "templates" / "connector"


def get_sdk_version() -> str:
    return sdk_version


def render_template(filename: str, **context: Any) -> str:
    """
    Load a template file from the SDK's templates/connector directory
    and format it with the given context.
    """
    template_path = TEMPLATE_DIR.joinpath(filename)
    text = template_path.read_text()
    return text.format(**context)


def scaffold_connector() -> int:
    """
    Usage: ahs-scaffold <slug> [--target-dir <dir>]

    Creates:
      <target-dir>/connectors/<slug>/
        pyproject.toml
        metadata.yaml
        <slug>_connector/
          __init__.py
          tools/
            handlers.py
        tests/
          test_handlers.py
    """
    args = sys.argv[1:]
    if not args:
        print(scaffold_connector.__doc__)
        sys.exit(1)

    slug = args[0]
    # Generate human-readable name by replacing hyphens with spaces and capitalizing words
    human_readable_name = " ".join(word.capitalize() for word in slug.replace("-", " ").split())
    target = Path(".")
    if "--target-dir" in args:
        idx = args.index("--target-dir")
        target = Path(args[idx + 1])

    version = get_sdk_version()

    base = target / "connectors" / slug
    pkg_dir = base / f"{slug}_connector"
    tools_dir = pkg_dir / "tools"
    tests_dir = base / "tests"
    evals_dir = base / "evals"

    # Create directories
    for d in (base, pkg_dir, tools_dir, tests_dir, evals_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Map template → output path
    files_to_render = {
        "pyproject.toml.tpl": base / "pyproject.toml",
        "metadata.yaml.tpl": base / "metadata.yaml",
        "init.py.tpl": pkg_dir / "__init__.py",
        "handlers.py.tpl": tools_dir / "handlers.py",
        "test_handlers.py.tpl": tests_dir / "test_handlers.py",
        "evals.json.tpl": evals_dir / "evals.json",
        "README.md.tpl": base / "README.md",
    }

    # Render each template with both name & version
    for tpl_name, out_path in files_to_render.items():
        content = render_template(tpl_name, name=slug, version=version, human_readable_name=human_readable_name)
        out_path.write_text(content, encoding="utf-8")

    print(f"Scaffolded connector '{slug}' (SDK v{version}) at {base}")
    return 0
