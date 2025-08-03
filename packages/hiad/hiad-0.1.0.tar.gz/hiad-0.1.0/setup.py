import os

import pkg_resources
from setuptools import setup, find_packages

setup(
    name="hiad",
    version="0.1.0",
    description="high-resolution anomaly detection",
    author="cnulab",
    url="https://github.com/cnulab/HiAD",
    author_email="2024010482@bupt.cn",
    packages=find_packages(),
    install_requires=[
        'torch>=1.10',
        'torchvision',
        'torchmetrics',
        'numpy',
        'PyYAML',
        'easydict',
        'opencv-python',
        'Pillow',
        'scikit-learn',
        'scikit-image',
        'imgaug',
        'tabulate',
        'kornia',
        'matplotlib',
        'timm==0.8.15.dev0',
        'FrEIA',
        'geomloss',
        'pandas',
        'grad_cam'
    ],
    python_requires='>=3.8',
    include_package_data=True,
    extras_require={
        'cuda': ['faiss-gpu'],
        'cuda11': ['faiss-gpu-cu11'],
        'cuda12': ['faiss-gpu-cu12'],
    }

)