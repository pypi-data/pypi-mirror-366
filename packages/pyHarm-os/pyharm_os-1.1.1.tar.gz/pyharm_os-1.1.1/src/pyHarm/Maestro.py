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

from pyHarm.Analysis.FactoryNonLinearStudy import generateNonLinearAnalysis
from pyHarm.Systems.FactorySystem import generateSystem, check_and_repair_system_input
from pyHarm.BaseUtilFuncs import getCustomOptionDictionary, pyHarm_plugin
from pyHarm.Exporter import Exporter, Exportable
import numpy as np
import time
import copy
import logging
from pyHarm.Logger import basic_logger, export_logger
import uuid
from pyHarm._admin_funcs import deprecated

class Maestro():
    """
    Class that reads and launches the pyHarm analysis contained in the provided input file.

    The class is in charge of reading the input file and build the system and the analysis that are requested by the input file.
    The class is in charge of loading the plugins beforehand if some plugins are requested by the input file.
    When operated, the class runs a loop over the analysis required and solve them.
    
    Args:
        idata (dict): input dictionary describing all the necessary component (analysis, system composition).
        
    """
    default = {
        "plugin":[],
        "analysis":dict(),
        "export":dict(
            status=False,
            export_path='.',
            date_time_option=False
        )
    }
    def __init__(self,idata:dict):
        self.uuid = str(uuid.uuid4())
        idata = getCustomOptionDictionary(idata,self.default)
        self.inputData = idata
        self.inputData['export'] = getCustomOptionDictionary(self.inputData['export'],self.default['export'])
        self.exporter = Exporter(**self.inputData['export'])
        if self.inputData['export']['status'] == False : self.logger = basic_logger(f"{__name__}_{self.uuid}")
        else : self.logger = export_logger(f"{__name__}_{self.uuid}", self.exporter.folder)
        # -- Import the plugins -- #
        for cls in self.inputData["plugin"] :
            pyHarm_plugin(cls)
        # -- First we build the system -- #
        idata = check_and_repair_system_input(data=idata,logger=self.logger) # check system inputs and repair if necessary
        self.system = generateSystem(idata["system"]["type"],self.inputData, logger=self.logger)
        # -- Build the Analysis objects -- #
        self.nls = dict()
        # Operate the analysis : 
        for analysis_name,analysis_config_input in self.inputData["analysis"].items() : 
            analysis_config = copy.deepcopy(analysis_config_input)
            self.nls[analysis_name] = generateNonLinearAnalysis(analysis_config["study"], analysis_config, self.system, logger=self.logger, key=analysis_name)

        
    def operate(self, x0=None,**kwargs):
        """
        Loops over the analysis and runs the Solve method associated with the analysis.
        
        Args:
            x0 (None | np.ndarray | str): initial point from which running the analysis.
            kwargs : additional keyword arguments.
            
        """
        self.logger.info(f"# START COMPUTATIONS : {len(self.nls)} analysis \n")
        for name_analysis, analysis in self.nls.items():
            debut = time.time()
            analysis.Solve(x0,**kwargs)
            self.timetosolve = time.time()-debut
        self.logger.info(f"# END COMPUTATIONS\n")
        # exporting phase : 
        export_dict = dict()
        if isinstance(self.system, Exportable) : export_dict['system'] = self.system
        export_dict = export_dict | {
            prefix: analysis for prefix, analysis in self.nls.items()
            if isinstance(analysis, Exportable)
        }
        self.exporter.export(export_dict, logger=self.logger)

    @deprecated(replacement="Favor *_grabber functions from \'DofGrabber.py\' module")
    def getIndex(self, sub:str, node:int, dir_num:int) -> np.ndarray :
        """
        From a substructure name, a node number, and a direction; returns the index of the required dof into the explicit dof vector of the system.
        
        Args:
            sub (str): name of the substructure.
            node (int): node number.
            dir_num (int): direction number.
        
        Returns : 
            np.ndarray : sorted array of the dof index associated with the input in the explicit dof DataFrame of the system.
            
        """
        expl_dofs = self.system.expl_dofs
        submatch = (expl_dofs["sub"]==sub)
        nodematch = (expl_dofs["node_num"]==node)
        dof_match = (expl_dofs["dof_num"]==dir_num)
        return np.sort(expl_dofs[submatch*nodematch*dof_match].index)

