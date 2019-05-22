import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='dco-org-check',
     version='0.2',
     scripts=['dco-org-check'] ,
     author="John Mertic",
     author_email="jmertic@gmail.com",
     description="Script to check a GitHub org for commits without a DCO signoff that should have one.",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/jmertic/dco-org-check",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: Apache Software License",
         "Operating System :: OS Independent",
     ],
 )
