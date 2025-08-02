from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="FileTo_Tools",
    version="0.1.4",  
    author="WusRainy",
    author_email="3644365070@qq.com",
    description="Advanced file and directory operations toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.com/WusRainy/FileTo_Tools", 
    license="MIT",
    
    packages=find_packages(include=["FileTo_Tools", "FileTo_Tools.*"]),
    package_dir={"": "."},  
    
    python_requires=">=3.6",
    install_requires=[ 
        "pathlib2>=2.3.7;python_version<'3.4'",  # 旧版Python兼容
    ],
    
    include_package_data=True,
    package_data={
        "FileTo_Tools": ["*.txt", "*.md"],
    },
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries",
    ],
    
    
    project_urls={
        "Bug Reports": "https://github.com/your_username/FileTo_Tools/issues",
        "Source": "https://github.com/your_username/FileTo_Tools",
    },
)