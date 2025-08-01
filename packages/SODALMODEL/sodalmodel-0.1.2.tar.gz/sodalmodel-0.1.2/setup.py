from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="SODALMODEL",
    version='0.1.2',
    description='SODAL (Secure Object Detection and Auto-Labeling Framework): A simple yet powerful CNN wrapper for object detection, auto-labeling, training, evaluation, and model security with password protection.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Yotcheb Kandolo Jean',
    author_email='kandoloyotchebjean@gmail.com',
    license='MIT',
    url='https://github.com/YKandoloJean/SMARTVISIONCNN',
    packages=find_packages(),
    install_requires=[
        'tensorflow>=2.0',
        'matplotlib',
        'scikit-learn',
        'opencv-python',
        'tensorflow-hub',
        'ultralytics',
        'numpy'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.7',
)
