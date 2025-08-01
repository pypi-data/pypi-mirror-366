from pyHarm_cli.parameters.BaseParam import BaseParam
import numpy as np

param_kinematic= dict(
    GOdisplacement=[
        BaseParam(name='type', type=str, default="GOdisplacement", help='factory_keyword of the class'),
        BaseParam(name='ho', type=int, default=1, help='harmonic on which the condition is imposed'),
        BaseParam(name='dto', type=int, default=0, help='order of the time derivative of the displacement the condition is set on'),
        BaseParam(name='phi', type=float, default=0.0, help='phase value between cosine and sine for the condition'),
        BaseParam(name='amp', type=float, default=1.0, help='ampplitude of the imposed condition'),
    ],
    AccelImposed=[
        BaseParam(name='type', type=str, default="AccelImposed", help='factory_keyword of the class'),
        BaseParam(name='ho', type=int, default=1, help='harmonic on which the condition is imposed'),
        BaseParam(name='phi', type=float, default=0.0, help='phase value between cosine and sine for the condition'),
        BaseParam(name='amp', type=float, default=1.0, help='ampplitude of the imposed condition'),
    ],
    SpeedImposed=[
        BaseParam(name='type', type=str, default="SpeedImposed", help='factory_keyword of the class'),
        BaseParam(name='ho', type=int, default=1, help='harmonic on which the condition is imposed'),
        BaseParam(name='phi', type=float, default=0.0, help='phase value between cosine and sine for the condition'),
        BaseParam(name='amp', type=float, default=1.0, help='ampplitude of the imposed condition'),
    ],
    DispImposed=[
        BaseParam(name='type', type=str, default="DispImposed", help='factory_keyword of the class'),
        BaseParam(name='ho', type=int, default=1, help='harmonic on which the condition is imposed'),
        BaseParam(name='phi', type=float, default=0.0, help='phase value between cosine and sine for the condition'),
        BaseParam(name='amp', type=float, default=1.0, help='ampplitude of the imposed condition'),
    ],
    BaseProjection=[
        BaseParam(name='type', type=str, default="BaseProjection", help='factory_keyword of the class'),
        BaseParam(name='phi', type=str, default="to be completed as np.ndarray directly in the python file", help='Base of projection to be used'),
    ],
)

