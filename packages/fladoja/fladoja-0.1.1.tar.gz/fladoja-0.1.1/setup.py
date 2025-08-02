from setuptools import setup, find_packages
from pathlib import Path

# Чтение README.md
current_dir = Path(__file__).parent
long_description = (current_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="fladoja",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    
    # Лицензия и авторство
    license="SiteProjectGo",
    license_files=("LICENSE",),
    author="Vadim",
    author_email="somerare22@gmail.com",
    
    # Описание
    description="Hybrid web framework (Flask + Django + FastAPI style)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fladoja",
    
    # Классификаторы PyPI
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    
    # Зависимости и требования
    python_requires=">=3.7",
    install_requires=[
        "python-dotenv>=1.0.0",
    ],
    
    # Данные пакета
    package_data={
        "fladoja": [
            "templates/*.html",
            "templates/admin/*.html",
            "templates/errors/*.html",
            "static/*",
        ],
    },
    entry_points={
        "console_scripts": [
            "fladoja=fladoja.cli:main",
        ],
    },
)