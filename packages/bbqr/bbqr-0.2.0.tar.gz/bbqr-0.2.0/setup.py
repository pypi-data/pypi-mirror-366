from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name='bbqr',
    version='0.2.0',
    description='🔥 BBQR - The hottest terminal-based QR code generator that grills your data to perfection!',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ishman Singh',
    url='https://github.com/foglomon/bbqr',
    py_modules=['bbqr'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bbqr=bbqr:main',
        ],
    },
    install_requires=requirements,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Utilities',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Networking',
        'Environment :: Console',
    ],
    keywords='qr qrcode generator terminal cli bbq barcode wifi upload',
    project_urls={
        'Bug Reports': 'https://github.com/foglomon/bbqr/issues',
        'Source': 'https://github.com/foglomon/bbqr',
        'Documentation': 'https://github.com/foglomon/bbqr#readme',
    },
    include_package_data=True,
    zip_safe=False,
)