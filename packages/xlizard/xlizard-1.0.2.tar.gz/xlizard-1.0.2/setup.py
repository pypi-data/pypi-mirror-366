from setuptools import setup, find_packages

setup(
    name="xlizard",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[],  
    entry_points={
        "console_scripts": [
            "xlizard = xlizard.xlizard:main",  # Связывает команду xlizard с вашим скриптом
        ],
    },
    description="Extended Lizard with additional static code analysis features",
    author="Xor1no",
    license="Proprietary",  
)