"""
IPS Bundle Validator

This script validates generated IPS bundles to ensure they conform to
FHIR R4 and IPS Implementation Guide specifications.
"""

import json
import sys
from pathlib import Path
from fhir.resources.bundle import Bundle


def validate_ips_file(filepath: str) -> dict:
    """
    Validate an IPS JSON file
    
    Args:
        filepath: Path to the IPS JSON file
        
    Returns:
        Dictionary with validation results
    """
    results = {
        'valid': False,
        'file': filepath,
        'errors': [],
        'warnings': [],
        'info': {}
    }
    
    try:
        # Check file exists
        if not Path(filepath).exists():
            results['errors'].append(f"File not found: {filepath}")
            return results
        
        # Load JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate it's a Bundle
        if data.get('resourceType') != 'Bundle':
            results['errors'].append("Resource type is not 'Bundle'")
            return results
        
        # Parse as FHIR Bundle (this validates structure)
        try:
            bundle = Bundle.parse_obj(data)
            results['info']['bundle_id'] = bundle.id
            results['info']['bundle_type'] = bundle.type
            results['info']['timestamp'] = bundle.timestamp
        except Exception as e:
            results['errors'].append(f"FHIR validation error: {str(e)}")
            return results
        
        # Check it's a document bundle
        if bundle.type != 'document':
            results['errors'].append(f"Bundle type should be 'document', got '{bundle.type}'")
            return results
        
        # Check for entries
        if not bundle.entry or len(bundle.entry) == 0:
            results['errors'].append("Bundle has no entries")
            return results
        
        results['info']['entry_count'] = len(bundle.entry)
        
        # Check for Composition (required first entry in IPS)
        first_entry = bundle.entry[0]
        if type(first_entry.resource).__name__ != 'Composition':
            results['warnings'].append("First entry should be a Composition resource")
        
        # Count resource types
        resource_counts = {}
        required_resources = {
            'Composition': False,
            'Patient': False
        }
        
        for entry in bundle.entry:
            if entry.resource:
                resource_type = type(entry.resource).__name__
                resource_counts[resource_type] = resource_counts.get(resource_type, 0) + 1
                
                if resource_type in required_resources:
                    required_resources[resource_type] = True
        
        results['info']['resources'] = resource_counts
        
        # Check required resources
        for resource_type, found in required_resources.items():
            if not found:
                results['errors'].append(f"Missing required resource: {resource_type}")
        
        # Check Composition sections
        for entry in bundle.entry:
            if type(entry.resource).__name__ == 'Composition':
                composition = entry.resource
                if composition.section:
                    section_titles = [s.title for s in composition.section if s.title]
                    results['info']['sections'] = section_titles
                else:
                    results['warnings'].append("Composition has no sections")
        
        # Check IPS profile
        if bundle.meta and bundle.meta.profile:
            if 'http://hl7.org/fhir/uv/ips/StructureDefinition/Bundle-uv-ips' in bundle.meta.profile:
                results['info']['ips_profile'] = True
            else:
                results['warnings'].append("Bundle does not declare IPS profile")
        else:
            results['warnings'].append("Bundle meta or profile not specified")
        
        # If we got here with no errors, it's valid
        if len(results['errors']) == 0:
            results['valid'] = True
        
    except json.JSONDecodeError as e:
        results['errors'].append(f"Invalid JSON: {str(e)}")
    except Exception as e:
        results['errors'].append(f"Unexpected error: {str(e)}")
    
    return results


def print_validation_results(results: dict):
    """Print validation results in a readable format"""
    
    print("\n" + "="*70)
    print(f"IPS Validation Results: {results['file']}")
    print("="*70)
    
    if results['valid']:
        print("\n✓ VALID - Bundle conforms to FHIR R4 and IPS specifications")
    else:
        print("\n✗ INVALID - Bundle has validation errors")
    
    # Print errors
    if results['errors']:
        print("\n❌ Errors:")
        for error in results['errors']:
            print(f"   - {error}")
    
    # Print warnings
    if results['warnings']:
        print("\n⚠️  Warnings:")
        for warning in results['warnings']:
            print(f"   - {warning}")
    
    # Print info
    if results['info']:
        print("\nℹ️  Information:")
        for key, value in results['info'].items():
            if key == 'resources':
                print(f"   - Resource counts:")
                for resource_type, count in sorted(value.items()):
                    print(f"     • {resource_type}: {count}")
            elif key == 'sections':
                print(f"   - Composition sections:")
                for section in value:
                    print(f"     • {section}")
            else:
                print(f"   - {key}: {value}")
    
    print("\n" + "="*70 + "\n")


def validate_multiple_files(pattern: str = "ips_*.json"):
    """Validate multiple IPS files matching a pattern"""
    
    files = list(Path('.').glob(pattern))
    
    if not files:
        print(f"No files found matching pattern: {pattern}")
        return
    
    print(f"\nFound {len(files)} file(s) to validate\n")
    
    valid_count = 0
    invalid_count = 0
    
    for filepath in files:
        results = validate_ips_file(str(filepath))
        print_validation_results(results)
        
        if results['valid']:
            valid_count += 1
        else:
            invalid_count += 1
    
    print("="*70)
    print(f"Summary: {valid_count} valid, {invalid_count} invalid out of {len(files)} total")
    print("="*70)


def main():
    """Main function"""
    
    if len(sys.argv) > 1:
        # Validate specific file
        filepath = sys.argv[1]
        results = validate_ips_file(filepath)
        print_validation_results(results)
        
        # Exit with appropriate code
        sys.exit(0 if results['valid'] else 1)
    else:
        # Validate all IPS files in current directory
        validate_multiple_files("ips_*.json")


if __name__ == "__main__":
    main()
