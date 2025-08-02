# 哎呀卧槽, 直接和setup.py同级的py文件 会被塞到 S:\Python\Anaconda3\envs\env39\Lib\site-packages 下
# 而非我想的根目录放到site-packages下
from setuptools import setup, find_packages
print(find_packages())
# packages.extend(["viewData.py","presets.py","evaluation.py"])
setup( 
    name='lisnTorch',              # name：包的名称。
    version='0.4.1',               # version：包的版本。
    author='lishuainan',           #author和author_email：包的作者信息。
    author_email='lishuainan0209@qq.com;lishuainan0209@163.com',
    description='用于机器学习的辅助工具包',# description：简短的描述。
    # long_description=open('README.md',encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    # url='https://github.com/yourusername/my_project',
    packages=find_packages(), #packages：包含包的列表，使用find_packages()自动查找。# ! 暂时用不到包
    # py_modules=["viewData","presets","evaluation"], # 不属于任何包。我必须在单独的参数中提供它的模块名称 
    classifiers=[# classifiers：分类信息，帮助用户和工具找到你的包。
        'Programming Language :: Python :: 3', 
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6', #python_requires：指定需要的Python版本。
    install_requires=[ #install_requires：指定包的依赖项。确保指定的依赖项版本是稳定和受支持的。
        # 'matplotlib>=3.5.1',
        'matplotlib',
        'numpy',
        "torch",
        "pandas",
        "numpy",
        "torchsummary",
        "thop",
        "pygame",
    ],
)