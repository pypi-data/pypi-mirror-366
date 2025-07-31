from setuptools import setup,find_packages
import sys
 
includeFiles = ["__init__.py", "lanus.pyz"]
setup(
    name='lanus',
    description='a basic package',
    long_description=open("README.md", 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    version='1.1.0',
    packages=find_packages(),
    package_data={
        'lanus': includeFiles,
    },
    include_package_data=True,
    author='kubet',
    author_email='kubet@atomicmail.io',
    license='Apache License 2.0'
)
