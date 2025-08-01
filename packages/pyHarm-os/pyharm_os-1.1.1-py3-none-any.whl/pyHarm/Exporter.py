from typing import Protocol, runtime_checkable
from dataclasses import dataclass
import os
import pandas as pd
import os
import datetime
import logging 

def _create_results_folder(base_path='.', date_time_option:bool=False) -> str:
    # Generate timestamp
    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
    if date_time_option : folder_name = f"_results_{date_time}"
    else : folder_name = "_results"

    # Create full path
    full_path = os.path.join(base_path, folder_name)

    # Check if folder exists
    if not os.path.exists(full_path):
        # Create folder
        os.makedirs(full_path)

    return full_path

@runtime_checkable
class Exportable(Protocol):
    def export(self, export_path:str, prefix:str, *args, **kwargs) -> None :
        """
        Exports data to a specified file path.

        Args:
            data: The data to be exported.
            file_path: The path to the file where the data will be exported.
            **kwargs: Additional keyword arguments that might be needed for specific exporters.
        """
        ...

class Exporter:
    def __init__(self, export_path:str, status:bool=False, date_time_option:bool=False, **kwargs) -> None:
        self.status = status
        if self.status : 
            self.folder = _create_results_folder(base_path=export_path, date_time_option=date_time_option)
        else : self.folder = ""
        pass
    def export(self, DE:dict[str:Exportable], logger:logging.Logger) -> None:
        """
        Exports data to a specified file path.

        Args:
            data: The data to be exported.
            file_path: The path to the file where the data will be exported.
            **kwargs: Additional keyword arguments that might be needed for specific exporters.
        """
        if self.status : 
            logger.info(f"# START EXPORTING PHASE IN \'{self.folder}\' folder")
            for prefix,exportable in DE.items() : 
                exportable.export(export_path=self.folder, prefix=prefix)
            logger.info(f"# END EXPORTING PHASE\n")
        else : pass


