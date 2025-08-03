import setuptools

setuptools.setup(
    name="bh_usa_automate_req_ase",
    version="0.0.3",
    packages=setuptools.find_packages(),
    author="Rajesh Kanumuru",
    description="Dont install this package, purely testing purpose",
    entry_points={
        'console_scripts': [
            'bh_usa_automate_req_ase = http_query.http_query:main'
        ]
    },
    install_requires= [
        'click',
        'requests'
    ]
)
