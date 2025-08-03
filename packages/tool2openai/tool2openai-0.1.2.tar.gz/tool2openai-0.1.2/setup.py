from setuptools import setup, find_packages

# Читаем содержимое README.md для использования в качестве длинного описания
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tools2openai",
    version="0.1.1",
    author="Nehcy",
    author_email="cibershaman@пmail.com",
    description="набор простеньких инструментов для собственного openai-совместимого эндпоинта.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nehc/tool2openai",  # Замените на реальный URL
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",  # Или другая лицензия
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=[
        "openai>=1.98.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
)