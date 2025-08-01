from setuptools import setup, find_packages

setup(
    name='autoflowml',
    version='0.1.0',
    author='Leelavinothan A',
    author_email='leelavinothan900@gmail.com',
    description='An end-to-end Python library for automated data preprocessing and model selection, designed to streamline ML workflows',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Leelavinothan12',  
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    license="MIT",
    python_requires='>=3.7',
    install_requires=[
        'scikit-learn>=1.1.0',
        'evalml>=0.40.0',
        'pandas>=1.3.0',
        'numpy>=1.21.0',
        'joblib>=1.1.0',
        'category_encoders>=2.3.0',
    ]
    
)
