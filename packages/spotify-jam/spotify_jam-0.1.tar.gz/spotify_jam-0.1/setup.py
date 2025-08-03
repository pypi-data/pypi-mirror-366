from setuptools import setup, find_packages

setup(
    name='spotify-jam',
    description='spotify-jam is a package that allows you to manage Spotify Jams',
    version='0.1',
    packages=find_packages(),
    install_requirements=[
        'requests==2.32.4'
    ],
)