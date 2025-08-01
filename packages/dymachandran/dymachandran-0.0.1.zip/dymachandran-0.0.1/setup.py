from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='dymachandran',
    version='0.0.1',
    license='GNU GENERAL PUBLIC LICENSE',
    author='Nata Nobre',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='natanobre0605@gmail.com',
    keywords='ramachadran',
    description=u'ramachandran plotter for molecular dynamics',
    packages=['dymachandran'],
    install_requires=['numpy', 'pandas', 'plotly.express',
                       'argparse', 'PIL', 'MDAnalysis', 'multiprocessing', 'progressbar2', 'requests'],)
