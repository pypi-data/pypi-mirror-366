from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='dymachandran',
    version='0.0.2',
    license='GNU GENERAL PUBLIC LICENSE',
    license_files = "LICENSE",
    author='Nata Nobre',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='natanobre0605@gmail.com',
    keywords='ramachadran',
    description=u'ramachandran plotter for molecular dynamics',
    packages=['dymachandran'],
    install_requires=['numpy', 'pandas', 'plotly.express',
                       'argparse', 'Pillow', 'MDAnalysis', 'progressbar2', 'requests'],
    entry_points={"console_scripts": ["dymachandran = dymachandran:main"]})
