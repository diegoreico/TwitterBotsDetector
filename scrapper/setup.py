from setuptools import setup, find_packages

setup(
    name="TWitter Profile Scrapper",
    version="0.1.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["twitter-profile-scrapper= scrapper.cli:main"]},
    install_requires=[
        "Click==7.0",
        "SQLAlchemy==1.3.13",
        "psycopg2-binary==2.8.4",
        "requests==2.22.0",
        "pandas==1.0.1",
        "pytest==5.3.5",
        "pytest-cov==2.8.1",
        "pylint==2.4.4",
        "pytest-dotenv==0.4.0",
        "python-dotenv==0.11.0",
        "black==19.10b0",
        "tweepy==3.8.0",
    ],
    description="Tool that given a set of ids, download information about it",
    author="Gradiant",
    author_email="diegoreiriz@gmail.com",
    keywords=["Twitter", "scrapper", "ETL", "tool"],
)
