from setuptools import setup


setup(
    name='cldfbench_phoible',
    py_modules=['cldfbench_phoible'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'cldfbench.dataset': [
            'phoible=cldfbench_phoible:Dataset',
        ],
    },
    install_requires=[
        'pyglottolog>=3.4.0',
        'cldfbench>=1.6.0',
        'clldutils>=3.7.0',
        'pycldf>=1.18.1',
        'pybtex>=0.24.0',
        'beautifulsoup4>=4.9.3',
        'csvw>=1.10.1'
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
