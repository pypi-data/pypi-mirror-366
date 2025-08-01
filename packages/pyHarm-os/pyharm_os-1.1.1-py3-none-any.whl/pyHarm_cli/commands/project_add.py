import click
import json

from ._project_handler import _project_is_pyHarm
from ._commands_variables import SYSTEM_FILE_NAME, ANALYSIS_FILE_NAME

from pyHarm_cli.parameters.pck_substructures import param_substructures
from pyHarm_cli.parameters.pck_kinematic import param_kinematic
from pyHarm_cli.parameters.pck_connectors import param_connectors
from pyHarm_cli.parameters.pck_analysis import param_analysis
from pyHarm_cli.parameters.pck_systems import param_systems
from pyHarm_cli.parameters.pck_export import param_export
from pyHarm_cli.parameters.BaseParam import BaseParam
from dataclasses import dataclass

@dataclass
class fillingCLS():
    file_to_add: str
    json_category: str
    list_param: dict[str:list[BaseParam]]

sub_filling = fillingCLS(file_to_add=SYSTEM_FILE_NAME, json_category='substructures', list_param=param_substructures)
kin_filling = fillingCLS(file_to_add=SYSTEM_FILE_NAME, json_category='kinematics', list_param=param_kinematic)
ele_filling = fillingCLS(file_to_add=SYSTEM_FILE_NAME, json_category='connectors', list_param=param_connectors)
ana_filling = fillingCLS(file_to_add=ANALYSIS_FILE_NAME, json_category='analysis', list_param=param_analysis)
sys_filling = fillingCLS(file_to_add=SYSTEM_FILE_NAME, json_category='system', list_param=param_systems)
export_filling = fillingCLS(file_to_add=ANALYSIS_FILE_NAME, json_category='export', list_param=param_export)
dict_filling = dict(
    substructure = sub_filling,
    kinematic = kin_filling,
    connector = ele_filling,
    analysis = ana_filling,
    system = sys_filling,
    export = export_filling
)

_direct_fill = ['system', 'export']

def _select_cls_type(cls: str, type:str) -> str: 
    cls_types_choices = list(dict_filling[cls].list_param.keys()) # extract the possibilities for the cls chosen
    if type not in cls_types_choices : # if --type provide not in the possibilities -> ask for proper prompt
        # Prompt the user to select an object type
        prompt_with_choices = "".join(
            [f"Select the type of '{cls}' to add:\n"] + 
            [
                f"    - {i} : {cls_poss}\n" for i,cls_poss in enumerate(cls_types_choices)
            ]
        )
        object_type_selection = click.prompt(
            prompt_with_choices,
            type=int
        )
        object_type = cls_types_choices[object_type_selection]
    else : 
        object_type = type
    return object_type

def _read_input_file(project_name:str, file_name:str) -> dict : 
    with open(f"{project_name}/{file_name}", 'r', encoding='utf-8') as file : 
        system_data = json.load(file)
    return system_data

def _write_input_file(project_name:str, file_name:str, cls:str, object_type:str, name:str, param_list: list[BaseParam], optional:bool=False, interactive:bool=False) :
    data = _read_input_file(project_name=project_name, file_name=file_name)
    if not cls in _direct_fill : 
        cls_name = dict_filling[cls].json_category
        data_cls = data[cls_name]
        if name=="" : 
            N = 0
            while f"{object_type}_{N:02d}" in list(data_cls.keys()) : 
                N += 1
            name = f"{object_type}_{N:02d}"
        data[cls_name][name] = dict()
        for param in param_list : 
            if (not param.optional) or ((param.optional) and (optional)) : 
                data[cls_name][name][param.name] = param.default
    else : 
        if cls in _direct_fill :
            for param in param_list : 
                if (not param.optional) or ((param.optional) and (optional)) : 
                    data[cls][param.name] = param.default

    with open(f"{project_name}/{file_name}", 'w', encoding='utf-8') as file : 
        json.dump(data, file, indent=4)

def _complete_inputfiles(project_name:str, cls:str, object_type:str, name:str="", optional:bool=False, interactive:bool=False) : 
    param_list = dict_filling[cls].list_param[object_type]
    file = dict_filling[cls].file_to_add
    _write_input_file(project_name=project_name, file_name=file, cls=cls, object_type=object_type, name=name, param_list=param_list, optional=optional, interactive=interactive)
