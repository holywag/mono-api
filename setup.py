from setuptools import setup

setup(
    name='monobank',
    version='1.0',
    package_dir={'': 'src'},
    py_modules=['monobank'],
    install_requires=[
        'requests',
        'requests_toolbelt'
    ],
)
