#!/usr/bin/env python
import os
import subprocess
import platform

from setuptools import find_packages, setup, Extension
from Cython.Build import cythonize


def get_git_tag():
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.STDOUT
        ).decode().strip()
        return tag.lstrip('v')
    except subprocess.CalledProcessError:
        # Fallback to VERSION file if present (for sdist installs without .git)
        version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
        if os.path.exists(version_file):
            with open(version_file, 'r') as vf:
                return vf.read().strip()
        return "0.0.0"


def get_all_py_files(base_dir):
    py_files = []
    for dirpath, _, filenames in os.walk(base_dir):
        for file in filenames:
            if file.endswith(".py") and file != "__init__.py":
                py_files.append(os.path.join(dirpath, file))
    return py_files


# Create Extension objects to preserve directory structure
def create_extensions(base_dir):
    extensions = []
    for py_file in get_all_py_files(base_dir):
        # Convert path to module name (e.g., agentfoundry/agents/api_base.py -> agentfoundry.agents.api_base)
        module_name = py_file.replace(os.sep, '.')[:-3]  # Remove .py
        # Output .so file in the same directory as .py
        if platform.system() == "Windows":
            ext_suffix = ".cp311-win_amd64.pyd"
        else:
            ext_suffix = ".cpython-311-x86_64-linux-gnu.so"

        for py_file in get_all_py_files(base_dir):
            module_name = py_file.replace(os.sep, '.')[:-3]
            output_path = py_file[:-3] + ext_suffix
            extensions.append(
                Extension(
                    module_name,
                    [py_file],
                )
            )
        return extensions

    return extensions


ext_modules = cythonize(
    create_extensions("agentfoundry"),
    compiler_directives={"language_level": "3"},
    build_dir="build"
)

dist_name = "agentfoundry"
if os.getenv("AGENTFOUNDRY_ENFORCE_LICENSE", "1") == "0":
    dist_name += "-nolicense"

setup(
    name=dist_name,
    version=get_git_tag(),
    ext_modules=ext_modules,
    packages=find_packages(include=["agentfoundry*"]),
    include_package_data=True,
    exclude_package_data={
        "": ["*.py", "*.pyc"],
    },
    package_data={
        "agentfoundry": ["__init__.py", "*.so", "agentfoundry.lic", "agentfoundry.pem"],
        "agentfoundry.agents": ["*.so"],
        "agentfoundry.agents.tools": ["*.so"],
        "agentfoundry.chroma": ["*.so"],
        "agentfoundry.code_gen": ["*.so"],
        "agentfoundry.llm": ["*.so"],
        "agentfoundry.license": ["*.py", "*.so"],
        "agentfoundry.registry": ["*.so"],
        "agentfoundry.utils": ["*.so"],
        "agentfoundry.agents": ["__init__.py", "*.pyd"],
        "agentfoundry.agents.tools": ["__init__.py", "*.pyd"],
        "agentfoundry.chroma": ["__init__.py", "*.pyd"],
        "agentfoundry.code_gen": ["__init__.py", "*.pyd"],
        "agentfoundry.llm": ["__init__.py", "*.pyd"],
        "agentfoundry.license": ["__init__.py", "*.pyd", "public.pem"],
        "agentfoundry.registry": ["__init__.py", "*.pyd"],
        "agentfoundry.utils": ["__init__.py", "*.pyd"],
        # Include default configuration template unencrypted
        "agentfoundry.resources": ["default_agentfoundry.toml"],
    },
    zip_safe=False,
)
