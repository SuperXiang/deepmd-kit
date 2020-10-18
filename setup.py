from skbuild import setup
from skbuild.exceptions import SKBuildError
from skbuild.cmaker import get_cmake_version
from setuptools_scm import get_version
from packaging.version import LegacyVersion
from os import path, makedirs
import os, importlib, sys, platform, sysconfig


readme_file = path.join(path.dirname(path.abspath(__file__)), 'README.md')
try:
    from m2r import parse_from_file
    readme = parse_from_file(readme_file)
except ImportError:
    with open(readme_file) as f:
        readme = f.read()

install_requires=['numpy', 'scipy', 'pyyaml']
setup_requires=['setuptools_scm', 'scikit-build']

def find_tf(path):
    return importlib.machinery.FileFinder(path).find_spec("tensorflow")

extras_require = dict()
tf_spec = importlib.util.find_spec("tensorflow")
if tf_spec:
    tf_install_dir = tf_spec.submodule_search_locations[1]
else:
    site_packages_path = path.join(path.dirname(path.__file__), 'site-packages')
    tf_spec = importlib.machinery.FileFinder(path).find_spec("tensorflow")
    if tf_spec:
        tf_install_dir = tf_spec.submodule_search_locations[1]
    else:
        tf_version = os.environ.get('TENSORFLOW_VERSION', '2.3')
        setup_requires.append("tensorflow==" + tf_version)
        extras_require = {"cpu": "tensorflow_cpu==" + tf_version, "gpu": "tensorflow==" + tf_version}

# add cmake as a build requirement if cmake>3.7 is not installed
try:
    if LegacyVersion(get_cmake_version()) < LegacyVersion("3.7"):
        setup_requires.append('cmake')
except SKBuildError:
    setup_requires.append('cmake')

try:
    makedirs('deepmd')
except OSError:
    pass


setup(
    name="deepmd-kit",
    setup_requires=setup_requires,
    use_scm_version={'write_to': 'deepmd/_version.py'},
    author="Han Wang",
    author_email="wang_han@iapcm.ac.cn",
    description="A deep learning package for many-body potential energy representation and molecular dynamics",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/deepmodeling/deepmd-kit",
    packages=['deepmd'],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    ],
    keywords='deepmd',
    install_requires=install_requires,        
    cmake_args=['-DTENSORFLOW_ROOT:STRING=%s' % tf_install_dir, 
                '-DBUILD_PY_IF:BOOL=TRUE', 
                '-DBUILD_CPP_IF:BOOL=FALSE',
                '-DFLOAT_PREC:STRING=high',
    ],
    cmake_source_dir='source',
    cmake_minimum_required_version='3.0',
    extras_require={
        'test': ['dpdata>=0.1.9'],
        **extras_require,
    },
    entry_points={
          'console_scripts': ['dp = deepmd.main:main']
    }
)
