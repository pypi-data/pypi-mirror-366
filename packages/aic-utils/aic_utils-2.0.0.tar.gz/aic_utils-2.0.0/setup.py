# setup.py

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='aic_utils',
    version='2.0.0',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0',
        'PyYAML>=5.4.0',
        'pandas>=1.3.0',
        'slack_sdk>=3.0.0',
    ],
    author='Dylan D',
    author_email='dylan.doyle@jdpa.com',
    description='AIC API wrapper and GitLab integration framework for pipeline management',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dylandoyle11/aic_utils', 
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    keywords='aic gitlab pipeline automation devops',
)


