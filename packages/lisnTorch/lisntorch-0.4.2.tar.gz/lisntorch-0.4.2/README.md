### 目录结构
wheel_demo/
│
├── README.md
├── wheel_demo/
│   ├── __init__.py
│   ├── module1.py
│   ├── module2.py
│   └── ...
│
├── tests/
│   ├── __init__.py
│   ├── test_module1.py
│   ├── test_module2.py
│   └── ...
│
├── setup.py
└── LICENSE

### 说明
依照 https://docs.pingcode.com/ask/1143811.html
如果不想安装, 可以直接复制到 S:\Python\Anaconda3\envs\env39\Lib 中使用

## Installation


```bash

pip install wheel
pip install twine
在模块的根目录下（即 setup.py 所在的目录），打开终端

# 普通安装

  python setup.py sdist bdist_wheel
  pip install .  
这会将 my_module 安装到 Python 环境中，使其可以在任何地方导入

# 开发中安装
[参考文章](https://blog.csdn.net/lydstory123/article/details/143353424)

如果你在开发中不断修改模块，想要在更改后自动生效，可以使用 pip 的开发模式进行安装
  python setup.py sdist bdist_wheel
  pip install -e .
此时安装的是模块的符号链接版本，修改源代码后无需重新安装。


# 打包上传
  python setup.py sdist bdist_wheel
  twine upload dist/*
其中需要apitoken, 保存到
  C:\Users\lishuainan\.pypirc
[pypi]
  username = __token__
  password = api token里面的东西