from setuptools import setup, find_packages

setup(
    name='banguard-api',
    version='0.1.1',
    author='Zyrafaq',
    author_email='contact@zyrafaq.com',
    description='Python API wrapper for BanGuard API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/zyrafaq/BanGuard-API/',
    packages=find_packages(),
    license='GPL-3.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
