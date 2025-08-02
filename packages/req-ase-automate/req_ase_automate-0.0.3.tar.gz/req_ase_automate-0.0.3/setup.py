import setuptools

setuptools.setup(
    name="req_ase_automate",
    version="0.0.3",
    packages=setuptools.find_packages(),
    author="Rajesh Kanumuru",
    description="Dont install this package, purely testing purpose",
    entry_points={
        'console_scripts': [
            'req_ase = http_query.http_query:main'
        ]
    },
    install_requires= [
        'click',
        'requests'
    ]
)
