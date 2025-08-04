from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define cloud provider dependencies
CLOUD_PROVIDERS = {
    "gcp": [
        "google-cloud-storage==2.16.0",
        "google-cloud-firestore==2.16.0", 
        "google-cloud-pubsub==2.21.5",
        "google-api-python-client==2.142.0",
        "google-cloud-secret-manager==2.20.0",
        "google-cloud-monitoring==2.22.2",
        "google-cloud-run==0.10.14",
    ],
    "azure": [
        "azure-storage-blob>=12.17.0",
        "azure-servicebus>=7.11.0",
        "azure-cosmos>=4.5.0",
        "azure-identity>=1.13.0",
        "azure-keyvault-secrets>=4.7.0",
        "azure-monitor-query>=1.2.0",
        "azure-mgmt-containerinstance>=10.1.0",
    ],
    "aws": [
        "boto3>=1.28.0",
        "botocore>=1.31.0",
        "aws-secretsmanager-caching>=1.1.1.5",
    ],
}

# Feature-specific dependencies
FEATURES = {
    "backend": [
        "fastapi==0.103.2",
        "uvicorn[standard]==0.22.0",
        "propelauth_fastapi==2.1.16",
        "python-multipart==0.0.8",
        "httpx==0.26.0",
        "cryptography==43.0.1",
        "pyOpenSSL==24.2.1",
    ],
    "model": [
        "statsmodels==0.14.2",
        "scikit-learn==1.5.0",
        "scipy==1.11.3",
        "joblib==1.4.2",
        "matplotlib==3.8.4",
        "plotly>=5.0.0",
    ],
    "data_processing": [
        "openpyxl==3.1.2",
        "xarray==2023.6.0",
        "python-pptx==1.0.2",
        "squarify==0.4.4",
        "Pillow==10.3.0",
        "pdf2image==1.17.0",
        "pymupdf==1.24.11",
    ],
    "email": [
        "sendgrid==6.11.0",
        "email-validator==2.1.1",
    ],
    "ai": [
        "openai==1.47.1",
        "anthropic>=0.3.0",  # Multi-provider AI support
    ],
    "websockets": [
        "websockets==12.0",
    ],
}

# Combine all dependencies for convenience
all_cloud_deps = []
for deps in CLOUD_PROVIDERS.values():
    all_cloud_deps.extend(deps)

all_feature_deps = []
for deps in FEATURES.values():
    all_feature_deps.extend(deps)

setup(
    name="mmmlabs-common",
    version="1.1.0",
    author="MMM Labs",
    author_email="info@mmmlabs.ai",
    description="Cloud-agnostic utilities for MMM Labs services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mmmlabs/mmmlabs-common",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.11",
    install_requires=[
        # Core dependencies (cloud-agnostic)
        "pandas==2.2.2",
        "numpy==1.26.4",
        "requests==2.32.3",
        "pydantic==1.10.9",
        "typing-inspect==0.9.0",
        "python-dotenv>=1.0.0",  # For environment configuration
    ],
    extras_require={
        # Cloud providers
        **CLOUD_PROVIDERS,
        
        # Features
        **FEATURES,
        
        # Convenience combinations
        "all-clouds": all_cloud_deps,
        "all-features": all_feature_deps,
        "all": all_cloud_deps + all_feature_deps,
        
        # Common combinations
        "backend-gcp": CLOUD_PROVIDERS["gcp"] + FEATURES["backend"],
        "backend-azure": CLOUD_PROVIDERS["azure"] + FEATURES["backend"],
        "backend-aws": CLOUD_PROVIDERS["aws"] + FEATURES["backend"],
        
        "ml-gcp": CLOUD_PROVIDERS["gcp"] + FEATURES["model"] + FEATURES["data_processing"],
        "ml-azure": CLOUD_PROVIDERS["azure"] + FEATURES["model"] + FEATURES["data_processing"],
        "ml-aws": CLOUD_PROVIDERS["aws"] + FEATURES["model"] + FEATURES["data_processing"],
        
        # Development and testing
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mmmlabs-config=mmmlabs.cli:main",
        ],
    },
    package_data={
        "mmmlabs": ["py.typed"],  # For type hints
    },
    include_package_data=True,
)