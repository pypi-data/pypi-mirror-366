from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-predictor",
    version="1.0.0",
    author="MCP Predictor Team",
    author_email="your-email@example.com",
    description="Simple Time Series Prediction Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/mcp-predictor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.20.0",
        "prophet>=1.1.0",
        "lightgbm>=4.0.0",
        "scikit-learn>=1.0.0",
        "PyYAML>=6.0",
        "ibm-db>=3.2.0",
        "optuna>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mcp-predictor=mcp_predictor:predict",
        ],
    },
) 