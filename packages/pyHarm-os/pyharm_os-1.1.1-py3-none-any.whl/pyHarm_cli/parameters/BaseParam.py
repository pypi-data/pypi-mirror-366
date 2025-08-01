from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import List, Any

class BaseParam(BaseModel): 
    name : str
    type : type
    default : Any
    help : str
    optional: bool = False

    @field_validator('default')
    def check_default_type(cls, v, info):
        field_type = info.data.get('type')
        if field_type and not isinstance(v, field_type):
            raise ValueError(f"Default value must be of type {field_type.__name__}")
        return v    