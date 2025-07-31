from setuptools import setup, find_packages

setup(
    name='multisom',
    version='0.1.2',
    author='E.Bringa-F.Aquistapace-SiMaF',
    author_email='tatoaquista@gmail.com',
    license='MIT',
    description='Multilayer algorithm of Self Organising Maps (also known as Kohonen Networks) implemented in Python for clustering of atomistic samples through unsupervised learning. The program allows the user to select wich per-atom quantities to use for training and application of the network, this quantities must be specified in the LAMMPS input file that is being analysed. ',
    url='https://github.com/SIMAF-MDZ/MultiSOM',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[ 'pandas','numpy','joblib '],
    include_package_data=True,
)
