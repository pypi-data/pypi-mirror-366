from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='NetDes',
    version='1.0.6',
    packages=find_packages(),  
    description='Network modeling based on dynamic equation simulation (NetDes)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Yukai You',
    author_email='you.yu@northeastern.edu',
    url='https://github.com/lusystemsbio/NetDes',
    download_url='https://github.com/lusystemsbio/NetDes/archive/refs/heads/main.zip',
    keywords=['NetDes', 'TF', 'ODE', 'GRN', 'trajectories'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    license_files=['LICENSE.txt'],
    python_requires='>=3.9',
    install_requires=[
        'numpy>=1.26.4',
        'torch>=1.12.1',
        'matplotlib>=3.5.1',
        'pandas>=2.2.2',
        'scipy>=1.13.1',
        'scikit-learn>=1.0.2'
    ],
)
