from pyHarm_cli.parameters.BaseParam import BaseParam

_basic_export_config = [
        BaseParam(name='export_path', type=str, default=".", help='Export path folder'),
        BaseParam(name='datetime', type=bool, default=False, help='with date time to avoid rewrite'),
]
param_export = dict(
    export_results=[
        BaseParam(name='status', type=bool, default=True, help='Do we export results as csv files'),
    ] + _basic_export_config,
    donot_export_results=[
        BaseParam(name='status', type=bool, default=False, help='Do we export results as csv files'),
    ]+ _basic_export_config,
)