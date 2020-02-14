from setuptools import setup, find_packages

setup(name='TWitter Profile Scrapper',
      version='0.1.0',
      packages=find_packages(),
      entry_points={'console_scripts': ['twitter-profile-scrapper= etl.cli:main']},
      install_requires=[
          'click',
          'sqlalchemy',
          'psycopg2-binary',
          'requests=',
          'pytest',
          'pytest-cov',
          'pylint',
          'pytest-dotenv',
        ],
      description='Tool that given a set of ids, download information about it',
      author='Gradiant',
      author_email='diegoreiriz@gmail.com',
      keywords=['Twitter', 'scrapper', 'ETL', 'tool'])
