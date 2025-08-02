import setuptools

setuptools.setup(
    name="req_pre_automate1",
    version="0.0.3",
    packages=setuptools.find_packages(),
    author="Rajesh Kanumuru",
    description="Dont install this package, purely testing purpose",
    entry_points={
        'console_scripts': [
            'req_pre_automate1 = http_query.http_query:main'
        ]
    },
    install_requires= [
        'click',
        'requests'
    ]
)
