from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from setuptools import find_packages, setup

current_directory = Path(__file__).parent.resolve()


def _get_requirements() -> list:
    with open("requirements.txt") as f:
        return f.read().splitlines()


def _get_long_desc() -> str:
    return (current_directory / "README.md").read_text(encoding="utf-8")


def _get_version() -> str:
    vpath = current_directory / "easy_pil" / "_version.py"
    spec = spec_from_file_location(vpath.name[:-3], vpath)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)

    return mod.__version__


setup(
    name="easy-pil",
    version=_get_version(),
    description="A library to make common tasks of Pillow easy.",  # Optional
    long_description=_get_long_desc(),
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
    install_requires=_get_requirements(),
    extras_require={
        "dev": ["black", "isort", "click", "twine"],
    },
    project_urls={
        "Documentation": "https://easy-pil.readthedocs.io/en/latest/",
        "Bug Reports": "https://github.com/shahriyardx/easy-pil/issues",
        "Source": "https://github.com/shahriyardx/easy-pil/",
    },
)
