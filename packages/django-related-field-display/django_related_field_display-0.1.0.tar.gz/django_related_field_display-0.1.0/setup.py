from setuptools import setup, find_packages

setup(
    name='django-related-field-display',
    version='0.1.0',
    description='A Django admin mixin for displaying related fields with clickable links.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Sezer Bozkir',
    author_email='admin@sezerbozkir.com',
    url='https://github.com/natgho/django-related-field-display',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[
        'Django>=3.2',
    ],
    python_requires='>=3.9',
)