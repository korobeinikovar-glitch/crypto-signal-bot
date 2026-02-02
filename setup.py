"""
Setup configuration for the crypto signal bot package.
"""
from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='crypto-signal-bot',
    version='1.0.0',
    author='Crypto Signal Bot Contributors',
    description='A cryptocurrency analysis bot using Bybit public API for generating trade signals',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/korobeinikovar-glitch/crypto-signal-bot',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'crypto-signal-bot=signal_bot.main:main',
        ],
    },
    keywords='cryptocurrency trading signal bot bybit technical-analysis',
    project_urls={
        'Bug Reports': 'https://github.com/korobeinikovar-glitch/crypto-signal-bot/issues',
        'Source': 'https://github.com/korobeinikovar-glitch/crypto-signal-bot',
    },
)
