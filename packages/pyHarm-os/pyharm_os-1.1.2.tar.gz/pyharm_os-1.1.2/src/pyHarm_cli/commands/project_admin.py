"""
This module contains functions and logic that are used in order to craete, remove or run a pyHarm project
"""
import click
import pyHarm
import os
import sys
import shutil
import subprocess
import json
from ._project_handler import _project_is_pyHarm
from ._lock_file_handler import _new_lock_file, _hash_template_files
import importlib.resources
import pyHarm_cli.templates
from ._commands_variables import RUN_FILE_NAME
import nbformat as nbf
from nbformat.v4 import new_markdown_cell, new_code_cell
from .project_add import _read_input_file

def _create_pyharm_files(project_name: str) -> None : 
    # Copy each template file to the project directory
    template_package = importlib.resources.files(pyHarm_cli.templates)
    template_files = []
    for template_file in template_package.iterdir():
        if template_file.is_file():
            dest_file = os.path.join(project_name, template_file.name)
            template_files.append(dest_file)
            with importlib.resources.as_file(template_file) as src_file:
                shutil.copy2(src_file, dest_file)
    hash_dict = _hash_template_files(template_files)
    _new_lock_file(project_name, hash_dict)
    pass


def _new_project(project_name:str) -> None : 
    is_taken, is_pyHarm = _project_is_pyHarm(project_name=project_name)
    if not is_taken : 
        os.makedirs(project_name)
        _create_pyharm_files(project_name=project_name)
        click.echo(f"Project '{project_name}' has been created successfully")
    else : 
        click.echo(f"Error : project name '{project_name}' already taken")
        raise click.Abort()

def _remove_project(project_name:str, force_removal:bool=False) -> None : 
    is_taken, is_pyHarm = _project_is_pyHarm(project_name=project_name)
    if is_pyHarm : 
        if force_removal : 
            shutil.rmtree(project_name)
        else : 
            # here need to implement logic in order to avoid removal of results ...
            shutil.rmtree(project_name) 
        click.echo(f"Project '{project_name}' has been removed successfully")
    elif (is_taken) and (not is_pyHarm) : 
        click.echo(f"Error : directory '{project_name}' is not a pyharm project as no 'pyharm.lock' file could be found")
        raise click.Abort()
    else :
        click.echo(f"Error : directory '{project_name}' could not be found in the workspace")
        raise click.Abort()

def _check_if_project_is_pyharm(project_name: str) -> None:
    is_taken, is_pyHarm = _project_is_pyHarm(project_name=project_name)
    if not is_pyHarm : 
        click.echo(f"Error: Project '{project_name}' is not a valid pyHarm project.")
        raise click.Abort()

def _check_if_project_viable(project_name: str, verbose:bool=False) -> None:
    _check_if_project_is_pyharm(project_name=project_name)
    system_data = _read_input_file(project_name=project_name, file_name='system.json')
    analysis_data = _read_input_file(project_name=project_name, file_name='analysis.json')
    def click_echo(message:str, verbose:bool) -> None :
        if verbose : click.echo(message)
    viable = True
    # check is sytem is filled
    if len(system_data['system']) == 0 : 
        click_echo(f"Error: Project '{project_name}' is missing \'system\' \
                   parametrization -- consider using command \'pyharm add {project_name} system\'.", verbose=verbose)
        viable = False
    # check is substructure is filled
    if len(system_data['substructures']) == 0 : 
        click_echo(f"Error: Project '{project_name}' needs at least a \'substructure\' \
                   parametrization -- consider using command \'pyharm add {project_name} substructure\'.", verbose=verbose)
        viable = False
    # check is substructure is filled
    if len(analysis_data) == 0 : 
        click_echo(f"Warning: Project '{project_name}' does not have an \'analysis\' \
                   parametrization -- consider using command \'pyharm add {project_name} analysis to perform an analysis on your system\'.", verbose=verbose)
        viable = False
    if viable : click_echo(f"Project '{project_name}' seems viable for running", verbose=verbose)
    pass


def _check_update_project_lock(project_name: str) -> tuple[bool,str,dict[str:str]]:
    is_taken, is_pyHarm = _project_is_pyHarm(project_name=project_name)
    if not is_pyHarm : 
        click.echo(f"Error: Project '{project_name}' is not a valid pyHarm project.")
        raise click.Abort()

    lock_file_path = os.path.join(project_name, 'pyharm.lock')

    # Read the existing lock file
    with open(lock_file_path, 'r', encoding='utf-8') as lock_file:
        file_hashes = json.load(lock_file)# Check and update hashes
    
    lock_updated = False
    tracked_files = list(file_hashes.keys())
    new_hashes = _hash_template_files(tracked_files)
    for file_path in tracked_files:
        current_hash = new_hashes[file_path]
        stored_hash = file_hashes[file_path]
        if current_hash != stored_hash:
            click.echo(f"File '{file_path}' has been modified.")
            file_hashes[file_path] = current_hash
            lock_updated = True
    return lock_updated, lock_file_path, file_hashes

