from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-schedulerx",
    version="0.1.0",
    author="firatmio",
    author_email="",
    description="A lightweight and simple task scheduler for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/firatmio/py-schedulerx",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    keywords="scheduler, cron, task, job, automation, periodic, threading",
    project_urls={
        "Bug Reports": "https://github.com/firatmio/py-schedulerx/issues",
        "Source": "https://github.com/firatmio/py-schedulerx",
        "Documentation": "https://github.com/firatmio/py-schedulerx#readme",
    },
    include_package_data=True,
)
