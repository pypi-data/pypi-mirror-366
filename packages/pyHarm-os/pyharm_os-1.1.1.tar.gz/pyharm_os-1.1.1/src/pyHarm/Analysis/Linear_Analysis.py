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

from pyHarm.Analysis.ABCAnalysis import ABCAnalysis
from pyHarm.Solver import FirstSolution,SystemSolution
from pyHarm.Systems.ABCSystem import ABCSystem
from pyHarm.BaseUtilFuncs import getCustomOptionDictionary
from scipy import linalg
import numpy as np
import os
import pandas as pd
from pyHarm.Logger import basic_logger
from typing import Optional
import logging
import time
from pyHarm.DofGrabber import harm_cs_grabber, dof_grabber
from pyHarm.DynamicOperator import get_array_nh


class Linear_Analysis(ABCAnalysis):
    """
    Modal analysis and linear forced response analysis.

    Performs a linear modal analysis and then proceeds to a linear FRF by using mode superposition
    
    Attributes:
        system (ABCSystem): ABCSystem associated with the analysis.
        analysis_options (dict): input dictionary completed with the default values if keywords are missing.
        flag_print (bool): if True, prints a message after each Solve method.
        SolList (list[SystemSolution]): list of SystemSolution stored.
        eigensol (dict): output dictionary containing the eigenfrequencies and the eigenvectors
    """
    
    factory_keyword : str = "linear_analysis"
    """str: keyword that is used to call the creation of this class in the system factory."""

    name = "Linear modal & FRF"

    default={"puls_inf":.1,
             "puls_sup":1.0,
             "num_linear_puls": 100,
             "verbose":True,
             "damping": {"modal": {"xi":  0.001}}}

    """dict: default dictionary for the analysis."""
    
    def __init__(self, inputData:dict, System:ABCSystem, logger:Optional[logging.Logger]=None, key:str=""):
        self.key = key
        self.system = System
        self.analysis_options = getCustomOptionDictionary(inputData,self.default)
        self.logger:logging.Logger = logger or basic_logger(name=__name__, debug=True)
        if System.adim :
            self.analysis_options["puls_sup"] = self.analysis_options["puls_sup"] / System.wc
            self.analysis_options["puls_inf"] = self.analysis_options["puls_inf"] / System.wc
        self.flag_print = self.analysis_options["verbose"]
        self.SolList = []
        self.eigensol = {'eigenfrequencies': None,
                         'eigenvectors': None}
        self._check_h1_included(System)
    
    def _check_h1_included(self, System:ABCSystem) -> None: 
        _anh, _, _ =get_array_nh(System.nh)
        if 1 not in _anh :
            self.logger.error(f"Canot pursue {self.name} -- please add harmonic 1 to the system")
            raise ValueError(f"Harmonic 1 needs to be part of system to make {self.name} analysis")
    
    def initialise(self):
        """
        Retrieves the mass and stiffness matrix of the assembled system
        
        Returns:
            K_global (np.ndarray): full stiffness matrix of the system
            M_global (np.ndarray): full mass matrix of the system
        """
        self._init_log()
        x0 = np.concatenate([np.zeros(self.system.ndofs_solve), np.array([0.])])
        M_assembled = self.system._get_assembled_mass_matrix(x0)
        if len(self.system.LE_nonlinear_dlft) != 0 :
            Rlin = np.zeros(self.system.ndofs)
            Rlin += self.system._residual(self.system.LE_extforcing,x0)
            Rlin += self.system._residual(self.system.LE_linear,x0)
            K_assembled = self.system._get_assembled_stiffness_matrix(x0,**{"Rglin":Rlin,"dJgdxlin":None,"dJgdomlin":None})
        else:
           K_assembled = self.system._get_assembled_stiffness_matrix(x0) 
        self.index_h1 = np.array(harm_cs_grabber(self.system.expl_dofs, harm=1, cs='c'))
        _msh = np.meshgrid(self.index_h1,self.index_h1,indexing='ij')
        K_global =  K_assembled[_msh]
        M_global =  M_assembled[_msh]
        return K_global, M_global

    def modal_analysis(self, K, M):
        """
        Eigenvalue analysis leading to the eigenfrequencies and the normalized right eigenvectors
        
        Args:
            K (np.ndarray): full stiffness matrix of the system
            M (np.ndarray): full mass matrix of the system

        Returns:
            omega (np.ndarray): eigenfrequencies in rad/s
            phi (np.ndarray): normalized to unity right eigenvectors
        """
        w, phi = linalg.eig(K, M)
        omega = np.sort(np.sqrt(np.absolute(w)))
        freq_Hz = omega[:10] / (2 * np.pi)
        if self.flag_print:
            self.logger.info(f"### Modal analysis results")
            eigen_freq = [f"{valeur:.2e}" for valeur in freq_Hz]
            eigen_freq_table = "".join([f"|{str(k):^15}|{ef:^15} Hz|\n" for k,ef in enumerate(eigen_freq[:10])])
            self.logger.info(eigen_freq_table)
        return omega, phi

    def compute_linear_FRF(self, K, M, phi):
        """
        Linear frequency response function by means of mode superposition
        
        Args:
            K (np.ndarray): full stiffness matrix of the system
            M (np.ndarray): full mass matrix of the system
            phi (np.ndarray): normalized to unity right eigenvectors
        """
        damping = self.analysis_options['damping']

        # Generalized mass and stiffness matrices
        Mg = phi.T @ M @ phi
        Kg = phi.T @ K @ phi

        # Damping matrix
        # Option 1: Rayleigh
        if 'Rayleigh' in damping.keys():
            C = damping['Rayleigh']['coef_K'] * K + damping['Rayleigh']['coef_M'] * M
            Cg = phi.T @ C @ phi
        # Option 2: Modal damping
        elif 'modal' in damping.keys():
            Cg = 2 * damping['modal']['xi'] * np.sqrt(np.diag(np.diag(Kg))) @ np.sqrt(np.diag(np.diag(Mg)))

        # External forcing
        sub = list(self.system.LE_extforcing[0].data['connect'].keys())[0]
        node_num = self.system.LE_extforcing[0].data['connect'][sub][0]
        dof_num = self.system.LE_extforcing[0].data['dirs'][0]
        expl_dofs = self.system.expl_dofs.loc[self.index_h1].reset_index()
        dof_ex = np.array(dof_grabber(edf=expl_dofs, sub=sub, node=node_num, dof=dof_num))
        # dof_ex = expl_dofs[(expl_dofs['harm']==0) & (expl_dofs['sub']==sub) & (expl_dofs['node_num']==node_num) & (expl_dofs['dof_num']==dof_num)].index[0]
        F = np.zeros((len(K), 1))
        F[dof_ex] = self.system.LE_extforcing[0].data['amp']

        # Forced response
        om = np.linspace(self.analysis_options['puls_inf'], self.analysis_options['puls_sup'], self.analysis_options['num_linear_puls'])
        for omega in om:
            Z = Kg - omega**2 * Mg + (1j) * omega * Cg # Inverse of FRF or transfer function
            Q = np.linalg.inv(Z) @ (phi.T @ F)
            X = phi @ np.reshape(Q, (len(Q),))
            X = np.concatenate((np.abs(X).reshape(-1,1), np.asarray(omega).reshape(-1,1)))
            isol = FirstSolution(X)
            self.SolList.append(isol)

    def Solve(self, x0=None, **kwargs):
        """
        Solving step of the analysis.
        """
        self.Ti = time.time()
        K, M = self.initialise()
        omega, phi = self.makeStep(K,M)
        self.eigensol['eigenfrequencies'] = omega / (2 * np.pi)
        self.eigensol['eigenvectors'] = phi
        self.Te = time.time()
        self.timetosolve = self.Te - self.Ti
        self._end_log()
    
    def makeStep(self,K,M):
        """
        Makes a whole step of the analysis.
        
        Args:
            K (np.ndarray): full stiffness matrix of the system
            M (np.ndarray): full mass matrix of the system

        Returns:
            omega (np.ndarray): eigenfrequencies in rad/s
            phi (np.ndarray): normalized to unity right eigenvectors
        """
        omega, phi = self.modal_analysis(K,M)
        self.compute_linear_FRF(K, M, phi)
        return omega, phi

    def export(self, export_path:str, prefix:str, **kwargs) -> None:
        """
        export resutlts in csv files
        """
        file_to_export_solutions_linearFRF = os.path.join(export_path,f"{prefix}_linearFRF.csv")
        file_to_export_solutions_linearmodes = os.path.join(export_path,f"{prefix}_linearmodes.csv")
        acc_sols = [sol for sol in self.SolList]
        # test_sol = acc_sols[0]
        # print(test_sol.x[:-1].reshape(-1,1))
        xxom = np.concatenate([
            np.concatenate([sol.x[:-1].reshape(-1,1) * self.system.lc for sol in acc_sols], axis=1),
            np.array([sol.x[-1] * self.system.wc for sol in acc_sols]).reshape(1,-1)
            ],axis=0)
        df = pd.DataFrame(xxom)
        df.to_csv(file_to_export_solutions_linearFRF)
        xxom = np.concatenate([
            self.eigensol['eigenvectors'],
            self.eigensol['eigenfrequencies'].reshape(1,-1)
            ],axis=0)
        df = pd.DataFrame(xxom)
        df.to_csv(file_to_export_solutions_linearmodes)
        self._export_log()
        pass

    def _init_log(self,):
        _puls_inf = self.analysis_options["puls_inf"]
        _puls_sup = self.analysis_options["puls_sup"]
        range_puls = f"[{_puls_inf:.2E},{_puls_sup:.2E}] rad/s"
        range_freq = f"[{_puls_inf/(2*np.pi):.2E},{_puls_sup/(2*np.pi):.2E}] Hz"
        self.logger.info(f"""## Analysis \'{self.key}\'  of type \'{self.name}\'
                         |{"Pulsation range":^20}|{range_puls:30}|
                         |{"Frequency range":^20}|{range_freq:30}|\n""")
        self.logger.info(f"""Starting computations""")
        pass
        
    def _end_log(self,):
        self.logger.info(f"""## Ending \'{self.key}\' analysis of type \'{self.name}\' in {self.timetosolve}s\n""")
        pass
    
    def _export_log(self,):
        self.logger.info(f"""## Results of \'{self.key}\' analysis exported""")
        pass
