# Protegrity Developer Edition – protegrity-developer-python

Welcome to the `protegrity-developer-python` repository, part of the Protegrity Developer Edition suite. This repository provides the Python module for integrating Protegrity's Data Discovery and Protection APIs into GenAI and traditional applications.
Customize, compile, and use the module as per your requirement.

## 📦 Repository Structure

```text
.
├── LICENSE
├── README.md
├── pyproject.toml
├── pytest.ini
├── requirements.txt
├── src
│   ├── protegrity_developer_python
│   │   ├── __init__.py
│   │   └── securefind.py
└── tests
    ├── e2e
    │   ├── features
    │   ├── steps
    │   ├── data
    │   └── utils
    │   └── conftest.py
    │   └── README.md
    └── unit
        └── test_securefind.py
```

## 🧰 Features

- **Find and Redact** provides the functionality for classifying PII in unstructured text.
- **Cross-platform support** for the Linux, Windows, and MacOS operating systems.

##  Getting Started

### Prerequisites

- [Git](https://git-scm.com/downloads)
- [Python >= 3.9](https://www.python.org/downloads/)

<!-- ### 🛠️ Installation

Install the package locally using pip:

```bash
pip install protegrity-developer-python
``` -->

### Build the protegrity-developer-python module

1. Install the prerequisites.
```bash
pip install -r requirements.txt
```
2. Build the package after making the required changes in the module and running the following command from the root directory of the repository.
```bash
python -m build
```
3. Verify the build artifacts created. The Python source `.tar.gz` and wheel `.whl` files will be generated under the `dist` directory.
```text
dist
├── protegrity_developer_python-0.9.0-py3-none-any.whl
└── protegrity_developer_python-0.9.0.tar.gz
```
4. Install the `protegrity-developer-python` module from `dist` directory.
```bash
pip install dist/protegrity_developer_python-0.9.0-py3-none-any.whl
```

### 🧪 Sample Usage

```python
import protegrity_developer_python

protegrity_developer_python.configure(
    endpoint_url="http://localhost:8580/pty/data-discovery/v1.0/classify",
    named_entity_map={"PERSON": "NAME", "SOCIAL_SECURITY_NUMBER": "SSN"},
    masking_char="#",
    classification_score_threshold=0.6,
    method="redact",
    enable_logging=True,
    log_level="info"
)

input_text = "John Doe's SSN is 123-45-6789."
output_text = protegrity_developer_python.find_and_redact(input_text)
print(output_text)
```
> **💡Note:** Ensure that the Data Discovery Services are running before executing this snippet.
For setup instructions, please refer to the documentation [here](https://github.com/Protegrity-Developer-Edition/protegrity-developer-edition?tab=readme-ov-file#setup-instructions)


## 📄 Configuration

You can configure the SDK using a `config.json` file or programmatically. Key parameters include:

- endpoint_url: URL of the Data Discovery classification API.
- named_entity_map: Mapping of entity types to label.
- masking_char: Character used for masking PII.
- classification_score_threshold: Minimum score to consider classification.
- method: redact or mask.
- enable_logging: Enable or disable logging.
- log_level: Set the logging level.



## 📚 Documentation

- The Protegrity Developer Edition documentation is available at [http://developer.docs.protegrity.com/](http://developer.docs.protegrity.com/).
- For API reference and tutorials, visit the Developer Portal at [https://www.protegrity.com/developer](https://www.protegrity.com/developer).

## 🧪 Sample Use Case

Use this repo to build GenAI applications like chatbots that:
- Detect PII in prompts using the classifier.
- Redact or mask sensitive data before processing.

## 📜 License

See [LICENSE](./LICENSE) for terms and conditions.
