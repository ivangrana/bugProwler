# BugProwler

BugProwler is a security-focused tool designed for analyzing Insecure Direct Object References (IDOR) in web APIs. The tool leverages OpenAPI specifications for automated attack pattern detection. Below is an overview of its current features and basic usage based on the existing implementation.

## Key Features

### Architecture
- **OpenAPI Specification Analysis**: Parses provided OpenAPI specifications to identify potential security flaws.
- **Automation of Detection**: Utilizes predefined attack patterns to probe for IDOR vulnerabilities in a given API.
- **Event-Driven Design**: Follows an extensible architecture to allow future enhancements.

### IDORAnalyzer
- **OpenAPI Parsing**: Extracts endpoints, parameters, and schema details from an OpenAPI spec file.
- **Attack Pattern Detection**: Employs automated checks to identify common IDOR attack vectors.
- **Customizable Detection Rules**: Easily configurable rules to modify detection logic according to your test case requirements.

## Usage Examples

### Installation
To clone and install dependencies:
```bash
# Clone the repository
git clone https://github.com/ivangrana/bugProwler.git

# Navigate to the directory
cd bugProwler

# Install dependencies
pip install -r requirements.txt
```

### OpenAPI JSON Analysis
Here is an example of how to use the IDORAnalyzer with an OpenAPI JSON file:
```python
from idoranalyzer import IDORAnalyzer

# Load OpenAPI Spec
openapi_spec_path = "path/to/openapi.json"
analyzer = IDORAnalyzer(openapi_spec_path)

# Run Analysis
results = analyzer.run_detection()
print(results)
```

### Using Custom Detection Rules
You can modify the predefined attack patterns in `rules.json` to suit different endpoint testing scenarios.

### Contributing
Contributions are welcome! Please open an issue or submit a pull request for bug fixes, feature enhancements, or additional documentation.

---

For more details, check the source code and usage examples in the `examples/` folder. Any questions or support requests can be directed to the issues tab.