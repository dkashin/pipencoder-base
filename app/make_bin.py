
import os

from setuptools import find_packages, setup, Extension
from distutils.sysconfig import get_config_var
from Cython.Distutils import build_ext
from Cython.Build import cythonize


def get_ext_filename_without_platform_suffix(filename):
    name, ext = os.path.splitext(filename)
    ext_suffix = get_config_var('EXT_SUFFIX')

    if ext_suffix == ext:
        return filename

    ext_suffix = ext_suffix.replace(ext, '')
    idx = name.find(ext_suffix)

    if idx == -1:
        return filename
    else:
        return name[:idx] + ext


class BuildExtWithoutPlatformSuffix(build_ext):
    def get_ext_filename(self, ext_name):
        filename = super().get_ext_filename(ext_name)
        return get_ext_filename_without_platform_suffix(filename)


setup(
  name = 'main',
  version='2.4.6',
  cmdclass = { 'build_ext': BuildExtWithoutPlatformSuffix },
  ext_modules = cythonize(
    [
      Extension('main.*', [ 'run.py' ]),
      Extension('main.*', [ 'main/*/*.py' ]),
      Extension('main.*', [ 'main/*/*.py' ])
    ],
    build_dir = 'build',
#    exclude = [ '**/__init__.py', 'smooth' ],
    nthreads = 8,
    compiler_directives = {
      'language_level' : "3",
      'always_allow_keywords': True
    }
  ),
  packages = find_packages()
#  packages = []
)

