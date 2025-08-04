import setuptools

setuptools.setup(
    name='disaggregation',
    version='0.1.0',
    description='Disaggregates in Pandas',
    author='Nathaniel Rogalsk   yj',
    author_email='nr282@cornell.edu',
    packages=setuptools.find_packages(),
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