from setuptools import setup

version_file = open('VERSION', 'r')
version = version_file.readline()

setup(
    name='scrap-utils',
    version=version,
    packages=['requester'],
    url='https://github.com/westial/scrap-utils',
    license='GPL v3',
    author='Jaume Mila',
    author_email='jaume@westial.com',
    description='Python utils for scraping purposes.',
    install_requires=[
        'urllib3',
        'certifi',
        'cookiejar'
    ]
)
