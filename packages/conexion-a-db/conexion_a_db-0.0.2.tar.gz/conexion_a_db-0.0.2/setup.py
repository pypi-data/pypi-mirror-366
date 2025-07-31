from setuptools import setup, find_packages

setup(
    name='conexion_a_db',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[],
    author='Gerardo Rios Navarrete',
    author_email='gerardoriosn@gmail.com',
    description='Una librería para conectarse a bases de datos fácilmente.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/tu_usuario/conexion_a_db',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
