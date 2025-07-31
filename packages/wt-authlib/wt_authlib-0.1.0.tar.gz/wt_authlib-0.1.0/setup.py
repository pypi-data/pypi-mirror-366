from setuptools import setup, find_packages

setup(
    name='wt-authlib',
    version='0.1.0',
    packages=find_packages(where='wt_authlib'),
    package_dir={'': 'wt_authlib'},
    description='Librairie d\'authentification pour les apis WT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='David Libert',
    python_requires='>=3.12',
    install_requires=[
        'fastapi>=0.115.0',
        'pyjwt[crypto]>=2.10.1',
        'redis>=6.2.0',
        'aiohttp>=3.12.13',
        'pydantic>=2.11.7'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)