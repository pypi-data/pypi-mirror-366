from pyHarm_cli.parameters.BaseParam import BaseParam


param_analysis = dict(
    FRF_NonLinear=[
        BaseParam(name='study', type=str, default="frf", help='factory_keyword of the class'),
        BaseParam(name='puls_inf', type=float, default=1.0, help='Angular frequency lower bound'),
        BaseParam(name='puls_start', type=float, default=1.0, help='Starting angular frequency', optional=True),
        BaseParam(name='puls_sup', type=float, default=10.0, help='Angular frequency upper bound'),
        BaseParam(name='ds_min', type=float, default=1e-3, help='minimal step size'),
        BaseParam(name='ds_max', type=float, default=1e0, help='maximal step zise'),
        BaseParam(name='ds0', type=float, default=1e0, help='Initial step size'),
        BaseParam(name='solver', type=str, default="scipyroot", help='nonlinear solver used'),
        BaseParam(name='predictor', type=str, default="tangent", help='predictor for the continuation procedure'),
        BaseParam(name='corrector', type=str, default="arc_length", help='corrector for the continuation procedure'),
        BaseParam(name='reductors', type=list, default=[dict(type='noreductor')], help='reduction techniques applied'),
        BaseParam(name='sign_ds', type=int, default=1, help='direction of the path 1 increasing frequency, -1 decreasing'),
        BaseParam(name='stepsizer', type=str, default="acceptance", help='stepsize rule', optional=True),
        BaseParam(name='stopper', type=str, default="bounds", help='stop criterion', optional=True),
        BaseParam(name='purge_jacobians', type=bool, default=True, help='stop criterion', optional=True),
        BaseParam(name='verbose', type=bool, default=True, help='stop criterion', optional=False),
    ],
    Linear_Analysis=[
        BaseParam(name='study', type=str, default="linear_analysis", help='factory_keyword of the class'),
        BaseParam(name='puls_inf', type=float, default=1.0, help='Angular frequency lower bound'),
        BaseParam(name='puls_sup', type=float, default=10.0, help='Angular frequency upper bound'),
        BaseParam(name='damping', type=dict, default=dict(modal=dict(xi=0.1)), help='damping nature and value'),
        BaseParam(name='verbose', type=bool, default=True, help='stop criterion', optional=False),
    ],
)