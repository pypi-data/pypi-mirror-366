from setuptools import setup, find_packages

setup(
    name='megarnucleusx',
    version='0.0.2.4',
    description='IA modular y portable sin dependencias externas obligatorias.',
    long_description=open('README.md').read(), # Es una buena práctica añadir un README.md
    long_description_content_type='text/markdown',
    author='TuNombre',
    author_email='tu@email.com',
    url='https://github.com/TuUsuario/megarnucleusx', # Añade la URL de tu repo
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", # Considera añadir una licencia
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.6',
    # No hay 'install_requires', ¡ese es el objetivo!
)
