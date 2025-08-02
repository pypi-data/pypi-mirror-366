from setuptools import setup, find_packages
from pathlib import Path

readme_path = Path(__file__).parent / "README.md"
try:
    long_description = readme_path.read_text(encoding="utf-8")
except Exception as e:
    long_description = "Fladoja - hybrid web framework"
    print(f"Couldn't read README.md: {e}")

setup(
    name="fladoja",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    license="SiteProjectGo",
    author="Vadim",
    author_email="somerare22@gmail.com",
    description="Flask + Django + FastAPI hybrid framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/fladoja/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    test_suite="tests",
    install_requires=[],
)