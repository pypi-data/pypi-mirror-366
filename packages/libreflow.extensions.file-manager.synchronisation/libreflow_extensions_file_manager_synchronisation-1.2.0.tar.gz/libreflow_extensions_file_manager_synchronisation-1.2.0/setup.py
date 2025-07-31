import setuptools
import versioneer
import os

readme = os.path.normpath(os.path.join(__file__, '..', 'README.md'))
with open(readme, "r", encoding="utf-8") as fh:
    long_description = fh.read()

long_description += '\n\n'

changelog = os.path.normpath(os.path.join(__file__, '..', 'CHANGELOG.md'))
with open(changelog, "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    
    name="libreflow.extensions.file-manager.synchronisation",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="LFS",
    author_email="libreflow@lfs.coop",
    description="Libreflow extension to batch manage sync and requests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/lfs.coop/libreflow/extensions/file_manager/synchronisation",
    license="LGPLv3+",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
    keywords="kabaret libreflow",
    install_requires=[],
    python_requires='>=3.7',
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},

)
