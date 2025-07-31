from setuptools import find_packages, setup

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Definable - Infrastructure for building and deploying AI agents"

setup(
    name="definable",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0",
        "pydantic>=2.0.0",
        "click>=8.0.0",
        "docker>=6.0.0",
        "PyYAML>=6.0.0",
        "Jinja2>=3.0.0",
        "urllib3>=1.26.0,<2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "definable=definable.cli.main:cli",
        ],
    },
    python_requires=">=3.9",
    author="Definable Team",
    author_email="team@definable.ai",
    description="Infrastructure for building and deploying AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/definable/definable",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    include_package_data=True,
    package_data={
        "definable": ["templates/*.jinja2"],
    },
)
