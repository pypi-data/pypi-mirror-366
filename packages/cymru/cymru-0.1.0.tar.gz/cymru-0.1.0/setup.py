from setuptools import setup

setup(
    name="cymru",
    version="0.1.0",
    description="Cymru API wrapper for Python",
    url="https://github.com/FernandoDoming/cymru",
    author="Fernando Domínguez",
    author_email="6620286+FernandoDoming@users.noreply.github.com",
    license="GNU GPL v3",
    packages=[
        "cymru",
    ],
    install_requires = [
        "requests>=2.32.4",
    ],
    
    tests_require = [
        "responses>=0.25.7"
    ],

    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],

    entry_points = {
    },

    scripts=[
    ],
)