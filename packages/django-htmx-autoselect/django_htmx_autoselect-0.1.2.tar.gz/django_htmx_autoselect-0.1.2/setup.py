from setuptools import find_packages, setup

setup(
    name="django-htmx-autoselect",
    version="0.1.2",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="A reusable Django app to display notifications.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dw-liedji/django-htmx-autoselect",
    author="Your Name",
    author_email="liedjiwenkack@gmail.com",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "Django>=3.2",
    ],
)
