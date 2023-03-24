#!/usr/bin/env python
import json
import os
import shutil
import sys

import pyct.build

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.sdist import sdist

PANEL_LITE_BUILD = 'PANEL_LITE' in os.environ


def get_setup_version(reponame):
    """
    Helper to get the current version from either git describe or the
    .version file (if available).
    """
    basepath = os.path.split(__file__)[0]
    version_file_path = os.path.join(basepath, reponame, '.version')
    try:
        from param import version
    except Exception:
        version = None
    if version is not None:
        return version.Version.setup_version(basepath, reponame, archive_commit="$Format:%h$")
    else:
        print("WARNING: param>=1.6.0 unavailable. If you are installing a package, "
              "this warning can safely be ignored. If you are creating a package or "
              "otherwise operating in a git repository, you should install param>=1.6.0.")
        return json.load(open(version_file_path, 'r'))['version_string']


def _build_paneljs():
    from bokeh.ext import build

    from panel.compiler import bundle_resources
    print("Building custom models:")
    panel_dir = os.path.join(os.path.dirname(__file__), "panel")
    build(panel_dir)
    print("Bundling custom model resources:")
    bundle_resources()
    if sys.platform != "win32":
        # npm can cause non-blocking stdout; so reset it just in case
        import fcntl
        flags = fcntl.fcntl(sys.stdout, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdout, fcntl.F_SETFL, flags&~os.O_NONBLOCK)


class CustomDevelopCommand(develop):
    """Custom installation for development mode."""

    def run(self):
        if not PANEL_LITE_BUILD:
            _build_paneljs()
        develop.run(self)


class CustomInstallCommand(install):
    """Custom installation for install mode."""

    def run(self):
        if not PANEL_LITE_BUILD:
            _build_paneljs()
        install.run(self)


class CustomSdistCommand(sdist):
    """Custom installation for sdist mode."""

    def run(self):
        if not PANEL_LITE_BUILD:
            _build_paneljs()
        sdist.run(self)


_COMMANDS = {
    'develop': CustomDevelopCommand,
    'install': CustomInstallCommand,
    'sdist':   CustomSdistCommand,
}

try:
    from wheel.bdist_wheel import bdist_wheel

    class CustomBdistWheelCommand(bdist_wheel):
        """Custom bdist_wheel command to force cancelling qiskit-terra wheel
        creation."""

        def run(self):
            """Do nothing so the command intentionally fails."""
            if not PANEL_LITE_BUILD:
                _build_paneljs()
            bdist_wheel.run(self)

    _COMMANDS['bdist_wheel'] = CustomBdistWheelCommand
except Exception:
    pass

########## dependencies ##########

install_requires = [
    'panel >=1.0.0a1'
]

_tests = [
    # Test dependencies
    'parameterized',
    'pytest',
    'nbval',
    'flaky',
    'pytest-xdist',
    'pytest-cov',
    'pre-commit',
    'psutil',
]

_ui = [
    'playwright',
    'pytest-playwright'
]

extras_require = {
    'tests': _tests,
    'recommended': _recommended,
    'doc': _recommended + [
        'nbsite >=0.8.0rc7',
        'pydata-sphinx-theme ==0.9.0',
        'sphinx-copybutton',
        'sphinx-design',
    ],
    'ui': _ui
}

extras_require['all'] = sorted(set(sum(extras_require.values(), [])))

# Superset of what's in pyproject.toml (includes non-python
# dependencies).  Also, pyproject.toml isn't supported by all tools
# anyway (e.g. older versions of pip, or conda - which also supports
# non-python dependencies). Note that setup_requires isn't used
# because it doesn't work well with pip.
extras_require['build'] = [
    'param >=1.9.2',
    'pyct >=0.4.4',
    'setuptools >=42',
    'requests',
    'packaging',
    'bokeh >=3.1.0.dev3',
    'panel >=1.0.0a1',
    'pyviz_comms >=0.7.4',
]

setup_args = dict(
    name='panel_gwalker',
    version=get_setup_version("panel_gwalker"),
    description='A Panel extension for the graphic-walker library.',
    long_description=open('README.md', encoding="utf8").read() if os.path.isfile('README.md') else 'Consult README.md',
    long_description_content_type="text/markdown",
    author="HoloViz",
    author_email="philipp@holoviz.org",
    maintainer="HoloViz",
    maintainer_email="developers@holoviz.org",
    platforms=['Windows', 'Mac OS X', 'Linux'],
    license='BSD',
    url='http://panel.holoviz.org',
    project_urls={
        'Source': 'https://github.com/holoviz/panel',
    },
    cmdclass=_COMMANDS,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Other Audience",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Office/Business",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries"],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'panel = panel.command:main'
        ]
    },
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=extras_require['tests']
)

def clean_js_version(version):
    version = version.replace('-', '')
    for dev in ('a', 'b', 'rc'):
        version = version.replace(dev+'.', dev)
    return version

if __name__ == "__main__":
    example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'panel', 'examples')

    if 'develop' not in sys.argv and 'egg_info' not in sys.argv:
        pyct.build.examples(example_path, __file__, force=True)

    version = setup_args['version']
    if 'post' not in version:
        with open('./panel_gwalker /package.json') as f:
            package_json = json.load(f)
        js_version = package_json['version']
        version = version.split('+')[0]
        if any(dev in version for dev in ('a', 'b', 'rc')) and not '-' in js_version:
            raise ValueError(f"panel.js dev versions ({js_version}) must "
                             "must separate dev suffix with a dash, e.g. "
                             "v1.0.0rc1 should be v1.0.0-rc.1.")
        if version != 'None' and version != clean_js_version(js_version):
            raise ValueError(f"panel.js version ({js_version}) does not match "
                             f"panel version ({version}). Cannot build release.")

    setup(**setup_args)

    if os.path.isdir(example_path):
        shutil.rmtree(example_path)
