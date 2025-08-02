from setuptools import setup, find_packages

setup(
    name="BayesMCDM",
    version="0.1.0",
    description="Bayesian Multi-Criteria Decision Making Toolkit",
    author="Majid Mohammadi",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pystan",  
    ],
)   