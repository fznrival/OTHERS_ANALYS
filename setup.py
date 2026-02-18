from setuptools import setup, find_packages

setup(
    name="others_analysis",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
    ],
    python_requires=">=3.7",
    author="ICT Analysis",
    description="OTHERS analysis tool based on ICT (Inner Circle Trader) methodology",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
)
