import setuptools

setuptools.setup(
    name='Disaggregation',
    version='0.2.0',
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
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)