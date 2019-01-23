from setuptools import setup
from gecrypt import VERSION


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='git-easy-crypt',
    version=VERSION,
    description='The easy way to encrypt/decrypt private files in the git repo.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Version Control :: Git',
    ],
    keywords='git encrypt decrypt',
    url='https://github.com/taojy123/git-easy-crypt',
    author='tao.py',
    author_email='taojy123@163.com',
    license='MIT',
    py_modules=['gecrypt'],
    entry_points={
        'console_scripts': ['gecrypt=gecrypt:main'],
    },
    include_package_data=True,
    zip_safe=False,
)
