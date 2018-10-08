import setuptools

with open("README.md", encoding="utf-8", mode="r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cmaple",
    version="0.1",
    author="Ron Hinderer",
    author_email="rhindere@cisco.com",
    description="CMAPLE - Cisco Multipurpose API Programming Language Extension",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rhindere/cmaple",
    packages=['cmaple',
              'cmaple.fmc',
              'cmaple.amp',
              'cmaple.threatgrid',
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
        # "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)