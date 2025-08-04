import subprocess
from importlib.metadata import PackageNotFoundError, version


def get_version() -> str:
    """Get the version of the package."""
    try:
        return version("furiosa-models-lang")
    except PackageNotFoundError:
        try:
            git_hash = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], encoding="utf-8"
            ).strip()
            return f"0.0.0+{git_hash}"
        except Exception:
            return "0.0.0+local"
