from setuptools import setup, find_packages

setup(
    name='topsis_abhiraj_singh_jhajj_102217094',  # Updated package name
    version='1.0.6',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.18.0',
        'pandas>=1.0.0',
        'openpyxl>=3.0.0'
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'topsis=topsis_Abhiraj_102217094.topsis:main',  # Updated entry point
        ],
    },
    author='Abhiraj Singh Jhajj',  # Updated author name
    author_email='abhirajsinghjhajj@gmail.com',  # Updated email
    description='TOPSIS implementation for multi-criteria decision analysis',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/abhirajsinghjhajj/Topsis_Abhiraj_Singh_Jhajj_102217094',  # Updated GitHub URL
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
