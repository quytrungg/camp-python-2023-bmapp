from pathlib import Path

from invoke import task

from . import common

FRONTEND_REPO_NAME = "camp-python-2023-bmapp"
FRONTEND_REPO_PATH = Path(f"../{FRONTEND_REPO_NAME}")
FRONTEND_REPO_LINK = f"git@github.com:saritasa-nest/{FRONTEND_REPO_NAME}.git"


@task
def npm(context, command, frontend_repo_path=FRONTEND_REPO_PATH):
    """Call `npm` inside frontend dir with passed command."""
    with context.cd(frontend_repo_path):
        context.run(f"npm {command}")


@task
def clone_repo(
    context,
    frontend_repo_link=FRONTEND_REPO_LINK,
    frontend_repo_path=FRONTEND_REPO_PATH,
):
    """Clone repository with frontend."""
    if not frontend_repo_path.exists():
        common.success("Cloning frontend repository...")
        context.run(f"git clone {frontend_repo_link} {frontend_repo_path}")
        common.success(f"Successfully cloned to '{FRONTEND_REPO_PATH}'!")
    else:
        common.success("Pulling changes...")
        with context.cd(frontend_repo_path):
            context.run("git pull")


def install_dependencies(
    context,
    frontend_repo_path: Path,
    clean_build: bool,
):
    """Install frontend dependencies via `npm ci`.

    `clean_build` param allows to choose strategy of updating dependencies. If
    True use `npm ci` otherwise use `npm install`

    """
    common.success("Installing frontend dependencies...")
    command = "ci" if clean_build else "install"
    npm(context, command=command, frontend_repo_path=frontend_repo_path)


def create_env_file(frontend_repo_path: Path, backend_port: int) -> None:
    """Set up .env file for frontend.

    Set both `NG_APP_API_URL` and `REACT_APP_API_URL` to work with both the
    Angular/React framework in different projects. `VITE_API_URL` is required
    for React projects.

    """
    common.success("Creating env file...")
    env_file = Path(frontend_repo_path) / ".env.development.local"
    possible_framework_prefixes = ("NG_APP", "REACT_APP", "VITE")
    backend_api_url_env_vars = (
        f"{prefix}_API_URL='http://localhost:{backend_port}/api/v1/'"
        for prefix in possible_framework_prefixes
    )
    env_file.write_text("\n".join(backend_api_url_env_vars))


def prepare_frontend_dir(
    context,
    frontend_repo_path: Path,
    backend_port: int,
    clean_build: bool,
) -> None:
    """Prepare dir with frontend app for running."""
    common.success("Preparing frontend directory...")
    clone_repo(
        context,
        frontend_repo_link=FRONTEND_REPO_LINK,
        frontend_repo_path=frontend_repo_path,
    )
    install_dependencies(context, frontend_repo_path, clean_build)
    create_env_file(frontend_repo_path, backend_port)


@task
def run(
    context,
    frontend_repo_path=FRONTEND_REPO_PATH,
    backend_port=8000,
    rebuild=True,
    clean_build=True,
):
    """Run frontend locally.

    Use `--no-rebuild` param to just run `npm start` without reinstalling
    dependencies. Use `--no-clean-build` to use `npm install` instead of `npm
    ci` during installing node packages.

    """
    if rebuild:
        prepare_frontend_dir(
            context,
            frontend_repo_path,
            backend_port,
            clean_build,
        )

    npm(context, command="start", frontend_repo_path=frontend_repo_path)
