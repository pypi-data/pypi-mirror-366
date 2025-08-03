from setuptools import setup, find_packages

setup(
    name='megarnucleusx',
    version='0.0.2.2',
    description='Una micro IA evolucionada para Termux con entrenamiento básico y sin dependencias externas complicadas',
    author='Luis Fernando Montaño Hernandez',
    author_email='tu_correo@example.com',
    packages=find_packages(),
    install_requires=[
        'numpy'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
