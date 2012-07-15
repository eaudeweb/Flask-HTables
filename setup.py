import distutils.core

distutils.core.setup(
    name='Flask-HTables',
    version='0.1',
    py_modules=['flask_htables'],
    include_package_data=True,
    install_requires=[
        'Flask >= 0.8',
        'htables',
    ],
)
