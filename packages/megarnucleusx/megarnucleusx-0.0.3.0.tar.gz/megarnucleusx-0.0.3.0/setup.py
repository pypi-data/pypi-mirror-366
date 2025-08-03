from setuptools import setup, find_packages

setup(
    name='megarnucleusx',
    version='0.0.3.0',
    # ... otros metadatos ...
    description='Un micro-framework de IA con una red neuronal profunda y autograd, impulsado por micronumpy.',
    # REQUISITO ACTUALIZADO
    install_requires=[
        'micronumpy>=0.1.1',
    ],
    # ... resto de clasificadores ...
)
