import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="easy-pil",
    version="0.0.4",
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
    ],
    keywords="Pillow, PIL, Pillow wrapper, PIL wrapper, Easy Pillow, Easy PIL, discord rank card, discord card",
    packages=find_packages(),
    package_data={
        "easy_pil": ["fonts/*/*.ttf"],
    },
    python_requires=">=3.6, <4",
    install_requires=["Pillow>=8.3.1", "requests>=2.26.0", "aiohttp>=3.7.4"],
    project_urls={
        "Bug Reports": "https://github.com/shahriyardx/easy-pil/issues",
        "Source": "https://github.com/shahriyardx/easy-pil/",
    },
)
