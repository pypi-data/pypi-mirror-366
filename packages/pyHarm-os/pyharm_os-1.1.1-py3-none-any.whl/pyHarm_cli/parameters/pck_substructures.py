from pyHarm_cli.parameters.BaseParam import BaseParam


param_substructures = dict(
    onlydofs=[
        BaseParam(name='type', type=str, default="onlydofs", help='factory_keyword of the class'),
        BaseParam(name='nnodes', type=int, default=1, help='number of nodes'),
        BaseParam(name='nmodes', type=int, default=0, help='number of modal coordinates'),
        BaseParam(name='ndofs', type=int, default=3, help='number of dofs per node'),
        BaseParam(name='matching', type=list, default=[0,1,2], help='list dof matching to the global coordinate system', optional=True),
    ],
    substructure = [
        BaseParam(name='type', type=str, default="substructure", help='factory_keyword of the class'),
        BaseParam(name='filename', type= str, default="./sub_00.mat", help='path to the file containing the substructure matrices'),
        BaseParam(name='ndofs', type=int, default=3, help='number of dofs per node'),
        BaseParam(name='reader', type=str, default='generic', help='name of the file reader and parser', optional=True),
        BaseParam(name='nmodes', type=int, default=0, help='number of modal coordinates', optional=True),
        BaseParam(name='matching', type=list, default=[0,1,2], help='list dof matching to the global coordinate system ', optional=True),
    ]
)

