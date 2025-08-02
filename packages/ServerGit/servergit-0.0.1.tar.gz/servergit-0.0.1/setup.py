from setuptools import setup

with open("README.md", encoding="utf-8") as arq:
    readme = arq.read()

setup(
    name='ServerGit',
    version='0.0.1',
    license='MIT License',
    author='João Victor',
    author_email='ajaxbytestudio@gmail.com',
    description='Serve não oficial do GitHub!',
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords='ServerGit',
    packages=['ServerGit'],
    install_requires=[
        'PyGithub',
        'pandas',
    ],
)
