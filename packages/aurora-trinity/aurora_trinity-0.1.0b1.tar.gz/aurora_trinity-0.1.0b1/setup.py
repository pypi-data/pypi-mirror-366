from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name='aurora-trinity',
    version='0.1.0b1',
    description='Aurora Trinity-3: Inteligencia Electrónica Fractal, Ética y Libre',
    long_description=(here / 'README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    author='Aurora Alliance',
    author_email='contacto@aurora-program.org',
    url='https://github.com/Aurora-Program/Trinity-3',
    license='Apache-2.0',
    packages=find_packages(exclude=['tests', 'Test', '__pycache__']),
    python_requires='>=3.8',
    install_requires=[
        # Añade aquí tus dependencias principales
        # 'numpy', 'scipy', 'pandas', ...
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Natural Language :: Spanish',
    ],
    keywords='inteligencia artificial fractal aurora ética tensor',
    project_urls={
        'Documentation': 'https://github.com/Aurora-Program/Trinity-3',
        'Source': 'https://github.com/Aurora-Program/Trinity-3',
        'Tracker': 'https://github.com/Aurora-Program/Trinity-3/issues',
    },
)
