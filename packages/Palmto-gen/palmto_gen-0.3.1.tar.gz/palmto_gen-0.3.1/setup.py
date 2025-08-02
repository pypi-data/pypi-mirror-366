from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='Palmto_gen',
    version='0.3.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'Palmto_gen': ['data/*'],
    },
    description='Generate synthetic trajectories using PLMs',
    long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.md').read(),
    long_description_content_type='text/markdown',
    url='',
    author='Hayat Sultan, Joey Cherisea', 
    author_email='hayatsul@ualberta.ca, hai.p@northeastern.edu',
    license='MIT',
    classifiers = classifiers,
    keywords='trajectory generation' 'Probablistic Language Models',
    install_requires= ['geopandas', 'tqdm', 'geopy', 'scipy', 'folium'],
    project_urls={
        'Documentation': 'https://palmto-gen.readthedocs.io/en/latest/',
        'Source': 'https://github.com/HayatSultan/PaLMTo-Gen',
        'Bug Reports': 'https://github.com/HayatSultan/PaLMTo-Gen/issues'
    }
)