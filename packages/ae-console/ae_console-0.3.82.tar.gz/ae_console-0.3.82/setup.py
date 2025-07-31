# THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.tpl_project V0.3.36
""" setup of ae namespace module portion console: console application environment. """



# noinspection PyUnresolvedReferences
import setuptools

setup_kwargs = {
    'author': 'AndiEcker',
    'author_email': 'aecker2@gmail.com',
    'classifiers': ['Development Status :: 3 - Alpha', 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)', 'Natural Language :: English', 'Operating System :: OS Independent', 'Programming Language :: Python', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.9', 'Topic :: Software Development :: Libraries :: Python Modules'],
    'description': 'ae namespace module portion console: console application environment',
    'extras_require': {'dev': ['aedev_tpl_project', 'ae_ae', 'anybadge', 'coverage-badge', 'aedev_git_repo_manager', 'flake8', 'mypy', 'pylint', 'pytest', 'pytest-cov', 'pytest-django', 'typing', 'types-setuptools', 'wheel', 'twine'], 'docs': [], 'tests': ['anybadge', 'coverage-badge', 'aedev_git_repo_manager', 'flake8', 'mypy', 'pylint', 'pytest', 'pytest-cov', 'pytest-django', 'typing', 'types-setuptools', 'wheel', 'twine']},
    'install_requires': ['ae_base', 'ae_paths', 'ae_core', 'ae_literal', 'pyjnius'],
    'keywords': ['configuration', 'development', 'environment', 'productivity'],
    'license': 'OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'long_description': '<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project ae.ae V0.3.96 -->\n<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.tpl_namespace_root V0.3.14 -->\n# console 0.3.82\n\n[![GitLab develop](https://img.shields.io/gitlab/pipeline/ae-group/ae_console/develop?logo=python)](\n    https://gitlab.com/ae-group/ae_console)\n[![LatestPyPIrelease](\n    https://img.shields.io/gitlab/pipeline/ae-group/ae_console/release0.3.81?logo=python)](\n    https://gitlab.com/ae-group/ae_console/-/tree/release0.3.81)\n[![PyPIVersions](https://img.shields.io/pypi/v/ae_console)](\n    https://pypi.org/project/ae-console/#history)\n\n>ae namespace module portion console: console application environment.\n\n[![Coverage](https://ae-group.gitlab.io/ae_console/coverage.svg)](\n    https://ae-group.gitlab.io/ae_console/coverage/index.html)\n[![MyPyPrecision](https://ae-group.gitlab.io/ae_console/mypy.svg)](\n    https://ae-group.gitlab.io/ae_console/lineprecision.txt)\n[![PyLintScore](https://ae-group.gitlab.io/ae_console/pylint.svg)](\n    https://ae-group.gitlab.io/ae_console/pylint.log)\n\n[![PyPIImplementation](https://img.shields.io/pypi/implementation/ae_console)](\n    https://gitlab.com/ae-group/ae_console/)\n[![PyPIPyVersions](https://img.shields.io/pypi/pyversions/ae_console)](\n    https://gitlab.com/ae-group/ae_console/)\n[![PyPIWheel](https://img.shields.io/pypi/wheel/ae_console)](\n    https://gitlab.com/ae-group/ae_console/)\n[![PyPIFormat](https://img.shields.io/pypi/format/ae_console)](\n    https://pypi.org/project/ae-console/)\n[![PyPILicense](https://img.shields.io/pypi/l/ae_console)](\n    https://gitlab.com/ae-group/ae_console/-/blob/develop/LICENSE.md)\n[![PyPIStatus](https://img.shields.io/pypi/status/ae_console)](\n    https://libraries.io/pypi/ae-console)\n[![PyPIDownloads](https://img.shields.io/pypi/dm/ae_console)](\n    https://pypi.org/project/ae-console/#files)\n\n\n## installation\n\n\nexecute the following command to install the\nae.console module\nin the currently active virtual environment:\n \n```shell script\npip install ae-console\n```\n\nif you want to contribute to this portion then first fork\n[the ae_console repository at GitLab](\nhttps://gitlab.com/ae-group/ae_console "ae.console code repository").\nafter that pull it to your machine and finally execute the\nfollowing command in the root folder of this repository\n(ae_console):\n\n```shell script\npip install -e .[dev]\n```\n\nthe last command will install this module portion, along with the tools you need\nto develop and run tests or to extend the portion documentation. to contribute only to the unit tests or to the\ndocumentation of this portion, replace the setup extras key `dev` in the above command with `tests` or `docs`\nrespectively.\n\nmore detailed explanations on how to contribute to this project\n[are available here](\nhttps://gitlab.com/ae-group/ae_console/-/blob/develop/CONTRIBUTING.rst)\n\n\n## namespace portion documentation\n\ninformation on the features and usage of this portion are available at\n[ReadTheDocs](\nhttps://ae.readthedocs.io/en/latest/_autosummary/ae.console.html\n"ae_console documentation").\n',
    'long_description_content_type': 'text/markdown',
    'name': 'ae_console',
    'package_data': {'': []},
    'packages': ['ae'],
    'project_urls': {'Bug Tracker': 'https://gitlab.com/ae-group/ae_console/-/issues', 'Documentation': 'https://ae.readthedocs.io/en/latest/_autosummary/ae.console.html', 'Repository': 'https://gitlab.com/ae-group/ae_console', 'Source': 'https://ae.readthedocs.io/en/latest/_modules/ae/console.html'},
    'python_requires': '>=3.9',
    'setup_requires': ['aedev_setup_project'],
    'url': 'https://gitlab.com/ae-group/ae_console',
    'version': '0.3.82',
    'zip_safe': True,
}

if __name__ == "__main__":
    setuptools.setup(**setup_kwargs)
    pass
