from setuptools import setup, find_packages

setup(
    name='bullfinch',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['flask'],
    author='Your Name',
    author_email='your@email.com',
    description='A lightweight web framework like StillSite',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/bullfinch',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Flask',
        'License :: OSI Approved :: MIT License'
    ],
)
