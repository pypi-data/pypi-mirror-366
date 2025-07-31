from setuptools import find_namespace_packages, setup


class Readme(object):
    __readme_path = "README.md"

    @staticmethod
    def get():
        """get content README.md
        :param filename:
        :return:
        """
        long_description = ""
        with open(Readme.__readme_path, "r", encoding="utf-8") as req_file:
            long_description = req_file.read()
        return long_description


class Requirements(object):
    __requirements_path = "requirements_sdk.txt"

    @staticmethod
    def get():
        """Retrieve all dependencies for this project
        :param filename:
        :return:
        """
        requirements = [
            'm-singleton',
            'm-kafka-sdk-v2',
            'redis',
            'm-caching'
        ]
        # with open(Requirements.__requirements_path) as req_file:
        #     for line in req_file.read().splitlines():
        #         if not line.strip().startswith("#"):
        #             requirements.append(line)
        return requirements


version_dev='1.0.9'
version_prod='1.0.7'

run_mode=''

setup(
    name='mobio-dataout-sdk' + run_mode,
    version='1.0.7',
    description='Mobio project SDK',
    keywords="mobio, data out",
    url='https://github.com/mobiovn',
    author='MOBIO',
    author_email='contact@mobio.vn',
    license='MIT',
    # package_dir={'': './'},
    packages=find_namespace_packages(include=["mobio.*"]),
    install_requires=Requirements.get(),
    long_description=Readme.get(),
    long_description_content_type='text/markdown',
    python_requires='>=3.5',
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    project_urls={  # Optional
        # "Bug Reports": "https://github.com/mobiovn",
        # "Funding": "https://mobio.vn/",
        # "Say Thanks!": "https://mobio.vn/",
        # 'Documentation': 'https://packaging.python.org/tutorials/distributing-packages/',
        "Source": "https://github.com/mobiovn",
    }
)
