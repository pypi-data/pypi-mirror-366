from setuptools import setup, find_packages

setup(
    name='megarnucleusx',
    version='0.0.2.5',
    author='luis',
    author_email='gachaprimosxd128@gmail.com',
    description='Un micro-framework de IA autónomo con bots pre-entrenados y compatibilidad fantasma, sin dependencias externas.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/TuUsuario/megarnucleusx',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Development Status :: 4 - Beta", # Hemos avanzado a Beta!
    ],
    python_requires='>=3.6',
)
