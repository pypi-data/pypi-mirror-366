from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="nnea",       # 包名（PyPI唯一标识，需全小写）
    version="0.1.2",               # 版本号（每次更新需递增）
    packages=find_packages(),    # 自动包含所有包
    description="A biological inform neural network",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Chuwei Liu",
    author_email="liuchw26@mail.sysu.edu.cn",
    url="https://github.com/liuchuwei/nnea",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "torch>=1.9.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "toml>=0.10.0",
        "h5py>=3.1.0",
        "scipy>=1.7.0",
        "imbalanced-learn>=0.8.0",
        "networkx>=2.6.0",
        "pyyaml>=5.4.0",
        "umap-learn>=0.5.0",
        "plotly>=5.0.0",
        "shap>=0.40.0",
        "lime>=0.2.0"
    ],
    python_requires='>=3.6',     # Python版本要求
)