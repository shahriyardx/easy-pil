from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

current_directory = Path(__file__).parent.resolve()

long_description = (current_directory / "README.md").read_text(encoding="utf-8")

vpath = current_directory / "easy_pil" / "_version.py"
spec = spec_from_file_location(vpath.name[:-3], vpath)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)

setup(
    name="easy-pil",
    version=mod.__version__,
    description="A library to make common tasks of Pillow easy.",  # Optional
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shahriyardx/easy-pil",
    author="Md Shahriyar Alam",
    author_email="contact@shahriyar.dev",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="Pillow, PIL, Pillow wrapper, PIL wrapper, Easy Pillow, Easy PIL, discord rank card, discord card",
    packages=find_packages(),
    package_data={
        "easy_pil": ["fonts/*/*.ttf"],
    },
    python_requires=">=3.7, <4",
    install_requires=requirements,
    project_urls={
        "Documentation": "https://easy-pil.readthedocs.io/en/latest/",
        "Bug Reports": "https://github.com/shahriyardx/easy-pil/issues",
        "Source": "https://github.com/shahriyardx/easy-pil/",
    },
)
