from setuptools import setup, find_packages

setup(
    name="xlizard",
    version="1.0.4",
    packages=find_packages(include=['xlizard', 'xlizard_ext*']),
    package_data={'xlizard': ['xlizard_ext/*', 'xlizard_languages/*'],},
    install_requires=[
    'jinja2>=3.1.3',
    'tqdm>=4.66.2',
    'pathspec>=0.12.1',
    'lxml>=5.1.0',
    'pygments>=2.17.2',
    'chardet>=5.2.0',
    'psutil>=5.9.8',
    'multiprocess>=0.70.16',  # Для лучшей многопоточной обработки
    'colorama>=0.4.6',        # Для цветного вывода в консоли
],
    entry_points={
        "console_scripts": [
            "xlizard = xlizard.xlizard:main",  # Связывает команду xlizard с вашим скриптом
        ],
    },
    description="Extended Lizard with additional static code analysis features",
    author="Xor1no",
    license="Proprietary",  
)