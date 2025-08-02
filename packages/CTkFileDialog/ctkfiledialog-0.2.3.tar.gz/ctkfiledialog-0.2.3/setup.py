from setuptools import setup, find_packages

setup(
    name='CTkFileDialog',
    version='0.2.3',  
    packages=find_packages(),
    include_package_data=True,  
    package_data={
        'CTkFileDialog': [
            'icons/*.png',
            'icons/_IconsMini/*.png',
        ],
    },
    install_requires=[
        "customtkinter>=5.2.0",       
        "opencv-python>=4.9.0",       
        "Pillow>=10.0.0",
        "CTkMessagebox>=2.0",         
        "CTkToolTip>=1.0",            
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

