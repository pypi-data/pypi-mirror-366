from setuptools import setup, find_packages

setup(
    name='bullfinch',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    author='Vadim',
    author_email='somerare22@gmail.com',
    description='A lightweight web framework like StillSite',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Flask',
        'License :: OSI Approved :: MIT License'
    ],
)
