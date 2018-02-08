from setuptools import setup, find_packages


setup(
  name='vedro',
  description='',
  version='0.3.3',
  url='https://github.com/nikitanovosibirsk/vedro',
  author='Nikita Tsvetkov',
  author_email='nikitanovosibirsk@yandex.com',
  license='MIT',
  packages=find_packages(),
  package_data={'vedro': ['vedro.cfg']},
  install_requires=[
    'colorama>=0.3.3',
    'district42>=0.5.5',
    'valeera>=0.5.5',
    'blahblah>=0.5.8',
    'python-dotenv>=0.7.1'
  ]
)
