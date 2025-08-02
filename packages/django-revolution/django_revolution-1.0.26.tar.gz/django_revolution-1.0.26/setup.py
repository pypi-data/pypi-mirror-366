import setuptools
from pathlib import Path

# Read pyproject.toml
pyproject_path = Path(__file__).parent / "pyproject.toml"

try:
    import tomllib  # Python 3.11+

    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)
except ImportError:
    import toml

    with open(pyproject_path, "r", encoding="utf-8") as f:
        pyproject = toml.load(f)

project = pyproject["project"]

setuptools.setup(
    name=project["name"],
    version=project["version"],
    description=project.get("description", ""),
    long_description=(Path(__file__).parent / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author=project["authors"][0]["name"] if project.get("authors") else None,
    author_email=project["authors"][0]["email"] if project.get("authors") else None,
    url=pyproject.get("project", {}).get("urls", {}).get("Homepage", None),
    project_urls=pyproject.get("project", {}).get("urls", {}),
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires=project.get("requires-python", ">=3.9"),
    install_requires=project.get("dependencies", []),
    extras_require=pyproject.get("project", {}).get("optional-dependencies", {}),
    classifiers=project.get("classifiers", []),
    keywords=project.get("keywords", []),
    entry_points={
        "console_scripts": [
            "django-revolution=django_revolution.cli:main",
        ],
    },
    zip_safe=False,
)
