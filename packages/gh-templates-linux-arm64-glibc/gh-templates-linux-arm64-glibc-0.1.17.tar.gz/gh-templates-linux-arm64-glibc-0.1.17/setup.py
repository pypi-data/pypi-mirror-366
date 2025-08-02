from setuptools import setup
setup(
    name='gh-templates-linux-arm64-glibc',
    version='0.1.17',
    packages=['gh_templates_bin'],
    package_data={'gh_templates_bin': ['*']},
    entry_points={'console_scripts': ['gh-templates=gh_templates_bin:main']},
    license='Apache-2.0'
)
