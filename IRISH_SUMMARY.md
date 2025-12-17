# Irish FHIR IPS Generator - Summary

## What Was Created

I've successfully updated the FHIR International Patient Summary synthetic data generator to support **Irish population data** with **Azure OpenAI enrichment**.

## Key Features

### 1. Irish Localization (`--irish` flag)
- **Locale**: Uses `en_IE` for Irish-specific fake data
- **Counties**: Generates addresses with authentic Irish counties (Dublin, Cork, Galway, Limerick, etc.)
- **Identifiers**: Uses Irish PPS Number system (`urn:oid:2.16.372.1.2.1.1`)
- **Country Code**: Sets country to "IE"
- **Conditions**: Includes additional conditions common in Irish population:
  - Chronic obstructive pulmonary disease
  - Cardiovascular disease
  - Colon cancer  
  - Appendicitis

### 2. Azure OpenAI Integration (`--llm` flag)
- **Clinical Notes**: Enriches condition resources with realistic clinical notes
- **Irish Context**: LLM is configured to provide Irish healthcare-specific responses
- **Environment**: Uses Azure OpenAI credentials from `.env` file
- **Smart Fallback**: If LLM fails, generator continues without enrichment

## Usage

### Basic Irish Patient (No LLM)
```bash
python synthgen.py --irish
```
Generates Irish patient with authentic Irish names, addresses, and counties.

### Irish Patient with LLM Enrichment
```bash
python synthgen.py --llm --irish
```
Generates Irish patient with AI-enhanced clinical notes for conditions.

### Generate Multiple Irish Patients
```bash
python examples_irish.py
```
Runs comprehensive examples including:
- Basic Irish patients
- LLM-enriched patients
- Multiple patients from different counties
- Large datasets (100 patients)
- Detailed clinical profiles

## Example Output

### Patient Demographics
```json
{
  "name": [{"family": "O'Brien", "given": ["Sean"]}],
  "address": [{
    "line": ["123 Main Street"],
    "city": "Dublin",
    "state": "Dublin",
    "country": "IE"
  }],
  "identifier": [{
    "system": "urn:oid:2.16.372.1.2.1.1",
    "value": "..."
  }]
}
```

### Condition with LLM Enrichment
```json
{
  "code": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "13645005",
      "display": "Chronic obstructive pulmonary disease"
    }],
    "text": "Patient with a history of chronic obstructive pulmonary disease presents with increased dyspnoea and productive cough; advised to continue prescribed inhalers and monitor symptoms closely."
  }
}
```

## Files Modified/Created

### Modified
- `synthgen.py` - Added Irish locale support and Azure OpenAI integration
- `requirements.txt` - Added `openai` and `python-dotenv` dependencies

### Created
- `examples_irish.py` - Comprehensive Irish-specific examples
- `.env` - Contains Azure OpenAI credentials (already existed)

## Technical Implementation

### IPSGenerator Class Updates
```python
def __init__(self, locale: str = 'en_US', use_llm: bool = False):
    self.is_irish = locale == 'en_IE'
    self.use_llm = use_llm
    
    if use_llm:
        self.llm_client = AzureOpenAI(...)
```

### LLM Enrichment Method
```python
def _enrich_with_llm(self, prompt: str) -> Optional[str]:
    """Use Azure OpenAI to enrich medical data"""
    response = self.llm_client.chat.completions.create(
        model=self.deployment_name,
        messages=[
            {"role": "system", "content": "You are a medical data expert specializing in Irish healthcare..."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()
```

### Condition Generation with LLM
```python
def generate_condition(self, patient_id: str) -> Condition:
    cond = random.choice(self.conditions)
    
    # Use LLM to generate additional clinical context
    if self.use_llm and self.is_irish:
        prompt = f"Generate a brief 1-sentence clinical note for an Irish patient with {cond['display']}..."
        clinical_note = self._enrich_with_llm(prompt)
    
    # Add to CodeableConcept.text field
    code=CodeableConcept(
        coding=[...],
        text=clinical_note if clinical_note else cond["display"]
    )
```

## Benefits

1. **Authentic Irish Data**: Names, addresses, and medical conditions relevant to Ireland
2. **Rich Clinical Context**: LLM-generated notes make data more realistic
3. **Testing & Development**: Perfect for Irish healthcare system testing
4. **Scalable**: Can generate thousands of realistic Irish patient records
5. **FHIR Compliant**: All output follows FHIR R4 and IPS standards
6. **Privacy Safe**: Completely synthetic data, no real patient information

## Next Steps

You can extend this further by:
- Adding more Irish-specific conditions
- Including Irish medication names (where different from international)
- Adding Gaeilge (Irish language) names option
- Integrating Irish-specific medical guidelines
- Adding demographics matching Irish population statistics
- Including HSE (Health Service Executive) specific identifiers

## Testing Results

✅ Basic Irish generation works
✅ LLM enrichment successfully adds clinical notes
✅ All FHIR validation passes
✅ Irish counties correctly assigned
✅ Country code properly set to "IE"
✅ Azure OpenAI integration functional
