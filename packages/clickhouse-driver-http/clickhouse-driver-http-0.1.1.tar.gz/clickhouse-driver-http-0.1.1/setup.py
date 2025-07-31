from setuptools import setup, find_packages

setup(
    name="clickhouse-driver-http",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "pandas>=1.3.0; extra == 'pandas'"
    ],
    extras_require={
        "pandas": ["pandas>=1.3.0"],
    },
    author="Nikita Krachkovskiy",
    author_email="sudokns@gmail.com",
    description="Lightweight HTTP client for ClickHouse",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords=["clickhouse", "http", "driver", "database"],
)