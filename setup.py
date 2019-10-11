from importlib.machinery import SourceFileLoader

from setuptools import find_packages, setup

version = SourceFileLoader('version', 'hub/version.py').load_module()

install_requirements = [
    'boto3>=1.9.84,<2.0',
    'jsonpickle',
    'timeout-decorator>=0.4.1,<0.5',
    'boto',
]

test_requires = [
    'pytest',
    'pytest-cov',
    'black',
    'isort[pipfile]',
    'flake8',
    'moto==1.3.13',
    'jsonpickle',
]

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='hub-kinesis',
    version=version.__version__,
    author='Cuenca',
    author_email='dev@cuenca.com',
    description='Library for Kinesis Implementation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cuenca-mx/hub',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=install_requirements,
    setup_requires=['pytest-runner'],
    tests_require=test_requires,
    extras_require=dict(test=test_requires),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
