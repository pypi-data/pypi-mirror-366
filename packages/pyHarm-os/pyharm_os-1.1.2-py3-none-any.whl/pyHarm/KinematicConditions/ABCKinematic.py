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

from pyHarm.DynamicOperator import compute_DFT, nabla
from pyHarm.CoordinateSystem import CoordinateSystem
import numpy as np
import pandas as pd
import abc
import copy
from pyHarm.DofGrabber import gen_NodeToNode_select_matrix
from typing import Optional


class ABCKinematic(abc.ABC):
    """This is the abstract class ruling the kinematic conditions class. The kinematic conditions are responsible to impose kinematic on dofs of the system and transfer the residuals.
    
    Args:
        nh (int): number of harmonics.
        nti (int): number of time steps.
        name (str): name given to the kinematic condition.
        data (dict): dictionary containing all the definition information of the kinematic condition.
        CS (CoordinateSystem): local or global coordinate system the kinematic condition is defined on.

    Attributes:
        nh (int): number of harmonics.
        nti (int): number of time steps.
        D (dict[np.ndarray,np.ndarray]): Dynamic operators containing inverse discrete Fourier transform and discrete Fourier transform.
        nabla (np.ndarray): Derivation operator.
        indices (np.ndarray): index of the dofs that the kinematic conditions needs.
        Pdir (np.ndarray): a slice of first dimension is a transformation matrix to a direction in local coordinate system.
        Pslave (np.ndarray): selection array that selects the slave dofs of the kinematic condition.
        Pmaster (np.ndarray): selection array that selects the master dofs of the kinematic condition.
        subs (list[str]): list containing the name of the substructures that are involved.
        nbSub (int): number of substructure involved.
        nodes (list[list]): list of list of nodes the kinematic conditions act on.
        nbdofi (int): number of nodes involved per substructure.
    """
    
    @property
    @abc.abstractmethod
    def factory_keyword(self):
        ...
        
    def __init__(self, nh:int, nti:int, name:str, data:dict, CS:CoordinateSystem, dynop:Optional[dict[str,np.ndarray]]=None):
        # flags #
        self.__init_flags__()
        # real parameters #
        self.__init_harmonic_operators__(nh,nti, data=data,dynop=dynop)
        self.__init_data__(name,data,CS)
        self.__post_init__()
        self.__flag_update__()

    def __init_flags__(self,):
        pass


    def __init_harmonic_operators__(self, nh, nti, data:dict, dynop:Optional[dict[str,np.ndarray]]=None):
        _build_dynop = False
        self.nti = nti
        self.nh = nh
        if dynop : self.D = dynop # if dynop provided then use the provided ones
        if "nti" in data.keys(): self.nti:int = data['nti']; _build_dynop=True # if specific nti given in data of the element 
        if ((_build_dynop) or (not dynop)) : self.D = compute_DFT(self.nti, nh) # then build the required dynamic operator instead OR if dynop not provided
        self.nabla = nabla(nh)

    def __init_data__(self, name, data, CS):
        self.indices = []
        self.name = name
        self.CS = CS
        self.subs = list(data["connect"].keys())
        self.nbSub = len(self.subs)
        if "INTERNAL" in self.subs : 
            self.subs[1] = self.subs[0]
        self.nodes = list(data["connect"].values())
        self.nbdofi = len(data["connect"][list(data["connect"].keys())[0]])
        self.data = data

    def __str__(self):
        if not self.flag_substructure :
            subnames = self.subs
            sub1 = subnames[0]
            sub1ddls = self.dofssub[0]
            if self.nbSub == 1 :
                sub2 = "ground"
                sub2ddls = ""
            else : 
                sub2 = subnames[1]
                sub2ddls = self.dofssub[1]
            return "Kinematic Condition of type {} that links :\n - {} dofs {} \n to\n - {} dofs {}".format(self.__class__.__name__, sub1, sub1ddls,\
                                                                sub2, sub2ddls,)
        else :
            return "Kinematic Condition of type {}".format(self.__class__.__name__)
        
    def __repr__(self):
        return "{}[{}]".format(self.name, self.__class__.__name__)
    
    def __post_init__(self,*args):
        pass

    def __flag_update__(self,*args):
        pass


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

    @abc.abstractmethod
    def adim(self,lc,wc):
        """Using adim parameters, modifies the kinematic conditions accordingly.
        
        Args:
            lc (float): characteristic length.
            wc (float): characteristic angular frequency.
        """
        pass
    
    @abc.abstractmethod
    def complete_x(self, x, om):
        """Returns a vector x_add of same size of x that completes the vector of displacement x = x + x_add.
        
        Args:
            x (np.ndarray): displacement vector.
            om (float): angular frequency.
        """
        pass
    
    @abc.abstractmethod
    def complete_R(self, R, x):
        """Returns a vector R_add of same size of R that completes the vector of residual R = R + R_add
        
        Args:
            R (np.ndarray): residual vector.
            x (np.ndarray): displacement vector.
        """
        pass

    @abc.abstractmethod
    def complete_J(self, Jx, Jom, x):
        """Returns a vector Jx_add and Jom_add of same size of Jx and Jom that completes the Jacobian
        
        Args:
            Jx (np.ndarray): jacobian matrix with respect to displacement.
            Jom (np.ndarray): jacobian matrix with respect to angular frequency.
            x (np.ndarray): displacement vector.
        """
        pass