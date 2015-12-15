from setuptools import setup, find_packages


setup(
  name='vedro',
  description='',
  version='0.2.3',
  url='https://github.com/nikitanovosibirsk/vedro',
  author='Nikita Tsvetkov',
  author_email='nikitanovosibirsk@yandex.com',
  license='MIT',
  packages=find_packages(),
  package_data={'vedro': ['vedro.cfg']},
  dependency_links=[
    'https://github.com/nikitanovosibirsk/blahblah/tarball/2b49c2e8403d6f83dfbbb5579caccc46915a561b#egg=blahblah',
    'https://github.com/nikitanovosibirsk/valeera/tarball/74a119b57ce13bc573aa4f6a8a585379183052f4#egg=valeera',
    'https://github.com/nikitanovosibirsk/district42/tarball/dc9db4f5a261dd095642fdd8a564c067600b2309#egg=district42'
  ],
  install_requires=[
    'colorama>=0.3.3'
  ]
)
