from setuptools import setup


setup(
    name="panel-codes-twine",
    version="0.0.0",
    py_modules=['app'],
    entry_points='''
    [console_scripts]
    octue-app=app:octue_app
    ''',
    install_requires=[
        "numpy",
        "octue>=0.1.19",
    ]
)
