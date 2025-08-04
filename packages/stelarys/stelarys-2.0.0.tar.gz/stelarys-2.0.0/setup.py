from setuptools import setup, find_packages

setup(
    name='stelarys',
    version='2.0.0',
    packages=find_packages(),
    install_requires=[
        'wcwidth',
        'pypresence',
        'mccolors',
        'colorama',
        'requests',
        'bs4',
        'dnspython',
        'whois',
        'packaging'
    ],
    author='Pablo',
    author_email='follaonlineconmariaa2kmdetucasa@gmail.com',
    description='Una herramienta god por q me mide 20cm',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Pabloescobarxde/Stelarys-V2',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Cambia si usas otra
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
