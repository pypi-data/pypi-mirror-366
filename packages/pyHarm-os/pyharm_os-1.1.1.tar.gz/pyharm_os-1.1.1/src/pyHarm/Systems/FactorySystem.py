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
Module that defines the Factory of the package. 

Attributes:
    System_dico (dict[str,ABCSystem]) : Dictionary containing the available ABCSystem in pyHarm for creation as values and their factory_keyword as keys.
"""
from pyHarm.Systems.ABCSystem import ABCSystem
from pyHarm.Systems.System import System
import logging 
from typing import Optional


System_dico = { System.factory_keyword:             System}
"""dict[str,ABCSystem]: Dictionary containing the available ABCSystem in pyHarm for creation as values and their factory_keyword as keys.
"""

def check_and_repair_system_input(data:dict, logger:logging.Logger) -> dict : 
    """
    Check and repair the input dictionnary for systems in order to ensure proper functining.

    Args:
        data (dict): input dict provided to the maestro.

    Returns:
        dict: repaired data dictionnary
    """
    # check if key is present :
    if not 'system' in data.keys() :
        _err_msg = "System data checker -- \'system\' key is missing -- no System can be instanciated"
        logger.critical(_err_msg)
        raise KeyError(_err_msg)
    # fix the nh data if unordered list is provided
    _nh_data:int|list[int] = data['system']['nh']
    if isinstance(_nh_data, list) : data['system']['nh'] = sorted(set(_nh_data))

    return data


def generateSystem(name_system:str, datas:dict, logger:Optional[logging.Logger]=None) -> ABCSystem:
    """
    Factory function that creates a ABCSystem object.

    Args:
        name_system (str): Type of the system object that is to be instantiated.
        datas (dict): dictionary containing the inputs that are needed to create a system.

    Returns:
        ABCSystem: Instance of the required ABCSystem class.
    """
    E = System_dico[name_system](datas, logger=logger)
    return E