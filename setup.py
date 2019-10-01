import setuptools

install_requirements = [
    'jsonpickle'
    'boto3>=1.9.84,<2.0'
]

test_requires = [
    'pytest>=4.2.1,<4.3.0'
    'pycodestyle'
    'coveralls'
    'moto==1.3.13'
    'jsonpickle'
]

setuptools.setup(
    name='hub',
    version='0.1.1',
    author='Cuenca',
    author_email='dev@cuenca.com',
    description='Library for Kinesis Implementation',
    long_description='Library for Kinesis Implementation',
    long_description_content_type='text/markdown',
    url='https://github.com/cuenca-mx/hub',
    setup_requires=['pytest-runner'],
    install_requires=install_requirements,
    tests_require=test_requires,
    extras_require=dict(test=test_requires),
)
