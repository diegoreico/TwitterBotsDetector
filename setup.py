from setuptools import setup, find_packages

setup(
    name='TwitterBotDetector',
    version='1.0.0',
    description='Twitter Bot Detector',
    long_description=(
        'Twitter Bot Detector'
    ),
    author='Diego Reiriz Cores',
    author_email='dreiriz@gmail.com',
    keywords=['Bot', 'Twitter', 'Detector'],
    entry_points={'console_scripts': ['botdetector = botdetector.cli:main']},
    install_requires=[
        'click',
        'Flask',
        'numpy',
        'pandas',
        'scikit-learn',
        'tensorflow',
        'requests',
        'beautifulsoup4',
        'tweepy',
        'PyMySQL',
        'pytest',
        'pytest-cov',
        'pylint',
        'pytest-dotenv',
        'pytest-mock',
        'python-dotenv',
    ],
    packages=find_packages(),
    license='UNLICENSED'
)
