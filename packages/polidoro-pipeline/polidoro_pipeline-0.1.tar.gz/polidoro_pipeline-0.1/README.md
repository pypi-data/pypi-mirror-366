# Polidoro Pipeline

A powerful Python library for parallel data processing through a sequence of steps.

[![Code Quality](https://github.com/heitorpolidoro/polidoro-pipeline/actions/workflows/code_quality.yml/badge.svg)](https://github.com/heitorpolidoro/polidoro-pipeline/actions/workflows/code_quality.yml)
[![Upload Python Package](https://github.com/heitorpolidoro/polidoro-pipeline/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/heitorpolidoro/polidoro-pipeline/actions/workflows/pypi-publish.yml)
<br>
[![Latest Version](https://img.shields.io/github/v/release/heitorpolidoro/polidoro-pipeline?label=Latest%20Version)](https://github.com/heitorpolidoro/polidoro-pipeline/releases/latest)
![GitHub Release Date](https://img.shields.io/github/release-date/heitorpolidoro/polidoro-pipeline)
![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/heitorpolidoro/polidoro-pipeline/latest)
![GitHub last commit](https://img.shields.io/github/last-commit/heitorpolidoro/polidoro-pipeline)
<br>
[![GitHub issues](https://img.shields.io/github/issues/heitorpolidoro/polidoro-pipeline)](https://github.com/heitorpolidoro/polidoro-pipeline/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/heitorpolidoro/polidoro-pipeline)](https://github.com/heitorpolidoro/polidoro-pipeline/pulls)

[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=heitorpolidoro_polidoro-pipeline&metric=coverage)](https://sonarcloud.io/summary/new_code?id=heitorpolidoro_polidoro-pipeline)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=heitorpolidoro_polidoro-pipeline&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=heitorpolidoro_polidoro-pipeline)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=heitorpolidoro_polidoro-pipeline&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=heitorpolidoro_polidoro-pipeline)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=heitorpolidoro_polidoro-pipeline&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=heitorpolidoro_polidoro-pipeline)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=heitorpolidoro_polidoro-pipeline&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=heitorpolidoro_polidoro-pipeline)
<br>
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=heitorpolidoro_polidoro-pipeline&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=heitorpolidoro_polidoro-pipeline)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=heitorpolidoro_polidoro-pipeline&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=heitorpolidoro_polidoro-pipeline)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=heitorpolidoro_polidoro-pipeline&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=heitorpolidoro_polidoro-pipeline)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=heitorpolidoro_polidoro-pipeline&metric=bugs)](https://sonarcloud.io/summary/new_code?id=heitorpolidoro_polidoro-pipeline)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=heitorpolidoro_polidoro-pipeline&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=heitorpolidoro_polidoro-pipeline)
</br>
[![DeepSource](https://app.deepsource.com/gh/heitorpolidoro/polidoro-pipeline.svg/?label=active+issues&show_trend=true&token=hZuHoQ-gd4kIPgNuSX0X_QT2)](https://app.deepsource.com/gh/heitorpolidoro/polidoro-pipeline/)
</br>
![PyPI](https://img.shields.io/pypi/v/polidoro-pipeline?label=PyPi%20package)


| Python Versions                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ![GitHub branch check runs](https://img.shields.io/github/check-runs/heitorpolidoro/polidoro-pipeline/master?nameFilter=Code%20Quality%20%2F%20Tests%20(3.10)&logo=python&label=3.10)<br/>![GitHub branch check runs](https://img.shields.io/github/check-runs/heitorpolidoro/polidoro-pipeline/master?nameFilter=Code%20Quality%20%2F%20Tests%20(3.11)&logo=python&label=3.11)<br/>![GitHub branch check runs](https://img.shields.io/github/check-runs/heitorpolidoro/polidoro-pipeline/master?nameFilter=Code%20Quality%20%2F%20Tests%20(3.12)&logo=python&label=3.12)<br/>![GitHub branch check runs](https://img.shields.io/github/check-runs/heitorpolidoro/polidoro-pipeline/master?nameFilter=Code%20Quality%20%2F%20Tests%20(3.13)&logo=python&label=3.13) |

## 🚀 Overview

Polidoro Pipeline is a Python library that simplifies parallel data processing through a sequence of steps. It automatically handles parallelization using Python's ThreadPoolExecutor, making it easy to process both single values and lists of values efficiently.

## ✨ Features

- 🔄 Process data through a sequence of steps
- ⚡ Automatic parallelization of processing
- 🧩 Simple and intuitive API
- 🔌 Easy to integrate with existing code
- 📦 Handles both single values and lists of values

## 📋 Installation

```bash
pip install polidoro_pipeline
```

## 🔧 Usage

### Basic Example

```python
from ppipeline import Pipeline

# Define processing steps
def add_1(x):
    return x + 1

def multiply_by_2(x):
    return x * 2

# Create a pipeline with steps
pipeline = Pipeline([add_1, multiply_by_2])

# Process a single value
result = list(pipeline.run(1))  # [4]

# Process multiple values in parallel
results = list(pipeline.run([1, 2, 3]))  # [4, 6, 8]
```

### Adding Steps Incrementally

```python
pipeline = Pipeline()
pipeline.add_step(add_1)
pipeline.add_step(multiply_by_2)
result = list(pipeline.run(2))  # [6]
```

### Controlling Thread Count

```python
# Limit the number of worker threads
pipeline = Pipeline([add_1, multiply_by_2], thread_count=4)
results = list(pipeline.run([1, 2, 3, 4, 5]))
```

## 🧠 How It Works

1. The Pipeline class takes a list of callable functions as steps
2. When you call `run()` with input data, each item is processed through all steps in sequence
3. If the input is a list, items are processed in parallel using ThreadPoolExecutor
4. Each step can return a single value or a list of values
5. If a step returns multiple values (as a list), each value is processed independently in subsequent steps

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
