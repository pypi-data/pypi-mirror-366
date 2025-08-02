from setuptools import setup, find_packages

setup(
    name='CTkFileDialog',
    version='0.2.4',  
    packages=find_packages(),
    include_package_data=True,  
    package_data={
        'CTkFileDialog': [
            'icons/*.png',
            'icons/_IconsMini/*.png',
        ],
    },
    install_requires=[
        "customtkinter>=5.2.2",       
        "opencv-python>=4.12.0.88",       
        "Pillow>=11.3.0",
        "CTkMessagebox>=2.7",         
        "CTkToolTip>=0.8",            
    ],
    author='Flick',
    description='Un diálogo de archivos personalizado para CTk',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/FlickGMD/CTkFileDialog',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)

