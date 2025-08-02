# package_c/setup.py
from setuptools import setup, find_packages

setup(
    name='agent_chat_api',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=5.1.4', 
        'letta-client>=0.1.223',
        'openai==1.95.1',
    ],
)