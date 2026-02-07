from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ml-pipeline-template",
    version="1.0.0",
    author="ML Pipeline Template Contributors",
    author_email="contact@ml-pipeline-template.dev",
    description="Production-Ready ML Pipeline Template",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ml-pipeline-template",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/ml-pipeline-template/issues",
        "Documentation": "https://github.com/yourusername/ml-pipeline-template/docs",
        "Source Code": "https://github.com/yourusername/ml-pipeline-template",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ml-pipeline=src.cli.main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "ml-pipeline": [
            "config/*.yaml",
            "web/templates/*.html",
            "web/static/css/*.css",
            "web/static/js/*.js",
        ],
    },
)
