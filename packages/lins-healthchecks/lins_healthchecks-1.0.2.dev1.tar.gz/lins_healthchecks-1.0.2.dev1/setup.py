from os import environ

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='lins_healthchecks',
    version=environ.get('BITBUCKET_TAG', '0.0.1'),
    author='Diego Magalhães',
    author_email='dmlmagal@gmail.com',
    description='Pacote que integra containers do docker ao sistema de healthcheck da lins-ferrão',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/grupolinsferrao/lins-health-check',
    packages=setuptools.find_packages(),
    install_requires=['requests', 'pytz'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
