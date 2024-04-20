from invoke import task

from . import common


@task
def setup(context):
    """Set up git for working."""
    pre_commit(context)
    # https://wiki.saritasa.rocks/general/git/#fast-forward-merges
    context.run("git config --add merge.ff false")
    # https://wiki.saritasa.rocks/general/git/#auto-merged-pulls
    context.run("git config --add pull.ff only")


@task
def pre_commit(context):
    """Install git hooks via pre-commit."""
    common.success("Setting up pre-commit")
    hooks = " ".join(
        f"--hook-type {hook}" for hook in (
            "pre-commit",
            "pre-push",
            "commit-msg",
        )
    )
    context.run(f"pre-commit install {hooks}")


@task
def run_hooks(context):
    """Install git hooks."""
    common.success("Running git hooks")
    context.run("pre-commit run --hook-stage push --all-files")
