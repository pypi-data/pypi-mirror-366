from setuptools import setup, find_packages

setup(
    name='teslapython',
    version='0.1.1',
    author='TeslaPython Software Foundation',
    packages=find_packages(),
    install_requires=[  
    
    ],
    entry_points={
        'console_scripts': [
            'teslapython=teslapython.main:teslapython',
        ],
    },
)