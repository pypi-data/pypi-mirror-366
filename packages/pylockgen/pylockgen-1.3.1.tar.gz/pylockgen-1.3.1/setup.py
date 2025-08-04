from setuptools import setup, find_packages

setup(
    name='pylockgen',
    version='1.3.1',
    author='Hadi Reza',
    author_email='hadiraza.9002@gmail.com',
    description='Secure password generator and strength checker',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/unknownmeovo/pylockgen",
    project_urls={
        "Bug Tracker": "https://github.com/unknownmeovo/pylockgen/issues",
    },
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        "Topic :: Security",
	"Topic :: Utilities"
    ],
    python_requires='>=3.6',
)
