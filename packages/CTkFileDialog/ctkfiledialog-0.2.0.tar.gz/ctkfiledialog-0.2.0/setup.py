from setuptools import setup, find_packages

setup(
    name='CTkFileDialog',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,  # Importante
    package_data={
        'CTkFileDialog': [
            'icons/*.png',
            'icons/_IconsMini/*.png',
        ],
    },
    install_requires=[
        # lo que haya en requirements.txt
    ],
    author='Tu nombre',
    description='Un diálogo de archivos personalizado para CTk',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/FlickGMD/CTkFileDialog',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
