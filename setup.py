import re # toml not available at install time on slapos

from pathlib import Path
from setuptools import setup


_pyproj = Path("./pyproject.toml").read_text(encoding="utf8")
setup(
    name="abilian-sbe",
    version=re.search(r'version *= *"(.*)"' , _pyproj).group(1),
    package_dir={"": "src"},
    packages=["abilian", "extranet"],
)
