from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(
    name='pavdedutor',
    version='0.0.3',
    license='MIT',
    author='Wellington Moura',
    author_email='pro.wmoura@gmail.com',
    description='Otimizador de uso de ábacos de valores deduzíveis para análise de patologias em pavimentos rígidos e flexíveis',
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords='dnit pavimento norma ábaco rígido flexível',
    packages=['pavdedutor'],
    install_requires=['pandas', 'numpy'],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)