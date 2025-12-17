# HL7 FHIR International Patient Summary (IPS) Synthetic Data Generator

This tool generates realistic synthetic FHIR R4 International Patient Summary (IPS) documents for testing, development, and demonstration purposes.

## Overview

The International Patient Summary (IPS) is an electronic health record extract containing essential healthcare information about a patient. This generator creates complete IPS documents with:

- **Patient Demographics** - Names, addresses, contact information, identifiers
- **Allergies and Intolerances** - Drug, food, and environmental allergies
- **Medication Summary** - Active medications with dosage information
- **Problem List** - Active conditions and diagnoses
- **Immunization History** - Vaccination records
- **Procedures** - Past surgical and medical procedures
- **Diagnostic Results** - Vital signs and laboratory results

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the generator with default settings:

```bash
python synthgen.py
```

This will generate an IPS bundle with default quantities of each resource type and save it to a timestamped JSON file.

### Programmatic Usage

```python
from synthgen import IPSGenerator

# Create a generator instance
generator = IPSGenerator(locale='en_US')

# Generate a complete IPS bundle
ips_bundle = generator.generate_ips_bundle(
    num_allergies=2,
    num_medications=3,
    num_conditions=2,
    num_immunizations=3,
    num_procedures=1,
    num_observations=2
)

# Access the bundle as a FHIR resource
print(ips_bundle.json())

# Or generate individual resources
patient = generator.generate_patient()
allergy = generator.generate_allergy(patient.id)
medication = generator.generate_medication(patient.id)
```

### Customization Options

You can customize the generator by:

1. **Changing the locale** for region-specific data:
```python
generator = IPSGenerator(locale='de_DE')  # German
generator = IPSGenerator(locale='fr_FR')  # French
generator = IPSGenerator(locale='es_ES')  # Spanish
```

2. **Adjusting resource quantities**:
```python
ips_bundle = generator.generate_ips_bundle(
    num_allergies=5,      # More allergies
    num_medications=10,   # More medications
    num_conditions=4,     # More conditions
    num_immunizations=5,  # More immunizations
    num_procedures=3,     # More procedures
    num_observations=5    # More observations
)
```

## Output Format

The generator produces FHIR R4 compliant JSON documents structured as a Bundle resource with:

- **Bundle Type**: `document`
- **Profile**: `http://hl7.org/fhir/uv/ips/StructureDefinition/Bundle-uv-ips`
- **Contents**: 
  - 1 Composition resource (IPS document structure)
  - 1 Patient resource
  - Multiple clinical resources (allergies, medications, etc.)

### Example Output Structure

```json
{
  "resourceType": "Bundle",
  "id": "ips-bundle-12345",
  "meta": {
    "profile": ["http://hl7.org/fhir/uv/ips/StructureDefinition/Bundle-uv-ips"]
  },
  "type": "document",
  "timestamp": "2025-11-20T10:30:00Z",
  "entry": [
    {
      "fullUrl": "urn:uuid:composition-id",
      "resource": {
        "resourceType": "Composition",
        "type": {
          "coding": [{
            "system": "http://loinc.org",
            "code": "60591-5",
            "display": "Patient summary Document"
          }]
        }
      }
    },
    {
      "fullUrl": "urn:uuid:patient-id",
      "resource": {
        "resourceType": "Patient",
        "name": [{"family": "Doe", "given": ["John"]}]
      }
    }
    // ... more resources
  ]
}
```

## Code Samples

### Generate Multiple IPS Documents

```python
from synthgen import IPSGenerator
import json

generator = IPSGenerator()

# Generate 10 patient summaries
for i in range(10):
    bundle = generator.generate_ips_bundle()
    
    with open(f'ips_patient_{i+1}.json', 'w') as f:
        json.dump(json.loads(bundle.json()), f, indent=2)
    
    print(f"Generated IPS #{i+1}")
```

### Extract Specific Resources

```python
from synthgen import IPSGenerator

generator = IPSGenerator()

# Generate just a patient
patient = generator.generate_patient()
print(patient.json())

# Generate allergies for a specific patient
patient_id = "patient-12345"
allergies = [generator.generate_allergy(patient_id) for _ in range(3)]

for allergy in allergies:
    print(f"Allergy: {allergy.code.coding[0].display}")
```

### Validate Generated Resources

```python
from synthgen import IPSGenerator
from fhir.resources.bundle import Bundle

generator = IPSGenerator()
bundle = generator.generate_ips_bundle()

# The fhir.resources library validates automatically
# If there are validation errors, an exception will be raised

print(f"✓ Bundle is valid FHIR R4")
print(f"✓ Profile: {bundle.meta.profile[0]}")
print(f"✓ Total resources: {len(bundle.entry)}")
```

## Standards Compliance

This generator creates data compliant with:

- **FHIR R4** specification
- **IPS Implementation Guide** (http://hl7.org/fhir/uv/ips/)
- Standard terminologies:
  - **SNOMED CT** for clinical findings, allergies, procedures
  - **LOINC** for observations and document types
  - **RxNorm** for medications
  - **CVX** for vaccines

## Use Cases

- **Testing FHIR servers and APIs**
- **Developing IPS viewers and applications**
- **Training and demonstrations**
- **Integration testing**
- **Performance testing with realistic data**
- **Privacy-compliant development** (no real patient data)

## Limitations

- Data is synthetic and for testing purposes only
- Not suitable for clinical decision-making
- Clinical relationships may not be medically accurate
- Does not include all optional IPS sections (e.g., pregnancy history, social history)

## Extending the Generator

You can extend the generator by:

1. Adding more medical codes to the class attributes
2. Creating new resource generation methods
3. Implementing additional IPS sections
4. Adding custom business logic for realistic clinical relationships

Example:
```python
class CustomIPSGenerator(IPSGenerator):
    def __init__(self, locale='en_US'):
        super().__init__(locale)
        # Add custom medical codes
        self.custom_conditions = [
            {"code": "123456", "display": "Custom Condition", "system": "http://snomed.info/sct"}
        ]
    
    def generate_custom_resource(self, patient_id):
        # Implement custom resource generation
        pass
```

## License

This tool is provided as-is for educational and development purposes.

## References

- [HL7 FHIR R4 Specification](http://hl7.org/fhir/R4/)
- [International Patient Summary Implementation Guide](http://hl7.org/fhir/uv/ips/)
- [FHIR Python Library Documentation](https://pypi.org/project/fhir.resources/)
- [Faker Library Documentation](https://faker.readthedocs.io/)
