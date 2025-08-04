# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['itptest']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.116.1,<0.117.0']

setup_kwargs = {
    'name': 'itptest',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'kirshuvl',
    'author_email': 'kirshuvl@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
