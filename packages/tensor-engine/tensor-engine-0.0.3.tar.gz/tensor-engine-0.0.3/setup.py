from setuptools import setup, find_packages

setup(
    name="tensor-engine",
    version="0.0.3",
    author="MrPsyghost (Shivay)",
    author_email="shivaypuri2000@gmail.com",
    description="A really basic Terminal Game Engine built in Python.",
    # url="https://github.com/MrPsyghost/geo",
    project_urls={
        "YouTube": "https://www.youtube.com/@MrPsyghost",
        # "Bug Tracker": "https://github.com/MrPsyghost/geo/issues",
        # "Documentation": "https://github.com/MrPsyghost/geo/wiki",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        # "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    # install_requires=[
    #     "torch>=2.0.0",
    #     "matplotlib>=3.10.0",
    #     "rich>=13.0.0",
    #     "tqdm>=4.0.0"
    # ],
    python_requires=">=3.10",
    include_package_data=True,
    # license="MIT",
    keywords=[
        "game engine",
        "tensor engine",
        "terminal game engine",
        "terminal",
        "tensor",
        "game",
        "engine",
    ],
)
