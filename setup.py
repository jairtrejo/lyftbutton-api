from setuptools import setup, find_packages

setup(
    name='lyftbutton',
    version='0.1',
    description='API for lyftbutton.com',
    url='http://lyftbutton.com',
    author='Jair Trejo',
    author_email='jair@jairtrejo.mx',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'lyft-rides==0.2',
        'attrs==18.2',
        'pyjwt==1.6.4',
        'structlog==18.2.0'
    ],
    zip_safe=False)
