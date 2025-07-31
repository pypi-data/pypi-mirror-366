from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='tcai-churn-x',
    version='0.1.1',
    description='A Flask-based web app for predicting customer churn using a trained ML model.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='The Celeritas AI',
    author_email='business@theceleritasai.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask==3.1.1",
        "pandas==2.3.0",
        "numpy==2.3.0",
        "scikit-learn==1.6.1",
        "joblib==1.5.1",
        "python-dateutil==2.9.0.post0",
        "Werkzeug==3.1.3",
        "Jinja2==3.1.6",
    ],
    entry_points={
        'console_scripts': [
            'tcai-churn-x=tcai_churn_x.webapp:run_app',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
