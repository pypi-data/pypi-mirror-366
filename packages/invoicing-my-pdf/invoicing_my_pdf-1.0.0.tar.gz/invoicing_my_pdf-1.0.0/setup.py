from setuptools import setup


setup(
    name="invoicing-my-pdf",  # * Your package will have this name
    packages=["invoicing"],  # * Name the package again
    version="1.0.0",  # * To be increased every time your change your library
    license="MIT",  # Type of license. More here: https://help.github.com/articles/licensing-a-repository
    description="This package can be used to convert Excel invoices to PDF invoices.",  # Short description of your library
    author="Muhammad Abdullah",
    author_email="ma.email@example.com",  # Your email
    url="https://example.com",  # Homepage of your library (e.g. github or your website)
    keywords=["invoice", "excel", "pdf"],  # Keywords users can search on pypi.org
    install_requires=[
        "pandas",
        "fpdf",
        "openpyxl",
    ],  # Other 3rd-party libs that pip needs to install
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
# PythonStudent123$-AgEIcHlwaS5vcmcCJDdlMGZkNTQwLThhNWQtNDQwZi04MjgyLTY1ZGU2ZjI3YWQ3MwACKlszLCIzMGYyMDc1Yy00ZjRlLTQyN2MtOTZhNy01NDMxOTcxNTE0YWIiXQAABiAZoyE2Kh-nOi-uujaZqZYyIF2AJ-Za8ezeHejiKSLxNw
