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

"""
This module contains the basic NodeToNodeElement class being a abstract class derived from the ABCElement class 
It mostly implements a part of the required abstract methods : the methods that generates the indices from the input datas.
"""

import pandas as pd
from pyHarm.Elements.ABCElement import ABCElement
import numpy as np
import copy
from pyHarm.DofGrabber import gen_NodeToNode_select_matrix, _transform_input_for_grabber
from pyHarm.CoordinateSystem import CoordinateSystem

class NodeToNodeElement(ABCElement) :
    """
    Abstract ABCElement subclass that implements some of the methods in order to help building a node to node connector.
    
    Args:
        nh (int): number of harmonics.
        nti (int): number of time steps.
        name (str): name given to the kinematic condition.
        data (dict): dictionary containing all the definition information of the kinematic condition.
        CS (CoordinateSystem): local or global coordinate system the kinematic condition is defined on.

    Attributes:
        indices (np.ndarray): index of the dofs that the kinematic conditions needs.
        Pdir (np.ndarray): a slice of first dimension is a transformation matrix to a direction in local coordinate system.
        Pslave (np.ndarray): selection array that selects the slave dofs of the kinematic condition.
        Pmaster (np.ndarray): selection array that selects the master dofs of the kinematic condition.
        subs (list[str]): list containing the name of the substructures tht are involved.
        nbSub (int): number of substructure involved.
        nodes (list[list]): list of list of nodes the kinematic conditions act on.
        nbdofi (int): number of nodes involved per substructure.
    """ 
        

    def __init_data__(self, name, data, CS:CoordinateSystem):
        """"
        Method that interprets and deals with the input dictionary by creating some of the essential attributes.

        Attributes:
            subs (list[str]): list containing the name of the substructures tht are involved.
            nbSub (int): number of substructure involved.
            nodes (list[list]): list of list of nodes the kinematic conditions act on.
            nbdofi (int): number of nodes involved per substructure.
        
        """
        self.indices = []
        self.name = name
        self.CS:CoordinateSystem = CS
        _grabbed_inputs = _transform_input_for_grabber(data)
        self.subs = [gi['sub'] for gi in _grabbed_inputs]
        self.nbSub = len(self.subs)
        self.nodes = [[gi['node']] for gi in _grabbed_inputs]
        self.data = data

    def __str__(self):
        _str = f"Element {self.__class__.__name__} : \
            Sub {self.subs[0]} node {self.subs[0]} <--> {self.subs[1]} node {self.subs[1]} Sub"
        return _str


    def generateIndices(self, expl_dofs: pd.DataFrame):
        """From the explicit dof DataFrame, generates the index of dofs concerned by the connector.
        
        Args:
            expl_dofs (pd.DataFrame): explicit dof DataFrame from the studied system.

        Attributes:
            indices (np.ndarray): index of the dofs that the connector needs.
            Pdir (np.ndarray): a slice of first dimension is a transformation matrix to a direction in local coordinate system.
            Pslave (np.ndarray): selection array that selects the slave dofs of the connector.
            Pmaster (np.ndarray): selection array that selects the master dofs of the connector.
        """
        _indices, _Pmat = gen_NodeToNode_select_matrix(edf=expl_dofs, input_dict=self.data)
        _components = expl_dofs.loc[_indices]['dof_num'].unique()
        self.indices = _indices
        self.Pslave, self.Pmaster = _Pmat[0:2] # just keep the two first dofs
        self.Pdir = self._gen_Pdir(_components)

    def _gen_Pdir(self, _components):
        if self.data['dirs'] == [-1] : 
            Pdir = np.array([
                np.eye(self.Pslave.shape)
            ])
        else : 
            Pdir = self.CS.getTM(self.nh,_components)[np.array(self.data["dirs"]),:,:]
        return Pdir

    def _evalJaco_DF(self, xg, om, step):
        """Computes the jacobian using finite difference method.
        
        Args:
            xg (np.ndarray): full displacement vector.
            om (float): angular frequency value.
            step (float): step size for the finite difference method.

        Returns:
            dJdx (np.ndarray): jacobian with respect to displacement vector.
            dJdom (np.ndarray): jacobian with respect to angular frequency.
        """
        R_init = self.evalResidual(xg, om)
        dJdx = np.zeros((len(self.indices), len(self.indices)))
        dJdom = np.zeros((len(self.indices),1))
        for kk,idid in enumerate(self.indices) : 
            x_m = copy.copy(xg)
            x_m[idid] += step
            R_idid = self.evalResidual(x_m, om)
            dJdx[:,kk] = (R_idid - R_init) / step
        R_om = self.evalResidual(xg, om+step)
        dJdom[:,0] = (R_om - R_init) / step
        self.J = dJdx
        self.dJdom = dJdom
        return dJdx, dJdom
    