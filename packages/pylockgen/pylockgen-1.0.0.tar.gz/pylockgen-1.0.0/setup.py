from setuptools import setup, find_packages

setup(
    name='pylockgen',
    version='1.0.0',
    author='Hadi Raza',
    author_email='hadiraza.9002@gmail.com',
    description='Secure password generator and strength checker',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
