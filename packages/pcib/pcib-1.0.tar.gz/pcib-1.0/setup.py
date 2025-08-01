from setuptools import setup, find_packages

setup(
    name="pcib",
    version="1.0",
    author="flamecode",
    description="Python cURL-like library - аналог curl для Python",
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.1',
    ],
    entry_points={
        'console_scripts': [
            'pcib=pcib.core:main',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)