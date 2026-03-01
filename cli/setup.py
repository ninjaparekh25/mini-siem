from setuptools import setup

setup(
    name='monitor',
    version='1.0.0',
    py_modules=['cli'],
    install_requires=['click'],
    entry_points={
        'console_scripts': [
            'monitor=cli:monitor',
        ],
    },
)
