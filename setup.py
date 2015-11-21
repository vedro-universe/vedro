from setuptools import setup, find_packages


setup(
  name='vedro',
  description='',
  version='0.2.0',
  url='https://github.com/nikitanovosibirsk/vedro',
  author='Nikita Tsvetkov',
  author_email='nikitanovosibirsk@yandex.com',
  license='MIT',
  packages=find_packages(),
  install_requires=[
    'colorama>=0.3.3',
    'district42>=0.5.4',
    'valeera>=0.5.4',
    'blahblah>=0.5.5'
  ]
)
