from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()


setup(
    name='teslapython',
    version='0.1.5',
    author='TeslaPython Software Foundation',
    packages=find_packages(),
    install_requires=[  
    
    ],
    entry_points={
        'console_scripts': [
            'teslapython=teslapython.main:teslapython',
        ],
    },
    long_description=description,
    long_description_content_type='text/markdown',
)