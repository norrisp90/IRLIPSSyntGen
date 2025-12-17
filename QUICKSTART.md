# Quick Start Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### Generate a Single IPS Document

```bash
python synthgen.py
```

This will create a timestamped JSON file (e.g., `ips_sample_20251120_141709.json`) containing a complete FHIR IPS document.

### Run All Examples

```bash
python examples.py
```

This will:
1. Generate a basic IPS document
2. Create an IPS with custom resource quantities
3. Generate 5 different patient summaries
4. Create patients in different locales (US, German, French, Spanish, Italian)
5. Extract and display specific resource data
6. Generate individual FHIR resources

## Python API Usage

### Quick Example

```python
from synthgen import IPSGenerator

# Create generator
generator = IPSGenerator(locale='en_US')

# Generate IPS bundle
ips_bundle = generator.generate_ips_bundle()

# Save to file
import json
with open('my_ips.json', 'w') as f:
    json.dump(json.loads(ips_bundle.json()), f, indent=2)
```

### Customize Resource Quantities

```python
ips_bundle = generator.generate_ips_bundle(
    num_allergies=5,
    num_medications=8,
    num_conditions=4,
    num_immunizations=6,
    num_procedures=2,
    num_observations=4
)
```

### Generate Individual Resources

```python
# Generate patient
patient = generator.generate_patient()
patient_id = str(patient.id)

# Generate allergies
allergy1 = generator.generate_allergy(patient_id)
allergy2 = generator.generate_allergy(patient_id)

# Generate medications
med1 = generator.generate_medication(patient_id)
med2 = generator.generate_medication(patient_id)
```

### Use Different Locales

```python
# German patient data
generator_de = IPSGenerator(locale='de_DE')
german_bundle = generator_de.generate_ips_bundle()

# French patient data
generator_fr = IPSGenerator(locale='fr_FR')
french_bundle = generator_fr.generate_ips_bundle()
```

## What's Generated

Each IPS bundle contains:

- **1 Composition** - Document structure and sections
- **1 Patient** - Demographics, contact info, identifiers
- **Allergies** - Drug, food, environmental allergies with severity
- **Medications** - Active medications with codes from RxNorm
- **Conditions** - Problems/diagnoses with SNOMED CT codes
- **Immunizations** - Vaccination history with CVX codes
- **Procedures** - Past procedures with SNOMED CT codes
- **Observations** - Vital signs and lab results with LOINC codes

## Standards Compliance

All generated data follows:
- FHIR R4 specification
- IPS Implementation Guide
- Standard terminologies (SNOMED CT, LOINC, RxNorm, CVX)

## Common Use Cases

### Testing FHIR Servers
```python
generator = IPSGenerator()
for i in range(100):
    bundle = generator.generate_ips_bundle()
    # POST bundle to your FHIR server
```

### Generating Test Datasets
```python
generator = IPSGenerator()
patients = []
for i in range(1000):
    bundle = generator.generate_ips_bundle()
    patients.append(json.loads(bundle.json()))

# Save all to one file
with open('test_dataset.json', 'w') as f:
    json.dump(patients, f)
```

### Performance Testing
```python
import time
generator = IPSGenerator()

start = time.time()
for i in range(1000):
    bundle = generator.generate_ips_bundle()
end = time.time()

print(f"Generated 1000 IPS bundles in {end-start:.2f} seconds")
```

## Tips

1. **Reproducible Data**: Set random seed for consistent results
   ```python
   from faker import Faker
   Faker.seed(12345)
   ```

2. **Memory Usage**: For large datasets, generate and save incrementally
   
3. **Validation**: Generated resources are automatically validated by the fhir.resources library

4. **Customization**: Extend the `IPSGenerator` class to add custom medical codes or generation logic

## Support

For issues or questions:
- Check the README.md for detailed documentation
- Review examples.py for usage patterns
- Examine synthgen.py for implementation details
