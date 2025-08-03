# __init__.py该文件的作用就是相当于把自身整个文件夹当作一个包来管理，每当有外部import的时候，就会自动执行里面的函数。
# __all__ = ['viewData']
# 这是主模块下的子模块, 需要时使用 import 主模块名.子模块.py名 as py名  然后使用 py名.函数名即可使用函数
# import viewData as viewData
# 这样 就可以lisntorch.viewdata使用了, 不这样写, 需要import lisntorch.viewdata as viewdata
from lisntorch import (
    viewdata as viewdata,
    presets as presets,
    evaluation as evaluation,
    )