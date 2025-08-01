"""
This module contains usefull functions to discriminate if a project is a pyHarm project or not.
"""

import os
from pyHarm_cli.commands._commands_variables import LOCK_FILE_NAME

def _project_exists(project_name: str) -> bool :
    """Check if a folder under the provided project name already exists in the worksapce.
    
    Args:
        project_name (str): Name of the project.
    
    Returns:
        bool: True if folder name is taken.
    """
    is_folder_name_taken = False
    if os.path.exists(project_name) : is_folder_name_taken=True
    return is_folder_name_taken



def _project_is_pyHarm(project_name: str) -> tuple[bool] :
    """Check if the folder name provided is already taken and if so check if the folder is a pyHarm project by checking if the lock file is present.
    
    Args:
        project_name (str): Name of the project.
    
    Returns:
        bool: True if folder name is taken.
        bool: True if folder name is a pyharm project.
    """
    is_folder_name_taken = _project_exists(project_name)
    is_name_pyHarm = False
    if is_folder_name_taken : 
        pyHarm_lock_file = os.path.join(project_name, LOCK_FILE_NAME)
        if os.path.exists(pyHarm_lock_file) : is_name_pyHarm=True
    return is_folder_name_taken, is_name_pyHarm

