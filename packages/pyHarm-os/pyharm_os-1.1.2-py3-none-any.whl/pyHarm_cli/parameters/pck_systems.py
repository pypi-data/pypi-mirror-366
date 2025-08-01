from pyHarm_cli.parameters.BaseParam import BaseParam

default_adim_param = dict(
    status=True,
    lc=1.0,
    wc=1.0
)
param_systems = dict(
    Base=[
        BaseParam(name='type', type=str, default="Base", help='factory_keyword of the class'),
        BaseParam(name='nh', type=int, default=1, help='number of harmonics'),
        BaseParam(name='nti', type=int, default=1024, help='number of modal coordinates'),
        BaseParam(name='adim', type=dict, default=default_adim_param, help='adimentionalize the equations', optional=True)
    ]
)

