from setuptools import setup,find_packages

setup(
    name='vibhansh',
    version='0.1',
    author='VibhanshGod',
    author_email='vibhugpta3006@gmail.com',
    description='this is speech to text program for J.A.R.V.I.S made by VibhanshGod',
)
packages = find_packages(),
install_requirement = [
    'selenium',
    'webdriver_manager',
]