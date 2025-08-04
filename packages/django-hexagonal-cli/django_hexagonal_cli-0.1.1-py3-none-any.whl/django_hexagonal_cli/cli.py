import django
import subprocess
import sys
from pathlib import Path


DJANGO_SHORT_VERSION = ".".join(django.get_version().split(".")[:2])
PYTHON_SHORT_VERSION = ".".join(sys.version.split()[0].split(".")[:2])

VAR_REPLACEMENTS = {
    "__django_version__": DJANGO_SHORT_VERSION,
    "__python_version__": PYTHON_SHORT_VERSION,
}


def replace_vars_in_path(path: Path, replacements: dict):
    """Replace variables in a file with given replacements."""
    for file in path.rglob("*"):
        if file.is_file():
            content = file.read_text()
            for old, new in replacements.items():
                content = content.replace(old, new)
            file.write_text(content)


def remove_tpl_suffix(path: Path):
    """Remove '-tpl' suffix from files in the given path."""
    for file in path.rglob("*-tpl"):
        new_name = file.name.replace("-tpl", "")
        new_file = file.with_name(new_name)
        file.rename(new_file)


def create_project(project_name, template_path):
    """Create a Django project with the specified name and template."""
    project_path = Path(project_name)
    subprocess.run(
        [
            "django-admin",
            "startproject",
            project_name,
            f"--template={template_path}",
            f"--extension=tpl,md-tpl,toml-tpl",
        ]
    )
    remove_tpl_suffix(project_path)
    replace_vars_in_path(project_path, VAR_REPLACEMENTS)


def create_app(app_name, project_path, template_path):
    """Create a Django app with the specified name and template."""
    apps_path = Path(project_path) / "src" / "apps"
    app_path: Path = apps_path / app_name
    app_path.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "django-admin",
            "startapp",
            app_name,
            str(apps_path / app_name),
            f"--template={template_path}",
        ]
    )

    replace_vars_in_path(app_path, VAR_REPLACEMENTS)


def main():
    args = sys.argv[1:]

    if not args:
        subprocess.run(["django-admin"])
        return

    command = args[0]

    project_template = Path(__file__).parent / "templates" / "project"
    app_template = Path(__file__).parent / "templates" / "app"

    if command == "startproject":
        if len(args) == 2:
            project_name = args[1]
            create_project(project_name, project_template.resolve())
            return
        elif len(args) == 3:
            project_name, app_name = args[1], args[2]
            create_project(project_name, project_template.resolve())
            create_app(app_name, project_name, app_template.resolve())
            return
    elif command == "startapp":
        app_name = args[1]
        create_app(app_name, Path.cwd(), app_template.resolve())
        return

    subprocess.run(["django-admin"] + args)
