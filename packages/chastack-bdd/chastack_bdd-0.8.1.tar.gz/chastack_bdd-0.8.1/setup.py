from setuptools import setup, find_packages

setup(
    name='chastack-bdd',
    description="setuptools.build_meta",
    version='0.8.1',
    author           = 'Hernán A. Teszkiewicz Novick',
    author_email     = 'herni@cajadeideas.ar',
    url= 'https://github.com/Hernanatn/bdd.py',
    packages=['bdd', 'bdd.errores','bdd.tipos', 'usuario'],
)