def _update_project_lock_force(project_name: str, lock_updated:bool, lock_file_path:str, file_hashes:dict[str:str], force:bool=False) -> None:
    # Write the updated lock file if necessary
    if ((not force) and lock_updated) : 
        click.echo(f"Error: Project has been modified without updating the lock file.\n\
                   update manually or run it with --force option in order to force update but this might result in loosing data.")
        raise click.Abort()
    elif lock_updated:
        with open(lock_file_path, 'w', encoding='utf-8') as lock_file:
            json.dump(file_hashes, lock_file, indent=4)
        click.echo("Lock file has been updated.")
    else:
        click.echo("All tracked files are up to date. No changes to the lock file.")

def _update_project_lock(project_name: str, force:bool=False) -> None:
    lock_updated, lock_file_path, file_hashes = _check_update_project_lock(project_name=project_name)
    _update_project_lock_force(project_name=project_name, lock_updated=lock_updated, lock_file_path=lock_file_path, file_hashes=file_hashes, force=force)


def _run_project(project_name: str) -> None:
    # Define the path to the project directory
    project_dir =f"./{project_name}"
    is_taken, is_pyHarm = _project_is_pyHarm(project_name=project_name)
    # a check of the lock is necessary here
    if not is_pyHarm : 
        click.echo(f"Error : directory '{project_name}' is not a pyharm project as no 'pyharm.lock' file could be found")
        raise click.Abort()
    
    # Change the current working directory to the project directory
    os.chdir(project_dir)

    try:
        # Run the pyHarm_run.py script as a subprocess
        result = subprocess.run([sys.executable, RUN_FILE_NAME], check=True)
        print(f"Script executed successfully with return code {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Script execution failed with return code {e.returncode}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def _notebook_creation(project_name:str) -> None:
    python_script_file_path = os.path.join(project_name, 'pyHarm_run.py')
    # Read the existing python script file
    with open(python_script_file_path, 'r', encoding='utf-8') as python_script:
        pyscript = python_script.read()

    code_blocks = pyscript.split('######################')[1:-1]

    nb = nbf.v4.new_notebook()

    # Add a markdown cell with the project name
    nb.cells.append(new_markdown_cell(f"# pyHarm {project_name} project notebook"))

    # Add code cells for each block
    for block in code_blocks:
        code = block.strip()
        if code:
            nb.cells.append(new_code_cell(code))

    nb.cells.append(
        new_code_cell(
            """maestro = pyHarm.Maestro(input_dict)\nmaestro.operate()"""
        )
    )

    # Write the notebook to file
    notebook_file = os.path.join(project_name, 'pyHarm_notebook.ipynb')
    nbf.write(nb, notebook_file)
    pass


EXPORT_OPTIONS = dict(
        notebook=_notebook_creation,
    )


def _export_project(project_name:str, export_type:str) -> None:
    return EXPORT_OPTIONS[export_type](project_name=project_name)


def _clear_results(project_name:str) -> None:
    _check_if_project_is_pyharm(project_name)
    # List all items in the project directory
    for item in os.listdir(project_name):
        item_path = os.path.join(project_name, item)
        # Check if the item is a directory and its name starts with '_results_'
        if os.path.isdir(item_path) and item.startswith('_results'):
            try:
                # Remove the directory and all its contents
                shutil.rmtree(item_path)
            except Exception as e:
                click.echo(f"Error: Unable to remove directory {item_path}: {e}")
    click.echo(f"Project '{project_name}' results have been cleared")

def _track_file(project_name:str, file_path:str):
    _check_if_project_is_pyharm(project_name)

    lock_file_path = os.path.join(project_name, 'pyharm.lock')
    track_file = os.path.join(project_name, file_path)

    # Read the existing lock file
    with open(lock_file_path, 'r', encoding='utf-8') as lock_file:
        file_hashes = json.load(lock_file)# Check and update hashes

    if track_file in list(file_hashes.keys()) : 
        click.echo(f"Error: file {file_path} is already tracked")
        raise click.Abort()

    file_hashes = file_hashes | _hash_template_files(template_files=[track_file])
    click.echo(f"File {file_path} is now tracked in the pyharm.lock file")

    with open(lock_file_path, 'w', encoding='utf-8') as lock_file:
        json.dump(file_hashes, lock_file, indent=4)
    pass

def _untrack_file(project_name:str, file_path:str):
    _check_if_project_is_pyharm(project_name)

    lock_file_path = os.path.join(project_name, 'pyharm.lock')
    untrack_file = os.path.join(project_name, file_path)

    # Read the existing lock file
    with open(lock_file_path, 'r', encoding='utf-8') as lock_file:
        file_hashes = json.load(lock_file)# Check and update hashes

    if untrack_file not in list(file_hashes.keys()) : 
        click.echo(f"Error: file {untrack_file} is not tracked")
        click.echo(f"tracked files are the following {list(file_hashes.keys())}")
        raise click.Abort()

    _ = file_hashes.pop(untrack_file)
    click.echo(f"File {file_path} is now untracked from the pyharm.lock file")

    with open(lock_file_path, 'w', encoding='utf-8') as lock_file:
        json.dump(file_hashes, lock_file, indent=4)
    pass


