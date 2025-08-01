from setuptools import setup

setup(
    name='APIConnect',
    packages=['APIConnect', 'constants', 'exceptions', 'resources', 'services', 'feed'],
    version='2.0.9',
    license='MIT',
    description='APIs to trade from Nuvama',
    author='Nuvama',
    author_email='support@nuvama.com',
    url='https://nuvamawealth.com/',
    download_url='https://www.nuvamawealth.com/ewwebimages/webfiles/download/Python_APIConnect/APIConnect-2.0.8.tar.gz',
    keywords=['Nuvama', 'Open API', 'Trade', 'Nuvama Python Library'],
    python_requires=">=3.7",
    install_requires=[
        'urllib3>=1.26.6',
        'requests>=2.26.0'
        ],
    data_files=[('conf',['conf/settings.ini'])],
    license_files = ['LICENSE.txt',],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
    ],
)