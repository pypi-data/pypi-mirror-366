import setuptools

setuptools.setup(
    name='disaggregation',
    version='0.5.0',
    description='Disaggregates in Pandas',
    author='Nathaniel Rogalskyj',
    author_email='nr282@cornell.edu',
    packages=["disaggregation"],
    install_requires=[
        'requests',
        'numpy>=1.20',
        'pandas',
        'scipy',
        'coverage',
        'matplotlib',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)