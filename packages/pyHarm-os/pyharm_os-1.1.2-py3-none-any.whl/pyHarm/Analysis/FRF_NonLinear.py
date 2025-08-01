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
import numpy as np
from pyHarm.Correctors.FactoryCorrector import generateCorrector
from pyHarm.Predictors.FactoryPredictor import generatePredictor
from pyHarm.StepSizeRules.FactoryStepSize import generateStepSizeRule
from pyHarm.StopCriterion.FactoryStopCriterion import generateStopCriterion
from pyHarm.NonLinearSolver.FactoryNonLinearSolver import generateNonLinearSolver
from pyHarm.Reductors.FactoryChainedReductors import generateChainReductor
from pyHarm.BaseUtilFuncs import getCustomOptionDictionary
import logging 
from pyHarm.Logger import basic_logger
from typing import Optional
import pandas as pd
import os
import time

class FRF_NonLinear(ABCAnalysis):
    """
    Nonlinear forced response analysis.

    Predicts a starting point using the predictor and then solves the residual equations from the starting point.
    
    Attributes:
        flag_print (bool): if True, prints a message after each Solve method.
        flag_purge (bool): if True, the jacobian values are purged from the solutions stored in the solution list.
        analysis_options (dict): input dictionary completed with the default values if keywords are missing.
        ds (float): initial prediction step size.
        SolList (list[SystemSolution]): list of SystemSolution stored after each Solve method.
        system (ABCSystem): ABCSystem associated with the analysis.
        adaptstep (ABCStepSizeRule): ABCStepSizeRule associated with the analysis.
        predictor (ABCPredictor): ABCPredictor associated with the analysis.
        corrector (ABCCorrector): ABCCorrector associated with the analysis.
        stopper (ABCStopCriterion): ABCStopCriterion associated with the analysis.
        solver (ABCNLSolver): ABCNLSolver associated with the analysis.
        corrector_init (ABCCorrector): instance of no-continuation corrector for initial solution.
        reductor (ABCChainedReductor): ABCChainedReductor associated with the analysis.
    """
    
    factory_keyword : str = "frf"
    """str: keyword that is used to call the creation of this class in the system factory."""

    name = "Nonlinear FRF"

    default={   "study":"frf",
                "solver":"scipyroot",
                "predictor":"tangent",
                "corrector":"arc_length",
                "preconditioner":"nopreconditioner",
                "reductors":[{"type":"noreductor"}],
                "stepsizer":"acceptance",
                "stopper":"bounds",
                "ds_max":1e0,"ds_min":1e-8,"ds0":1e0,
                "sign_ds":1,
                "puls_inf":.1,"puls_sup":1.0,
                "verbose":True,
                "purge_jacobians":True,
                }
    """dict: default dictionary for the analysis."""
    
    def __init__(self, inputData:dict, System:ABCSystem, logger:Optional[logging.Logger]=None, key:str="", **kwargs):
        self.key = key
        self.analysis_options = getCustomOptionDictionary(inputData,self.default)
        self.flag_print = self.analysis_options["verbose"]
        self.flag_purge = self.analysis_options["purge_jacobians"]
        self.logger:logging.Logger = logger or basic_logger(name=__name__, debug=True)
        if System.adim :
            self.analysis_options["puls_sup"] = self.analysis_options["puls_sup"] / System.wc
            self.analysis_options["puls_inf"] = self.analysis_options["puls_inf"] / System.wc
        if "puls_start" not in self.analysis_options : # set the puls_start if not given to puls_inf or puls_sup depending on the sign ds
            self.analysis_options["puls_start"] = 1/2.*(self.analysis_options["sign_ds"]+1)*self.analysis_options["puls_inf"] \
                                                - 1/2.*(self.analysis_options["sign_ds"]-1)*self.analysis_options["puls_sup"]
        
        self.ds = self.analysis_options["ds0"]
        self.SolList = []
        ### Base objects :
        self.system = System
        self.adaptstep = generateStepSizeRule(self.analysis_options["stepsizer"],\
                                             [self.analysis_options['ds_min'],self.analysis_options['ds_max']],\
                                             self.analysis_options.get("stepsize_options",dict()))
        self.predictor = generatePredictor(self.analysis_options["predictor"], self.analysis_options["sign_ds"], logger=self.logger, predictor_options=self.analysis_options.get("predictor_options",dict()))
        self.corrector = generateCorrector(self.analysis_options["corrector"],self.analysis_options.get("corrector_options",dict()))
        self.stopper = generateStopCriterion(self.analysis_options["stopper"],\
                                             [self.analysis_options['puls_inf'],self.analysis_options['puls_sup']],\
                                             self.analysis_options['ds_min'],\
                                             self.analysis_options.get("stopper_options",dict()))
        self.solver = generateNonLinearSolver(self.analysis_options["solver"],\
                                             self.globalResidualwRed, self.globalJacobianwRed,\
                                             self.analysis_options.get("solver_options",dict()))
        self.corrector_init = generateCorrector("nocontinuation",self.analysis_options.get("corrector_options",dict()))
        self.reductor = generateChainReductor(self.analysis_options["reductors"],
                                              self.system._get_expl_dofs_into_solver())
    
    def initialise(self, x0=None, **kwargs):
        """
        First Solve on the initial guess.

        Args:
            x0 (None|str|np.ndarray): if None x0 is the linear solution at initial angular frequency, if "null" x0 is null vector, otherwise x0 is initialised using the provided array.
        """
        self._init_log()
        ### Some new arguments :
        x0 = self._get_x0(x0)
        self.x0,_,_ = self._update_reductor(x0)
        isol = FirstSolution(self.x0)
        self.solver.Solve(isol,self.SolList)
        isol.index_insolve = 0
        self.CompleteSolution(isol)
        isol.SaveSolution(self.SolList)
        if self.flag_print :
            if isol.flag_accepted :
                _status = "Converged"
            else :
                _status = "Fail"
            self.logger.info(f"{_status:^20} - om = {isol.x[-1]:.3E} rad/s")
                
    def _get_x0(self, x0) : 
        om0 = np.array([self.analysis_options["puls_start"]])
        if not isinstance(x0,np.ndarray) : 
            if x0 == None : # if none, takes linear solution as starting point
                x0 =np.concatenate([np.zeros(self.system.ndofs_solve), np.array([self.analysis_options["puls_start"]])])
                x0f = self.system._expand_q(x0)
                x0f += self.system._complete_x(self.system.LC, x0f)
                p0 = self.system._residual(self.system.LE_extforcing,x0f)
                p0 = self.system.kick_kc_dofs @ p0
                j0x,j0om = self.system.Jacobian(x0)
                x0x = np.linalg.solve(j0x,-p0)
                x0 = np.concatenate([x0x, om0])
            elif x0 == "null":
                x0 = np.concatenate([np.zeros(self.system.ndofs_solve), om0])
        else :
            x0 = np.concatenate([x0, om0])
        return x0
        
    def CompleteSolution(self,sol:SystemSolution):
        """
        Completes a SystemSolution informations that just went out of the Solve method.

        Args:
            sol (SystemSolution): solution to the system.
        """
        sol.x = self.reductor.expand(sol.x_red)
        sol.flag_R = True 
        sol.flag_J = True
        sol.flag_J_f = True
        dR_change=None
        sol.R = self.globalResidual(sol.x,sol)
        sol.J_f = self.globalJacobian(sol.x,sol)
        
    def globalResidual(self, solx:np.ndarray, sol:SystemSolution):
        """
        Computes the residual of the whole system without the reducers.

        Args:
            solx (np.ndarray): displacement vector for which residual is computed.
            sol (SystemSolution): actual SystemSolution being solved.
        """
        # Get the Residual of the system at point x
        Rg = self.system.Residual(solx)
        # Get the corrector closure equation
        if isinstance(sol,FirstSolution) :
            R_cont = self.corrector_init.ClosureEquation(solx, sol, self.SolList)
        else : 
            R_cont = self.corrector.ClosureEquation(solx, sol, self.SolList)
        # Assembly of the matrix
        Rg = np.concatenate((Rg, np.asarray([R_cont])))
        return Rg

    def globalJacobian(self, solx:np.ndarray, sol:SystemSolution):
        """
        Computes the jacobians of the whole system without the reducers.

        Args:
            solx (np.ndarray): displacement vector for which residual is computed.
            sol (SystemSolution): actual SystemSolution being solved.
        """
        # Get the Jacobian of the system at point x
        [dJdx, dJdom] = self.system.Jacobian(solx)
        # Get the corrector Jacobian of closure equation 
        if isinstance(sol,FirstSolution) :
            [dRdx, dRdom] = self.corrector_init.ClosureJacobian(solx, sol, self.SolList) 
        else :
            [dRdx, dRdom] = self.corrector.ClosureJacobian(solx, sol, self.SolList) 
        Jg = np.block([[dJdx, dJdom], [np.reshape(dRdx, (1, dJdx.shape[0])), np.asarray([dRdom])]])
        return Jg
    
    def globalJacobianwRed(self, solq:np.ndarray, sol:SystemSolution):
        """
        Computes the reduced jacobians of the whole system.

        Args:
            solq (np.ndarray): reduced displacement vector for which residual is computed.
            sol (SystemSolution): actual SystemSolution being solved.
        """
        solx = self.reductor.expand(solq)
        Jg = self.globalJacobian(solx, sol)
        Jg = self.reductor.reduce_matrix(Jg,solx[-1])
        return Jg
    
    def globalResidualwRed(self, solq:np.ndarray, sol:SystemSolution):
        """
        Computes the reduced residuals of the whole system.

        Args:
            solq (np.ndarray): reduced displacement vector for which residual is computed.
            sol (SystemSolution): actual SystemSolution being solved.
        """
        solx = self.reductor.expand(solq)
        Rg = self.globalResidual(solx, sol)
        Rg = self.reductor.reduce_vector(Rg)
        return Rg
    
    def _update_reductor(self, xpred_full, last_solution_pointer=None):
        """
        Updates the reducers

        Args:
            xpred_full (np.ndarray): full starting displacement vector.
            last_solution_pointer (SystemSolution): SystemSolution from which the prediction has been generated.

        Returns:
            xpred_red (np.ndarray): reduced starting displacement vector.
            J_red (np.ndarray): reduced jacobian matrix.
            output_expl_dofs (pd.DataFrame): DataFrame of the dofs after applying the reduction layers.
        """
        if last_solution_pointer == None : 
            sol = FirstSolution(xpred_full)
        else :
            sol = SystemSolution(xpred_full,last_solution_pointer) # fake SystemSolution
        J_f = self.globalJacobian(xpred_full,sol)
        xpred_red, J_red, output_expl_dofs = self.reductor.update_reductor(xpred_full,
                                                                           J_f,
                                                                           self.system._get_expl_dofs_into_solver(),
                                                                           self.system) # updates the reductor
        
        return xpred_red, J_red, output_expl_dofs
    
    def makeStep(self,**kwargs) :
        """
        Makes a step of solving : get a step size, generate a predicted point, solve the nonlinear system, save the solution.
        """
        # obtain the starting point 
        self.ds = self.adaptstep.getStepSize(self.ds,self.SolList)

        xpred_full,last_solution_pointer,sign_ds = self.predictor.predict(self.SolList,self.ds)

        ## update the reductor --> need to use old version of the reduce
        xpred_red,_,output_expl_dofs = self._update_reductor(xpred_full, last_solution_pointer) # update the reductor
        ## end update reductor
        sol = SystemSolution(xpred_red,last_solution_pointer) 
        sol.ds = self.ds
        sol.sign_ds = sign_ds
        sol = self.solver.Solve(sol, self.SolList)
        self.CompleteSolution(sol)
        if "index_insolve" in kwargs : 
            sol.index_insolve = kwargs["index_insolve"]
        sol.SaveSolution(self.SolList)
        if self.flag_print :
            if sol.flag_accepted :
                _status = "Converged"
            else :
                _status = "Fail"
            self.logger.info(f"{_status:^20} - om = {sol.x[-1]:.3E} rad/s")
        pass

    def Solve(self, x0=None, **kwargs):
        """
        Makes the whole analysis using continuation techniques until the stopping criterion is validated

        Args:
            x0 (None|str|np.ndarray): if None x0 is the linear solution at initial angular frequency, if "null" x0 is null vector, otherwise x0 is initialised using the provided array.
        """
        self.Ti = time.time()
        self.initialise(x0, **kwargs)
        k=1
        while not self.stopper.getStopCriterionStatus(self.SolList[-1],self.SolList) : 
            self.makeStep(index_insolve=k)
            self.purge_jacobians()
            k+=1
        self.Te = time.time()
        self.timetosolve = self.Te - self.Ti
        self._end_log()
        pass

    def purge_jacobians(self,):
        """Purge the Jacobians of Solutions that are no longer used."""
        def purge(SA) : 
            for sol in SA:
                sol.J_f = None
                sol.J_lu = None
                sol.J_qr = None
                sol.flag_J = False
                sol.flag_J_qr = False # Jacobian available with qr formalism of scipy.linalg.qr=[Q,R]
                sol.flag_J_lu = False # Jacobian available with lu formalism of scipy.linalg.lu=[P,L,U]
                sol.flag_J_f = False # Jacobian available full size

        if not self.flag_purge : 
            pass
        else : 
            acc_sols = [sol for sol in self.SolList if ((sol.flag_accepted) and (sol.flag_J))]
            nonacc_sols = [sol for sol in self.SolList if ((not sol.flag_accepted) and (sol.flag_J))]
            purge(acc_sols[:-2])
            purge(nonacc_sols)

    def export(self, export_path:str, prefix:str, **kwargs) -> None:
        """
        export resutlts in csv files
        """
        _sollist:list[SystemSolution] = self.SolList
        # export solutions in dataFrame -- [x, om]
        file_solutions = os.path.join(export_path,f"{prefix}_sol.csv")
        xxom = np.concatenate([
            np.concatenate([sol.x[:-1].reshape(-1,1) * self.system.lc for sol in _sollist], axis=1),
            np.array([sol.x[-1] * self.system.wc for sol in _sollist]).reshape(1,-1)
            ],axis=0)
        df = pd.DataFrame(xxom)
        df.to_csv(file_solutions)
        # export solutions char -- [accepted, bifurcation]
        file_solcarac = os.path.join(export_path,f"{prefix}_carac.csv")
        acc = []
        bif = []
        normR = []
        for sol in _sollist : 
            acc.append(sol.flag_accepted)
            bif.append(sol.flag_bifurcation)
            normR.append(np.linalg.norm(sol.R_solver))
        df_carac = pd.DataFrame(
            dict(
                accepted = acc,
                bifurcation = bif,
                normResidual = normR
            )
        )
        df_carac.to_csv(file_solcarac)
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
