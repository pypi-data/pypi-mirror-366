from setuptools import setup, find_packages

VERSION = '0.0.0000002' 
DESCRIPTION = "Package permettant de generer un ensemble de fichiers et de fichier en fonction de la configuration voulu."
LONG_DESCRIPTION = "Il s'agit d'un package qui permet de generer un ensemble de fichiers et de fichier en fonction de la configuration voulu."

# Setting up
setup(
       # the name must match the folder name 'pyarcgenerator'
        name="pyarcgenerator", 
        version=VERSION,
        author="INICODE",
        author_email="contact.inicode@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
            "pytz;python_version>='2022.1'",
            "typing;python_version>='3.7.4.3'",
            "asyncio;python_version>='3.4.3'",
        ],
        
        keywords=['python', 'hivi', 'pyarcgenerator', 'generator'],
        classifiers= [
            # "Headless CMS :: package :: Digibehive",
        ]
)