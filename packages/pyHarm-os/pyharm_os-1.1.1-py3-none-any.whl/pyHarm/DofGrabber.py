# Copyright 2024 SAFRAN SA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module gives some functions that allow for grabbing specific dofs from the explicit dof dataFrame built by the system"""
import pandas as pd
import numpy as np


################################ NODE GRABBERS FROM THE EXPLICIT DATAFRAME
def sub_grabber(edf:pd.DataFrame, sub:str, **kwargs) -> pd.Index : 
    """
    Grab indices from the explicit dof DataFrame based on the substructure.

    Args:
        edf (pd.DataFrame): The explicit dof DataFrame.
        sub (str): The substructure identifier.
        **kwargs: Additional keyword arguments.

    Returns:
        pd.Index: The indices corresponding to the specified substructure.
    """
    Indices = edf[
            (edf['sub']==sub)
            ].index
    return Indices

def node_grabber(edf:pd.DataFrame, sub:str|None, node:int|None, **kwargs) -> pd.Index : 
    """
    Grab indices from the explicit dof DataFrame based on the substructure and node number.

    Args:
        edf (pd.DataFrame): The explicit dof DataFrame.
        sub (str | None): The substructure identifier.
        node (int | None): The node number.
        **kwargs: Additional keyword arguments.

    Returns:
        pd.Index: The indices corresponding to the specified substructure and node number.
    """
    Indices = edf[
            (edf['sub']==sub) &
            (edf['node_num']==node)
            ].index
    return Indices

def list_node_grabber(edf:pd.DataFrame, sub:str|None, node:list[int]|None, **kwargs) -> pd.Index : 
    """
    Grab indices from the explicit dof DataFrame based on the substructure and a list of node numbers.

    Args:
        edf (pd.DataFrame): The explicit dof DataFrame.
        sub (str | None): The substructure identifier.
        node (list[int] | None): The list of node numbers.
        **kwargs: Additional keyword arguments.

    Returns:
        pd.Index: The indices corresponding to the specified substructure and list of node numbers.
    """
    Indices = edf[
            (edf['sub']==sub) &
            (edf['node_num'].isin(node))
            ].index
    return Indices

def dof_grabber(edf:pd.DataFrame, sub:str|None, node:int|None, dof:int|None, **kwargs) -> pd.Index : 
    """
    Grab indices from the explicit dof DataFrame based on the substructure, node number, and dof number.

    Args:
        edf (pd.DataFrame): The explicit dof DataFrame.
        sub (str | None): The substructure identifier.
        node (int | None): The node number.
        dof (int | None): The dof number.
        **kwargs: Additional keyword arguments.

    Returns:
        pd.Index: The indices corresponding to the specified substructure, node number, and dof number.
    """
    Indices = edf[
            (edf['sub']==sub) &
            (edf['node_num']==node) &
            (edf['dof_num']==dof)
            ].index
    return Indices

def harm_grabber(edf:pd.DataFrame, harm:int|None, **kwargs) -> pd.Index :
    """
    Grab indices from the explicit dof DataFrame based on the harmonic number.

    Args:
        edf (pd.DataFrame): The explicit dof DataFrame.
        harm (int | None): The harmonic number.
        **kwargs: Additional keyword arguments.

    Returns:
        pd.Index: The indices corresponding to the specified harmonic number.
    """ 
    Indices = edf[
            (edf['harm']==harm)
            ].index
    return Indices

def harm_cs_grabber(edf:pd.DataFrame, harm:int|None, cs:str|None, **kwargs) -> pd.Index : 
    """
    Grab indices from the explicit dof DataFrame based on the harmonic number and cosine or sine part.

    Args:
        edf (pd.DataFrame): The explicit dof DataFrame.
        harm (int | None): The harmonic number.
        cs (str | None): either cosine or sine part.
        **kwargs: Additional keyword arguments.

    Returns:
        pd.Index: The indices corresponding to the specified harmonic number and cosine or sine part.
    """
    Indices = edf[
            (edf['harm']==harm) &
            (edf['cs']==cs)
            ].index
    return Indices

################################ GRABS THE DOFS RETURN INDEXES AND TRANFORMATION MATRICES
def gen_NodeToNode_select_matrix(edf:pd.DataFrame, input_dict:dict, **kwargs) -> tuple[np.ndarray, list[np.ndarray]] :
    """
    Generate a selection matrix for NodeToNode type of connectors -- Pslave, Pmaster

    Args:
        edf (pd.DataFrame): The explicit dof DataFrame.
        input_dict (dict): The input dictionary containing connection information.
        **kwargs: Additional keyword arguments.

    Returns:
        np.ndarray: indices of the dof conserned from the explicit dof DataFrame.
        list[np.ndarray]: The selection matrix for NodeToNode transformation.
    """
    Lgrabs = _transform_input_for_grabber(input_dict)
    LIndex = [node_grabber(edf, **grab) for grab in Lgrabs]

    UIndex = _recursive_union_of_Index(LIndex)
    indices = np.array(UIndex)

    edf_sel = edf.loc[UIndex]
    edf_sel = edf_sel.assign(local_index=np.arange(len(edf_sel)))

    LPmat = []
    col_size = len(edf_sel)
    lin_size_00 = len(LIndex[0]) # Slave node is the reference size
    for grab, Index in zip(Lgrabs, LIndex) : 
        if grab['sub'] == 'GROUND' : lin_size = lin_size_00
        else : lin_size = len(Index)
        Pmat = np.zeros((lin_size,col_size))
        if not Index.empty:
            Pmat[
                    np.arange(lin_size),
                    np.array(edf_sel.loc[Index]['local_index'])
            ] = 1
        LPmat.append(Pmat)
    return indices, LPmat

################################ SOME HELPER FUNCTION TO TREAT INPUT DICT INPUT EASIER FORMAT
def _is_connect_type_legacy(_connect:dict[str,list] | list[tuple[str,list[int]]]) -> bool :
    _legacy = False 
    if isinstance(_connect, dict) : _legacy = True 
    return _legacy

def _transform_legacy(_connect:dict[str,list]) -> list[dict[str,int]]:
    Lgrabs = []
    if len(_connect) == 1 : _connect['GROUND'] = list(_connect.values())[0]
    for _sub,_Lnode in _connect.items():
        if _sub == 'INTERNAL' :  sub=prev_sub; Lnode = _Lnode
        elif _sub == 'GROUND' : sub='GROUND'; Lnode=[None]
        else : sub=_sub; Lnode=_Lnode
        Lgrabs.append(
            dict(
                sub=sub,
                node=Lnode[0]
            )
        )
        prev_sub = sub
    return Lgrabs

def _transform_new(_connect:list[tuple[str,list[int]]]) -> list[dict[str,int]]:
    Lgrabs = []
    for _sub,_Lnode in _connect : 
        if _sub == 'GROUND' :  sub='GROUND'; Lnode = [None]
        else : sub=_sub; Lnode=_Lnode
        Lgrabs.append(
            dict(
                sub=sub,
                node=Lnode[0]
            )
        )
        prev_sub = sub
    return Lgrabs

def _transform_input_for_grabber(input_dict:dict) -> list[dict[str,int]]:
    _connect = input_dict.get("connect")
    _legacy:bool = _is_connect_type_legacy(_connect)
    if _legacy : Lgrabs = _transform_legacy(_connect)
    else : Lgrabs = _transform_new(_connect)
    return Lgrabs

def _recursive_union_of_Index(LI:list[pd.Index]):
    if len(LI) == 1 : return LI[0]
    else : return LI[0].union(_recursive_union_of_Index(LI[1:]))
