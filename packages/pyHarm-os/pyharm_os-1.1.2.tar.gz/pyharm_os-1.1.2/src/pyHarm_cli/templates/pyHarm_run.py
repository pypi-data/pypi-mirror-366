####################### IMPORTS
import pyHarm
import json

####################### GLOBAL VARIABLES
BASE_PATH_SYS = r"./system.json"
BASE_PATH_ANA = r"./analysis.json"

######################## INPUT DICT
input_dict = dict()

########## plugin some user classes if needed
input_dict['plugin'] = [
    
]

########## System input
with open(BASE_PATH_SYS, 'r', encoding='utf-8') as sysjson :
    input_dict = input_dict | json.load(sysjson)

########## Analysis input
with open(BASE_PATH_ANA, 'r', encoding='utf-8') as anajson :
    input_dict = input_dict | json.load(anajson)

######################## BUILD AND RUN MAESTRO IF MAIN FILE RUN
if __name__ == "__main__" : 
    maestro = pyHarm.Maestro(input_dict)
    maestro.operate()

