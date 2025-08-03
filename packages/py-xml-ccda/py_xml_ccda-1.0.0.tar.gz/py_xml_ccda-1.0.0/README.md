# py_xml_ccda

**GitHub Repository**: [https://github.com/omkarmore2008/py_xml_ccda](https://github.com/omkarmore2008/py_xml_ccda)

A Python package for parsing XML CCDA (Continuity of Care Document Architecture) files and extracting structured patient data. This package converts complex medical XML documents into easy-to-use JSON format, making healthcare data more accessible for analysis and integration.

## Features

- **Comprehensive Data Extraction**: Extracts multiple types of patient data from CCDA XML files
- **Structured Output**: Returns well-organized JSON data with consistent formatting
- **Date Normalization**: Automatically formats dates to ISO standard (YYYY-MM-DD)
- **Base64 Support**: Handles base64-encoded XML input
- **Error Handling**: Robust error handling with graceful fallbacks

## Supported Data Types

The package extracts the following patient information from CCDA XML files:

### 🏥 **Medications**
- Medication name
- Route of administration
- Clinical notes
- Start and end dates
- Status

### 🩺 **Medical Encounters**
- Encounter type
- Location
- Encounter date
- Healthcare provider
- Diagnosis codes

### ⚠️ **Allergies**
- Allergy/allergen name
- Drug/non-drug classification
- Reaction details
- Allergy type
- Onset date
- Status

### 🔄 **Referrals**
- Referral reason
- Diagnosis information
- Referral organization
- Referring provider details
- Referred provider information
- Referral priority

### 🏷️ **Problems/Conditions**
- Problem type
- SNOMED codes
- ICD codes
- Onset date
- Problem status
- Work-up status
- Risk level
- Clinical notes

### 📋 **Care Plans**
- Test names
- Order dates
- Treatment plans

## Installation

Install the package using pip:

```bash
pip install py_xml_ccda
```

## Usage

### Basic Usage

```python
from py_xml_ccda import convert_ccda_to_json
import base64

# If you have a base64-encoded XML string
base64_xml = "your_base64_encoded_ccda_xml_here"
patient_data = convert_ccda_to_json(base64_xml)

# Access different data sections
medications = patient_data['medication_summary']
encounters = patient_data['encounter_summary']
allergies = patient_data['allergies_summary']
referrals = patient_data['referral_summary']
problems = patient_data['problems_summary']
care_plans = patient_data['care_plan_summary']
```

### Working with XML Files

```python
from py_xml_ccda.utils import get_clinical_summary
import base64

# Read XML file and convert to base64
with open('patient_ccda.xml', 'r', encoding='utf-8') as file:
    xml_content = file.read()

# Convert to base64
base64_xml = base64.b64encode(xml_content.encode('utf-8')).decode('utf-8')

# Extract patient data
patient_data = convert_ccda_to_json(base64_xml)

# Or work directly with XML string
patient_data = get_clinical_summary(xml_content)
```

### Example Output

```python
{
    "medication_summary": [
        {
            "medication_name": "Lisinopril 10mg",
            "route": "Oral",
            "notes": "Take once daily",
            "start_date": "2023-01-15",
            "end_date": "",
            "status": "Active"
        }
    ],
    "encounter_summary": [
        {
            "encounter": "Office Visit",
            "location": "Primary Care Clinic",
            "encounter_date": "2023-06-15",
            "provider": "Dr. Smith",
            "diagnosis_codes": ["Z00.00", "I10"]
        }
    ],
    "allergies_summary": [
        {
            "allergy": "Penicillin",
            "drug_non_drug": "Drug",
            "reaction": "Rash",
            "allergy_type": "Drug Allergy",
            "onset_date": "2020-03-10",
            "status": "Active"
        }
    ],
    "referral_summary": [...],
    "problems_summary": [...],
    "care_plan_summary": [...]
}
```

## Command Line Usage

The package also provides a command-line interface:

```bash
py_xml_ccda
```

## Requirements

- Python 3.6+
- No external dependencies (uses only Python standard library)

## Error Handling

The package includes comprehensive error handling:

- Invalid XML files return empty data structures instead of crashing
- Missing sections are handled gracefully
- Date parsing errors result in empty date fields
- All functions include try-catch blocks with appropriate fallbacks

## Data Format Standards

- **Dates**: All dates are normalized to ISO format (YYYY-MM-DD)
- **Diagnosis Codes**: Multiple codes are split and cleaned automatically
- **Text Fields**: All text is stripped of whitespace and normalized
- **Missing Data**: Empty or missing fields return empty strings instead of None

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please visit the project repository or contact the maintainers.

## Changelog

### Version 0.1
- Initial release
- Support for medications, encounters, allergies, referrals, problems, and care plans
- Base64 XML input support
- Command-line interface
- Comprehensive error handling
