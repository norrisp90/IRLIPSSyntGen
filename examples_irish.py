"""
Irish Population IPS Generator Examples

Demonstrates generating FHIR International Patient Summary documents
specifically for Irish population with Azure OpenAI enrichment.
"""

import json
from datetime import datetime, timezone
from synthgen import IPSGenerator


def example_basic_irish():
    """Generate basic Irish patient summary without LLM"""
    print("="*70)
    print("Example 1: Basic Irish Patient (No LLM)")
    print("="*70)
    
    generator = IPSGenerator(locale='en_IE', use_llm=False)
    bundle = generator.generate_ips_bundle(
        num_allergies=2,
        num_medications=3,
        num_conditions=2,
        num_immunizations=3,
        num_procedures=1,
        num_observations=2
    )
    
    # Save bundle
    filename = "ips_irish_basic.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json.loads(bundle.json()), f, indent=2, ensure_ascii=False)
    
    # Print patient info
    patient = None
    for entry in bundle.entry:
        if type(entry.resource).__name__ == 'Patient':
            patient = entry.resource
            break
    
    if patient:
        print(f"\n✓ Generated Irish patient: {patient.name[0].given[0]} {patient.name[0].family}")
        if patient.address and patient.address[0].state:
            print(f"   County: {patient.address[0].state}")
        print(f"   Country: {patient.address[0].country}")
    
    print(f"✓ Saved to: {filename}\n")


def example_irish_with_llm():
    """Generate Irish patient summary with LLM enrichment"""
    print("="*70)
    print("Example 2: Irish Patient with LLM Enrichment")
    print("="*70)
    
    generator = IPSGenerator(locale='en_IE', use_llm=True)
    bundle = generator.generate_ips_bundle(
        num_allergies=2,
        num_medications=3,
        num_conditions=3,  # More conditions to show LLM enrichment
        num_immunizations=3,
        num_procedures=1,
        num_observations=2
    )
    
    # Save bundle
    filename = "ips_irish_enriched.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json.loads(bundle.json()), f, indent=2, ensure_ascii=False)
    
    # Print patient info and conditions with LLM notes
    patient = None
    conditions = []
    
    for entry in bundle.entry:
        resource_type = type(entry.resource).__name__
        if resource_type == 'Patient':
            patient = entry.resource
        elif resource_type == 'Condition':
            conditions.append(entry.resource)
    
    if patient:
        print(f"\n✓ Generated Irish patient: {patient.name[0].given[0]} {patient.name[0].family}")
        if patient.address and patient.address[0].state:
            print(f"   County: {patient.address[0].state}")
        print(f"   Country: {patient.address[0].country}")
    
    print(f"\n📋 Conditions (with LLM-enriched notes):")
    for cond in conditions:
        print(f"\n   • {cond.code.coding[0].display}")
        if cond.code.text and cond.code.text != cond.code.coding[0].display:
            print(f"     Clinical Note: {cond.code.text}")
    
    print(f"\n✓ Saved to: {filename}\n")


def example_multiple_irish_patients():
    """Generate multiple Irish patients from different counties"""
    print("="*70)
    print("Example 3: Multiple Irish Patients (Various Counties)")
    print("="*70)
    
    generator = IPSGenerator(locale='en_IE', use_llm=False)
    
    patients_data = []
    
    for i in range(5):
        bundle = generator.generate_ips_bundle(
            num_allergies=random.randint(1, 3),
            num_medications=random.randint(2, 5),
            num_conditions=random.randint(1, 3),
            num_immunizations=random.randint(2, 4),
            num_procedures=random.randint(0, 2),
            num_observations=random.randint(1, 3)
        )
        
        # Extract patient info
        for entry in bundle.entry:
            if type(entry.resource).__name__ == 'Patient':
                patient = entry.resource
                county = patient.address[0].state if patient.address and patient.address[0].state else "Unknown"
                print(f"   {i+1}. {patient.name[0].given[0]} {patient.name[0].family} - County {county}")
                break
        
        patients_data.append(json.loads(bundle.json()))
    
    # Save all patients
    filename = "ips_irish_multiple.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(patients_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Generated 5 Irish patients")
    print(f"✓ Saved to: {filename}\n")


def example_irish_population_dataset():
    """Generate a dataset of Irish patients for testing"""
    print("="*70)
    print("Example 4: Irish Population Dataset (100 patients)")
    print("="*70)
    
    generator = IPSGenerator(locale='en_IE', use_llm=False)
    
    print("Generating 100 Irish patient summaries...")
    
    dataset = []
    county_distribution = {}
    
    for i in range(100):
        bundle = generator.generate_ips_bundle(
            num_allergies=random.randint(0, 4),
            num_medications=random.randint(1, 6),
            num_conditions=random.randint(1, 5),
            num_immunizations=random.randint(2, 5),
            num_procedures=random.randint(0, 3),
            num_observations=random.randint(1, 4)
        )
        
        # Track county distribution
        for entry in bundle.entry:
            if type(entry.resource).__name__ == 'Patient':
                patient = entry.resource
                if patient.address and patient.address[0].state:
                    county = patient.address[0].state
                    county_distribution[county] = county_distribution.get(county, 0) + 1
                break
        
        dataset.append(json.loads(bundle.json()))
        
        if (i + 1) % 20 == 0:
            print(f"   Generated {i + 1}/100...")
    
    # Save dataset
    filename = "ips_irish_dataset_100.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Generated 100 Irish patient summaries")
    print(f"✓ Saved to: {filename}")
    print(f"\n📊 County Distribution:")
    for county, count in sorted(county_distribution.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   - {county}: {count} patients")
    print()


def example_irish_with_specific_conditions():
    """Generate Irish patients with specific conditions common in Ireland"""
    print("="*70)
    print("Example 5: Irish Patients with Common Irish Conditions")
    print("="*70)
    
    generator = IPSGenerator(locale='en_IE', use_llm=True)
    
    # Generate patient with multiple conditions
    bundle = generator.generate_ips_bundle(
        num_allergies=2,
        num_medications=5,
        num_conditions=4,  # More conditions
        num_immunizations=3,
        num_procedures=2,
        num_observations=3
    )
    
    filename = "ips_irish_detailed.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json.loads(bundle.json()), f, indent=2, ensure_ascii=False)
    
    print(f"✓ Generated detailed Irish patient profile")
    print(f"✓ Saved to: {filename}\n")


def run_all_examples():
    """Run all Irish IPS examples"""
    import random
    random.seed(42)  # For reproducibility
    
    print("\n" + "="*70)
    print("Irish Population FHIR IPS Generator - Examples")
    print("="*70 + "\n")
    
    example_basic_irish()
    example_irish_with_llm()
    example_multiple_irish_patients()
    example_irish_population_dataset()
    example_irish_with_specific_conditions()
    
    print("="*70)
    print("All Irish examples completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    import random
    run_all_examples()
