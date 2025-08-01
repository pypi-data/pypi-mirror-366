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

from pyHarm.NonLinearSolver.ABCNonLinearSolver import ABCNLSolver
import copy
import numpy as np
from pyHarm.Solver import FirstSolution,SystemSolution
from pyHarm.BaseUtilFuncs import getCustomOptionDictionary
from typing import Callable

class Solver_NewtonRaphson(ABCNLSolver):
    """This nonlinear solver is an implementation of iterative Newton Raphson solving procedure.
    
    Attributes:
        factory_keyword (str): keyword that is used to call the creation of this class in the system factory.
        solver_options (dict): dictionary containing other options for creation of the solver class.
        residual (Callable): function that returns the residual vector of the system to be solved.
        jacobian (Callable): function that returns the jacobian matrix of the system to be solved.
        solver_options_root (dict): dictionary containing options for the root function.
        extcall (Callable): root function of scipy.optimize.
    """
    
    factory_keyword : str = "NewtonRaphson"
    """str: keyword that is used to call the creation of this class in the system factory."""

    default = {"tol_residual":1e-8          ,
               "tol_delta_x" :1e-8          ,
               "max_iter"    :300            ,
               "momentum"    :0e-1            } # Maximum iterations accepted before confirming divergence
    """dict: dictionary containing the default solver_options"""


    def __post_init__(self):
        from scipy.linalg import solve as solve
        self.linearsolve = solve
        self.solver_options = getCustomOptionDictionary(self.solver_options,self.default)
        _momentum = self.solver_options["momentum"]
        if ((_momentum>=1.0) or (_momentum<0)):
            raise ValueError(f"Momentum shall be set between [0.0,1.0] : provided value {_momentum:.2E}")
               
    def Solve(self,sol:SystemSolution,SolList:list) -> SystemSolution:
        """
        Runs the solver.

        Args:
            sol (SystemSolution): SystemSolution that contains the starting point.
            SolList (SystemSolution): list of previously solved solutions.
        
        Returns:
            sol (SystemSolution): SystemSolution solved and completed with the output information.
        """
        _residual:Callable = self.residual
        _jacobian:Callable = self.jacobian
        _tol_residual = self.solver_options["tol_residual"]
        _tol_delta_x = self.solver_options["tol_delta_x"]
        _max_iter = self.solver_options["max_iter"]
        _momentum = self.solver_options["momentum"]
        x, xprec, AXk, FXk, iter, status = self._initialisation(sol=sol,SolList=SolList)

        while (\
            (np.linalg.norm(FXk)>= _tol_residual) or\
            (np.linalg.norm(x - xprec)>=_tol_delta_x)
            ):
            deltak = self._linSysdeltak(AXk=AXk, FXk=FXk)
            xprec = copy.deepcopy(x)
            x +=  (-deltak)
            FXk = _residual(x, sol)
            AXk = (1-_momentum)*_jacobian(x, sol) + (_momentum)*AXk
            iter+=1
            if iter>=_max_iter:
                status=5
                self.CompleteSystemSolution(
                    sol=sol,SolList=SolList,
                    x=x, FXk=FXk, iter=iter, status=status)
                return sol
        self.CompleteSystemSolution(
            sol=sol,SolList=SolList,
            x=x, FXk=FXk, iter=iter, status=status)
        return sol

    def _initialisation(self,sol:SystemSolution,SolList:list) \
        -> tuple[np.ndarray,np.ndarray,np.ndarray,np.ndarray, int, int]:
        x = sol.x_start
        xprec = sol.x_start
        FXk = self.residual(sol.x_start, sol)
        AXk = self.jacobian(sol.x_start, sol)
        iter = 0
        status = 1
        return x, xprec, AXk, FXk, iter, status

    def CompleteSystemSolution(self, sol:SystemSolution, SolList:list[SystemSolution],
                               x:np.ndarray, FXk:np.ndarray, iter:int, status:int):
        """
        Function that allows to retrieve information of interest

        Args:
            sol (SystemSolution): SystemSolution that contains the starting point.
            SolList (SystemSolution): list of previously solved solutions.
        """
        sol.x_red = copy.deepcopy(x)
        sol.R_solver = copy.deepcopy(FXk)
        sol.iter_numb = iter
        sol.flag_R = True 
        sol.flag_J = True
        sol.flag_J_f = True
        sol.J_f = self.jacobian(sol.x,sol)
        sol.flag_intosolver = True
        if status == 1:
            sol.flag_accepted = True
        sol.status_solver = status


    def _linSysdeltak(self, AXk:np.ndarray, FXk:np.ndarray) -> np.ndarray:
        """
        Calculation of the 'deltak' correction to apply to the current iteration in order to converge towards the solution.

        Returns:
            self.extcall_newton(matA,matB): Correction 'deltak'
        """
        return self.linearsolve(AXk,FXk)