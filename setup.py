"""

    Declare a Python package eelplone.policy

"""

from setuptools import setup, find_packages

setup(name = "eelplone.policy",
    version = "1.2.1",
    description = "A Plone policy and customization product",
    author = "",
    author_email = "",
    url = "",
    packages = find_packages(exclude=['ez_setup']),
    namespace_packages = ['eelplone'],
    include_package_data = True,
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],     
    license="GPL2",
    install_requires = [
        "setuptools",
        "five.grok", 
        "z3c.jbot", 
        "collective.monkeypatcher",
    ],
    entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      [console_scripts]
      testldap = eelplone.policy.scripts.testldap:run
      testldap_require_cert = eelplone.policy.scripts.testldap:run_require_cert
      testldap_ignore_cert = eelplone.policy.scripts.testldap:run_ignore_cert
      testldap_search_groups = eelplone.policy.scripts.testldap:search_groups
      """,        
) 