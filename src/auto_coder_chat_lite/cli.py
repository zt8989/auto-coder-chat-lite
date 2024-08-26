import os
import shutil
import click

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates', 'project_template')

@click.command()
@click.argument('project_name')
def create_project(project_name):
    """Create a new project with the given name."""
    if os.path.exists(project_name):
        click.echo(f"Error: The directory '{project_name}' already exists.")
        return

    shutil.copytree(TEMPLATE_DIR, project_name)
    click.echo(f"Created project '{project_name}' successfully.")

if __name__ == '__main__':
    create_project()
