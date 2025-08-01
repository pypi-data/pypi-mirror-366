from setuptools import setup, find_packages

setup(
    name='moex-wrapper',
    version='0.1.0',
    packages=find_packages(),
    author='Aist Tech',
    author_email='aisttechco@gmail.com',
    description='A production-ready wrapper for the Moscow Exchange API',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AistTech/MOEX_Wrapper',
    license='MIT',
    install_requires=[
        'requests',
        'pandas',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial :: Investment'
    ],
    python_requires='>=3.7',
) 