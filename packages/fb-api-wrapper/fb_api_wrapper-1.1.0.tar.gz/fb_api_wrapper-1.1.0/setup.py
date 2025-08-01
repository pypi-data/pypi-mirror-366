import os
from distutils.core import setup, Extension
from Cython.Build import cythonize
def get_ext_paths(root_dir, exclude_files):
    """get filepaths for compilation"""
    paths = []
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if os.path.splitext(filename)[1] != '.py':
                continue

            file_path = os.path.join(root, filename)
            if file_path in exclude_files:
                continue

            paths.append(file_path)
    print(paths)
    return paths
setup(
    name='fb_api_wrapper',
    version='1.1.0',
    ext_modules=cythonize(
        get_ext_paths('fb_api_wrapper', ""),
        compiler_directives={'language_level': 3}
    ),
    )