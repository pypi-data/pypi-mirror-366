from setuptools import setup, find_packages

setup(
    name='passport-cropper',
    version='0.1.0',
    description='Auto-crop scanned images into passport-style photos using face detection.',
    author='Abhay Braja',
    author_email='abhaybraja@gmail.com',
    url='https://github.com/abhaybraja/passport-cropper',
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'numpy'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
