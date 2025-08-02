#!/usr/bin/env python
# -*- coding:utf-8 -*-


#############################################
# File Name: setup.py
# Author: Cai Jianping
# Mail: jpingcai@163.com
# Created Time:  2025-08-01 22:47:43
#############################################


from setuptools import setup, find_packages

setup(
    name="myexp",
    version="0.0.0",
    keywords=["experiment", "deploy"],
    description="`myexp` is a Python library that simplifies the deployment, management, and execution of research experiments. It allows researchers to easily configure, deploy, and run experiments with flexible environment management and automation.",
    long_description="`myexp` is a Python library aimed at providing researchers with an easy-to-use toolkit for managing and executing experiment tasks. Whether it's machine learning experiments, data analysis tasks, or other types of research experiments, `myexp` enables users to quickly set up experiment environments, manage experiment configurations, and automate experiment execution. By integrating with `pip` and virtual environments, `myexp` ensures that each experiment runs in a consistent and controlled environment, avoiding issues related to inconsistent environment setups. The library is designed to be highly modular, supporting user-defined experiment configuration files such as hyperparameters, dataset paths, model configurations, and more. Users can not only manage experiment dependencies flexibly but also schedule experiment tasks, monitor progress, and collect results seamlessly.",
    license="MIT Licence",
    author="Cai Jianping",
    author_email="jpingcai@163.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["uv"],
    entry_points={}
)
