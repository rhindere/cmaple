import setuptools

long_description = 'See README.md'

setuptools.setup(
    name="maple",
    version="0.1",
    author="Ron Hinderer",
    author_email="rhindere@cisco.com",
    description="MAPLE - Multipurpose API Programming Language Extension",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['maple',
              'maple.fmc',
              'maple.amp',
              'maple.threatgrid',
              ],
    install_requires=['Autologging',
                      'jsonpath_ng',
                      'requests',
                      'xmltodict',
                      'objectpath',
                      'urllib3',
                      'pytz',
                      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Cisco Sample Code License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)