from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='bdgd2dss',
    version='0.0.5',
    license='MIT License',
    author='Arthur Gomes de Souza',
    author_email='arthurgomesba@gmail.com',
    maintainer='Wellington Maycon Santos Bernardes',
    maintainer_email='wmsbernardes@ufu.br',
    description=u'Ferramenta para modelagem de alimentadores da BDGD para uso com OpenDSS',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='bdgd2dss bdgd',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        'colorama==0.4.6',
        'et_xmlfile==2.0.0',
        'numpy==2.2.5',
        'openpyxl==3.1.5',
        'pandas==2.2.3',
        'py-dss-interface==1.0.2',
        'python-dateutil==2.9.0.post0',
        'pytz==2025.2',
        'six==1.17.0',
        'tzdata==2025.2'
    ],
)
