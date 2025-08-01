from setuptools import setup,find_packages
import sys
 
includeFiles = ["*"]
setup(
    name='lavajung',
    description='a basic emoji package',
    long_description=open("README.md", 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    version='1.3',
    packages=find_packages(),
    package_data={
        'lavajung': includeFiles,
    },
    include_package_data=True,
    author='kubet',
    author_email='kubet@atomicmail.io',
    license='Apache License 2.0'
)