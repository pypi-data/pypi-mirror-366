from setuptools import setup, find_packages

setup(
    name='megarnucleusx',
    version='0.0.5.0',
    author='TuNombre',
    author_email='tu@email.com',
    description='Una IA modular de alto nivel con bots pre-configurados, impulsada por sminitorch y micronumpy.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/TuUsuario/megarnucleusx',
    packages=find_packages(),
    install_requires=[
        'sminitorch>=0.1.0',
        # micronumpy es una dependencia de sminitorch, así que no es estrictamente necesaria aquí
        # pero es bueno ser explícito.
        'micronumpy>=0.1.2',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Development Status :: 4 - Beta",
    ],
    python_requires='>=3.6',
)

