from pyHarm_cli.parameters.BaseParam import BaseParam

ntn_con = [
    BaseParam(name='connect', type=dict, default=dict(substructure_00=[0], INTERNAL=[1]), help='connexion to sub and nodes'),
    BaseParam(name='dirs', type=list, default=[0], help='connexion to sub and nodes')
]
m_con = [
    BaseParam(name='connect', type=str, default="substrucutre_00", help='connexion to sub'),
]

param_connectors = dict(
    GOElement=[
        BaseParam(name='type', type=str, default="GOElement", help='factory_keyword of the class'),
        BaseParam(name='dto', type=int, default=0, help='Order of the time derivative'),
        BaseParam(name='xo', type=int, default=1, help='power of the displacement'),
        BaseParam(name='k', type=float, default=1.0, help='rigidity of the element'),
    ]+ntn_con,
    LinearSpring=[
        BaseParam(name='type', type=str, default="LinearSpring", help='factory_keyword of the class'),
        BaseParam(name='k', type=float, default=1.0, help='rigidity of the element'),
    ]+ntn_con,
    LinearDamper=[
        BaseParam(name='type', type=str, default="LinearDamper", help='factory_keyword of the class'),
        BaseParam(name='k', type=float, default=1.0, help='rigidity of the element'),
    ]+ntn_con,
    CubicSpring=[
        BaseParam(name='type', type=str, default="CubicSpring", help='factory_keyword of the class'),
        BaseParam(name='k', type=float, default=1.0, help='rigidity of the element'),
    ]+ntn_con,
    GOForcing=[
        BaseParam(name='type', type=str, default="GOForcing", help='factory_keyword of the class'),
        BaseParam(name='ho', type=int, default=1, help='Order of the time derivative'),
        BaseParam(name='phi', type=float, default=0.0, help='phase between sine and cosine term'),
        BaseParam(name='amp', type=float, default=1.0, help='amplitude of the forcing'),
    ]+ntn_con,
    CosinusForcing=[
        BaseParam(name='type', type=str, default="CosinusForcing", help='factory_keyword of the class'),
        BaseParam(name='amp', type=float, default=1.0, help='amplitude of the forcing'),
    ]+ntn_con,
    SinusForcing=[
        BaseParam(name='type', type=str, default="SinusForcing", help='factory_keyword of the class'),
        BaseParam(name='amp', type=float, default=1.0, help='amplitude of the forcing'),
    ]+ntn_con,
    PenaltyUnilateralGap=[
        BaseParam(name='type', type=str, default="PenaltyUnilateralGap", help='factory_keyword of the class'),
        BaseParam(name='k', type=float, default=1.0, help='Added rigidity when gap closes'),
        BaseParam(name='gap', type=float, default=0.0, help='Initial size of the gap'),
    ]+ntn_con,
    Jenkins=[
        BaseParam(name='type', type=str, default="Jenkins", help='factory_keyword of the class'),
        BaseParam(name='k', type=float, default=1.0, help='Rigidity in stick conditions'),
        BaseParam(name='mu', type=float, default=0.3, help='friction coeficient'),
        BaseParam(name='N0', type=float, default=1.0, help='Constant normal force on the slider'),
    ]+ntn_con,
    Penalty3D=[
        BaseParam(name='type', type=str, default="Penalty3D", help='factory_keyword of the class'),
        BaseParam(name='k_n', type=float, default=1.0, help='Normal rigidity'),
        BaseParam(name='k_t', type=float, default=1.0, help='Tangential rigidity in stick conditions'),
        BaseParam(name='g', type=float, default=0.0, help='Rigidity in stick conditions'),
        BaseParam(name='mu', type=float, default=0.3, help='friction coeficient'),
        BaseParam(name='N0', type=float, default=1.0, help='Constant normal force on the slider at initial state'),
    ]+ntn_con,
    DLFTUniGap=[
        BaseParam(name='type', type=str, default="DLFTUniGap", help='factory_keyword of the class'),
        BaseParam(name='eps', type=float, default=1e3, help='Penalty coeficient of the DLFT formulation'),
        BaseParam(name='g', type=float, default=0.0, help='Initial gap size'),
    ]+ntn_con,
    DLFTFriction=[
        BaseParam(name='type', type=str, default="DLFTFriction", help='factory_keyword of the class'),
        BaseParam(name='eps', type=float, default=1e3, help='Penalty coeficient of the DLFT formulation'),
        BaseParam(name='mu', type=float, default=0.0, help='Friction coefficient'),
        BaseParam(name='N0', type=float, default=0.0, help='Constant normal force on the slider'),
    ]+ntn_con,
    DLFT3D=[
        BaseParam(name='type', type=str, default="DLFT3D", help='factory_keyword of the class'),
        BaseParam(name='eps', type=float, default=1e3, help='Penalty coeficient of the DLFT formulation'),
        BaseParam(name='mu', type=float, default=0.0, help='Friction coefficient'),
        BaseParam(name='N0', type=float, default=0.0, help='Constant normal force on the slider'),
        BaseParam(name='g', type=float, default=0.0, help='Initial gap size'),
    ]+ntn_con,
    # Matrix based connectors
    GOMatrix=[
        BaseParam(name='type', type=str, default="GOMatrix", help='factory_keyword of the class'),
        BaseParam(name='dto', type=int, default=0, help='Order of the time derivative'),
        BaseParam(name='dom', type=int, default=0, help='Order of the power applied to angular frequency', optional=True),
        BaseParam(name='matrix', type=str, default="to be filled with nd.array directly from python script", help='matrix contribution'),
    ]+m_con,
    linear_hysteretic=[
        BaseParam(name='type', type=str, default="GOMatrix", help='factory_keyword of the class'),
        BaseParam(name='matrix', type=str, default="to be filled with nd.array directly from python script", help='matrix contribution'),
    ]+m_con,
)

