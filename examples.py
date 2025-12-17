"""
Example scripts for using the IPS Generator
"""

import json
from synthgen import IPSGenerator


def example_1_basic_generation():
    """Example 1: Basic IPS generation with default settings"""
    print("=" * 60)
    print("Example 1: Basic IPS Generation")
    print("=" * 60)
    
    generator = IPSGenerator(locale='en_US')
    bundle = generator.generate_ips_bundle()
    
    # Save to file
    with open('ips_example1.json', 'w', encoding='utf-8') as f:
        json.dump(json.loads(bundle.json()), f, indent=2)
    
    print(f"✓ Generated IPS with {len(bundle.entry) if bundle.entry else 0} entries")
    print("✓ Saved to: ips_example1.json\n")


def example_2_custom_quantities():
    """Example 2: Generate IPS with custom resource quantities"""
    print("=" * 60)
    print("Example 2: Custom Resource Quantities")
    print("=" * 60)
    
    generator = IPSGenerator(locale='en_US')
    bundle = generator.generate_ips_bundle(
        num_allergies=5,
        num_medications=8,
        num_conditions=4,
        num_immunizations=6,
        num_procedures=2,
        num_observations=4
    )
    
    # Save to file
    with open('ips_example2.json', 'w', encoding='utf-8') as f:
        json.dump(json.loads(bundle.json()), f, indent=2)
    
    print(f"✓ Generated IPS with more resources: {len(bundle.entry) if bundle.entry else 0} entries")
    print("✓ Saved to: ips_example2.json\n")


def example_3_multiple_patients():
    """Example 3: Generate multiple patient summaries"""
    print("=" * 60)
    print("Example 3: Multiple Patient Summaries")
    print("=" * 60)
    
    generator = IPSGenerator(locale='en_US')
    
    for i in range(5):
        bundle = generator.generate_ips_bundle()
        
        filename = f'ips_patient_{i+1}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json.loads(bundle.json()), f, indent=2)
        
        print(f"✓ Generated patient {i+1} - Saved to: {filename}")
    
    print(f"\n✓ Total: 5 patient summaries generated\n")


def example_4_different_locales():
    """Example 4: Generate IPS with different locales"""
    print("=" * 60)
    print("Example 4: Different Locales")
    print("=" * 60)
    
    locales = {
        'en_US': 'US English',
        'de_DE': 'German',
        'fr_FR': 'French',
        'es_ES': 'Spanish',
        'it_IT': 'Italian'
    }
    
    for locale_code, locale_name in locales.items():
        generator = IPSGenerator(locale=locale_code)
        bundle = generator.generate_ips_bundle(num_allergies=1, num_medications=2)
        
        filename = f'ips_{locale_code}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json.loads(bundle.json()), f, indent=2)
        
        print(f"✓ Generated {locale_name} patient - Saved to: {filename}")
    
    print(f"\n✓ Generated patients in {len(locales)} different locales\n")


def example_5_extract_specific_data():
    """Example 5: Generate and extract specific resource data"""
    print("=" * 60)
    print("Example 5: Extract Specific Resource Data")
    print("=" * 60)
    
    generator = IPSGenerator(locale='en_US')
    bundle = generator.generate_ips_bundle()
    
    # Extract patient information
    if bundle.entry:
        for entry in bundle.entry:
            if type(entry.resource).__name__ == 'Patient':
                patient = entry.resource
                print(f"\n👤 Patient Information:")
                if patient.name and len(patient.name) > 0:
                    name = patient.name[0]
                    print(f"   Name: {' '.join(name.given or [])} {name.family or ''}")
                print(f"   Gender: {patient.gender or 'Unknown'}")
                print(f"   Birth Date: {patient.birthDate or 'Unknown'}")
                if patient.address and len(patient.address) > 0:
                    addr = patient.address[0]
                    print(f"   City: {addr.city or 'Unknown'}")
            
            elif type(entry.resource).__name__ == 'AllergyIntolerance':
                allergy = entry.resource
                if allergy.code and allergy.code.coding:
                    print(f"\n🚨 Allergy: {allergy.code.coding[0].display}")
                    print(f"   Category: {allergy.category[0] if allergy.category else 'Unknown'}")
                    print(f"   Criticality: {allergy.criticality or 'Unknown'}")
            
            elif type(entry.resource).__name__ == 'MedicationStatement':
                med = entry.resource
                if hasattr(med, 'medicationCodeableConcept') and med.medicationCodeableConcept:
                    if med.medicationCodeableConcept.coding:
                        print(f"\n💊 Medication: {med.medicationCodeableConcept.coding[0].display}")
                        print(f"   Status: {med.status}")
    
    print("\n")


def example_6_individual_resources():
    """Example 6: Generate individual resources for testing"""
    print("=" * 60)
    print("Example 6: Individual Resource Generation")
    print("=" * 60)
    
    generator = IPSGenerator(locale='en_US')
    patient_id = "test-patient-123"
    
    # Generate individual resources
    patient = generator.generate_patient(patient_id=patient_id)
    allergy = generator.generate_allergy(patient_id)
    medication = generator.generate_medication(patient_id)
    condition = generator.generate_condition(patient_id)
    
    print("✓ Generated individual resources:")
    print(f"   - Patient: {patient.id}")
    print(f"   - Allergy: {allergy.id}")
    print(f"   - Medication: {medication.id}")
    print(f"   - Condition: {condition.id}")
    
    # Save each as separate JSON
    resources = {
        'patient': patient,
        'allergy': allergy,
        'medication': medication,
        'condition': condition
    }
    
    for resource_name, resource in resources.items():
        filename = f'{resource_name}_example.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json.loads(resource.json()), f, indent=2)
        print(f"   - Saved {resource_name} to: {filename}")
    
    print("\n")


def run_all_examples():
    """Run all example functions"""
    print("\n" + "="*60)
    print("HL7 FHIR IPS Generator - Examples")
    print("="*60 + "\n")
    
    example_1_basic_generation()
    example_2_custom_quantities()
    example_3_multiple_patients()
    example_4_different_locales()
    example_5_extract_specific_data()
    example_6_individual_resources()
    
    print("="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    run_all_examples()
