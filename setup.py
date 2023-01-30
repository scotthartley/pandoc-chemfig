from setuptools import setup


def readme():
    with open("README.rst") as file:
        return file.read()


setup(name="pandoc-chemfig",
      version="2.0",
      description=("Figure support for chemists in pandoc, with "
                   "cross-referencing and wrapping"),
      long_description=readme(),
      author="Scott Hartley",
      author_email="scott.hartley@miamioh.edu",
      url="https://hartleygroup.org",
      license="MIT",
      scripts=["pandoc-chemfig"],
      packages=["pandoc_chemfig"],
      install_requires=["pandocfilters"],
      python_requires=">=3",
      )
