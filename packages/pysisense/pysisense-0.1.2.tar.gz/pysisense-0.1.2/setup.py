from setuptools import setup, find_packages
import os

long_description = open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else ""

setup(
    name='pysisense',
    version='0.1.2',
    license="MIT",
    author='Himanshu Negi',
    author_email='himanshu.negi.08@gmail.com',
    description='A Python SDK for interacting with Sisense API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hnegi01/pysisense',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pyyaml',
        'pandas'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    include_package_data=True,
    keywords="Sisense API SDK analytics BI",
    project_urls={
        "Documentation": "https://github.com/hnegi01/pysisense/tree/main/docs",
        "Source": "https://github.com/hnegi01/pysisense",
        "Issues": "https://github.com/hnegi01/pysisense/issues",
    },
)
