from setuptools import setup, find_packages

name = 'html_parsing_dqa'
version = '0.1.6'
install_requires = [
    'bs4',
    'tika',
    'datetime',
    'python-dateutil',
    'jieba',
    'simhash'
]


setup(
    name = name,
    version = version,
    # url = 'https://code.devops.xiaohongshu.com/jinlei1/mmidls',
    author = 'jinqiu',
    author_email = 'jinqiu@xiaohongshu.com',
    description = 'utils for html parsing',
    packages = find_packages(),
    zip_safe = True,
    include_package_data = True,
    install_requires = install_requires,
)

