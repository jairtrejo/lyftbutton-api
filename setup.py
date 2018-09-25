from setuptools import setup

setup(
    name='lyftbutton',
    version='0.1',
    description='API for lyftbutton.com',
    url='http://lyftbutton.com',
    author='Jair Trejo',
    author_email='jair@jairtrejo.mx',
    license='MIT',
    packages=['lyftbutton'],
    install_requires=[
        'lyft-rides==0.2',
        'attrs==18.2'
    ],
    zip_safe=False)
