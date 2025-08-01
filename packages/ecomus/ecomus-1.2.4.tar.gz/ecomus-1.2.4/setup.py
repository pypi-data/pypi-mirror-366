from setuptools import setup,find_packages
import sys
 
includeFiles = ["*"]
setup(
    name='ecomus',
    description='Replace unicode emojis by its corresponding image representation. supports unicode 9 standard.',
    long_description=open("README.md", 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    version='1.2.4',
    packages=find_packages(),
    package_data={
        'ecomus': includeFiles,
    },
    include_package_data=True,
    author='kubet',
    author_email='kubet@atomicmail.io',
    license='Apache License 2.0'
)
