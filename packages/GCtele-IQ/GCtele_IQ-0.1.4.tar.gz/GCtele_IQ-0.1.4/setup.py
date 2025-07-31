from setuptools import setup, find_packages

setup(
    name="GCtele_IQ",
    version="0.1.4",
    description="一个面向运营商领域的人机测评工具，支持本地与API模型评估",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    license_files=["LICENSE.txt"],
    author="GuoChuang",
    author_email="wang.yingying@ustcinfo.com",
    url="https://github.com/zsjslab/GCtele_IQ",  
    packages=find_packages(),
    install_requires=[
        "pandas",
        "tqdm",
        "openai",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
