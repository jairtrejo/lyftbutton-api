from setuptools import find_packages, setup

setup(
    name="lyftbutton",
    version="0.1",
    description="API for lyftbutton.com",
    url="http://lyftbutton.com",
    author="Jair Trejo",
    author_email="jair@jairtrejo.mx",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "attrs==18.2",
        "google-api-python-client==1.7.4",
        "oauth2client==4.1.3",
        "lyft-rides==0.2",
        "PyJWT==1.6.4",
        "structlog==18.2.0",
    ],
    zip_safe=False,
)
