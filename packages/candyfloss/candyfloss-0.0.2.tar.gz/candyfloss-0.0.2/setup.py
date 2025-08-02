from distutils.core import setup, Extension
from setuptools import find_packages
import subprocess as sp

EXTRA_COMPILE_ARGS = ['-O3']
#EXTRA_COMPILE_ARGS = ['-g', '-O0', '-fsanitize=leak'],

def extension_with_deps(ext_name, ext_sources, dep_packages, libs_flags):
    include_dirs = []
    lib_dirs = []
    libs = []
    state = (include_dirs, lib_dirs, libs)
    state_switches = ('-I', '-L', '-l')
    for pkg_name in dep_packages:
        for part in sp.check_output(['pkg-config', '--cflags', '--libs', pkg_name]).decode('utf-8').split():
            for i, switch in enumerate(state_switches):
                if part.startswith(switch):
                    state[i].append(part[len(switch):])
    return Extension(ext_name,
        extra_compile_args=EXTRA_COMPILE_ARGS,
        sources=ext_sources,
        include_dirs=include_dirs,
        library_dirs=lib_dirs,
        libraries=libs + libs_flags)

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='candyfloss',
    description='An ergonomic interface to GStreamer',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(include=['candyfloss']),
    install_requires=['Pillow'],
    ext_modules=[extension_with_deps(
        'c_candyfloss', 
        ['native/py_entrypoint.c'], 
        ['gstreamer-1.0', 'gstreamer-base-1.0', 'gstreamer-video-1.0'],
        ['pthread'])])
    
