from setuptools import setup

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='xztools',
    version='0.2.1',
    packages=['xztools'],
    description='A fun library with time utilities and random compliments!',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Your Name',
    author_email='your_email@example.com',
    keywords='time countdown weekend month year utilities fun',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.6',
)