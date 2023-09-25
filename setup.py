#make sure you make any necassary changes before running this
from setuptools import setup, find_packages

"""
_______________________________________________________

All Changes are the strings below
_______________________________________________________
"""
#Must change
DriverName="qil_Scale"
version ='1.0.0'
author ='Ben Field'
email ='bfie3543@.sydney.edu.au'
repository_url ='https://github.com/Quantum-Integration-Laboratory/LN2_Scale',
description ='Reading information from Dymo USB scale.n'

#Less important
license ='MIT'
classifiers =["Programming Language :: Python :: 3",
            "License :: OSI Approved :: BSD-2 License",
            "Operating System :: OS Independent",]
keywords ='anything that maybe useful'



"""
_______________________________________________________

For standard use these lines should not need to be changed
_______________________________________________________
"""
  
#gets all the requirements
with open('requirements.txt') as f:
    requirements = f.readlines()

#Copys the github read me as the long description
with open ('readme.md') as f:
    long_description = f.read()
    
#automatically gets all packages in the passed folder
package_list = find_packages(where=DriverName)


setup(
        name =DriverName,
        version =version,
        author =author,
        author_email =email,
        url =repository_url,
        description =description,
        long_description = long_description,
        long_description_content_type ="text/markdown",
        license =license,
        packages = package_list,
        classifiers =classifiers,
        keywords =keywords,
        install_requires = requirements,
        zip_safe = False
)