from setuptools import setup

setup(
    name="PySFCGAL",
    version="2.2.0",
    description="Python binding of SFCGAL.",
    long_description="""Python binding of SFCGAL. SFCGAL is a C++ wrapper
    library around CGAL with the aim of supporting ISO 191007:2013 and OGC
    Simple Features for 3D operations.""",
    long_description_content_type='text/plain',
    url="https://gitlab.com/SFCGAL/pysfcgal",
    author="Joshua Arnott (initial work) and Loïc Bartoletti (Oslandia)",
    author_email="infos@sfcgal.org",
    license="GPL-3.0-or-later",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    packages=["pysfcgal"],
    package_data={"pysfcgal": ["*.c"]},
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["pysfcgal/sfcgal_build.py:ffibuilder"],
    install_requires=["cffi>=1.0.0"],
    extras_require={"contract": ["icontract>=2.6.0"]}
)
