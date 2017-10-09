from distutils.core import setup

setup(
    name='PyInstagram',
    version='0.1.8',
    packages=['pyinstagram'],
    url='www.alessandrocucci.it',
    license='MIT',
    author='Alessandro Cucci',
    author_email='alessandro.cucci@gmail.com',
    description='Instagram Scraping',
    install_requires=[
            "requests==2.18.4",
            "sqlalchemy==1.1.14",
    ]
)
