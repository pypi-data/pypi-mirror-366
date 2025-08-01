import click
from pyHarm_cli.commands import project_admin
from pyHarm_cli.commands import project_add

@click.group()
@click.version_option(package_name='pyHarm-os')
def pyharm_cli() -> None:
    pass

@pyharm_cli.command(help="create a new pyHarm project")
@click.argument('project_name')
def new(project_name:str) -> None : 
    project_admin._new_project(project_name=project_name)
    pass

@pyharm_cli.command(help="check if project seems viable to be run")
@click.argument('project_name')
def check(project_name:str) -> None : 
    project_admin._check_if_project_viable(project_name=project_name, verbose=True)
    pass

@pyharm_cli.command(help="remove an existing pyHarm project")
@click.argument('project_name')
@click.option("--force", "-f", is_flag=True, help="Force the removal")
def remove(project_name:str, force:bool = False) -> None : 
    project_admin._remove_project(project_name=project_name, force_removal=force)
    pass

@pyharm_cli.command(help="update a pyHarm project lock file")
@click.argument('project_name')
def update(project_name:str) -> None : 
    project_admin._update_project_lock(project_name=project_name, force=True)
    pass

@pyharm_cli.command(help="add a file to track in a pyHarm project lock file")
@click.argument('project_name')
@click.argument('file_path')
def track(project_name:str, file_path:str) -> None : 
    project_admin._track_file(project_name=project_name, file_path=file_path)
    pass

@pyharm_cli.command(help="remove a file to track in a pyHarm project lock file")
@click.argument('project_name')
@click.argument('file_path')
def untrack(project_name:str, file_path:str) -> None : 
    project_admin._untrack_file(project_name=project_name, file_path=file_path)
    pass

@pyharm_cli.command(help="run a pyHarm project")
@click.argument('project_name')
@click.option("--verbose", "-v", is_flag=True, help="Add verbosity viable check")
@click.option("--force", "-f", is_flag=True, help="Force lock file update -- can lead to data loss")
def run(project_name:str, verbose:bool=False, force:bool=False) -> None : 
    project_admin._check_if_project_viable(project_name=project_name, verbose=verbose)
    project_admin._update_project_lock(project_name=project_name, force=force)
    project_admin._run_project(project_name=project_name)
    pass

@pyharm_cli.command(help="Make a jupyter notebook from the python script")
@click.argument('project_name')
@click.argument('export_type', type=click.Choice(list(project_admin.EXPORT_OPTIONS.keys())))
def export(project_name:str, export_type:str) -> None : 
    project_admin._export_project(project_name=project_name, export_type=export_type)
    pass

@pyharm_cli.command(help="Clear pyHarm project from all results")
@click.argument('project_name')
def clear(project_name:str) -> None : 
    project_admin._clear_results(project_name=project_name)
    pass

@pyharm_cli.command(help="Complete the input files with default classes settings a pyHarm project")
@click.argument('project_name')
@click.argument('cls', type=click.Choice(list(project_add.dict_filling.keys())))
@click.option("--type", "-t", help="Subclass of selected class")
@click.option("--name", "-n", help="Name to give instance of the class")
@click.option("--optional", "-o", is_flag=True, help="Add the optional arguments in the input files")
@click.option("--interactive", "-i", is_flag=True, help="Interactive filling of the class parameters")
def add(project_name:str, cls: str, type:str, name:str, optional:bool, interactive:bool) -> None :
    try :  
        object_type = project_add._select_cls_type(cls=cls, type=type)
        # object_cls = project_add.ADD_OPTIONS[cls][object_type]
        if not name : name=""
        project_add._complete_inputfiles(project_name=project_name, cls=cls, object_type=object_type, name=name, optional=optional, interactive=interactive)
    except KeyboardInterrupt:
        click.echo("\nOperation aborted by user.")
        raise  # Re-raise the exception to exit the program
    pass


if __name__ == "__main__":
    pyharm_cli()
