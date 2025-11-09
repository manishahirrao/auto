from setuptools import setup, find_packages

setup(
    name="selenium_login_automation",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "selenium>=4.10",
        "pytest>=7.0",
        "pytest-html>=3.2",
        "python-dotenv>=1.0",
    ],
    python_requires=">=3.10",
)
