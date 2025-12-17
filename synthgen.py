"""
HL7 FHIR International Patient Summary (IPS) Synthetic Data Generator

This module generates synthetic FHIR IPS documents containing:
- Patient demographics
- Allergies and Intolerances
- Medications
- Problems/Conditions
- Immunizations
- Procedures
- Medical Devices
- Diagnostic Results
"""

import json
import random
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from decimal import Decimal
from faker import Faker
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.patient import Patient, PatientContact
from fhir.resources.humanname import HumanName
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.address import Address
from fhir.resources.identifier import Identifier
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.allergyintolerance import AllergyIntolerance
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.condition import Condition
from fhir.resources.immunization import Immunization
from fhir.resources.procedure import Procedure
from fhir.resources.observation import Observation, ObservationComponent
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference
from fhir.resources.composition import Composition, CompositionSection
from fhir.resources.meta import Meta


class IPSGenerator:
    """Generator for FHIR International Patient Summary synthetic data"""
    
    def __init__(self, locale: str = 'en_US', use_llm: bool = False):
        """Initialize the IPS generator with a specific locale
        
        Args:
            locale: Faker locale (use 'en_IE' for Irish)
            use_llm: Whether to use Azure OpenAI for enriching medical data
        """
        self.fake = Faker(locale)
        self.locale = locale
        self.use_llm = use_llm
        self.is_irish = locale == 'en_IE'
        Faker.seed(random.randint(0, 999999))
        
        # Initialize Azure OpenAI client if enabled
        self.llm_client = None
        if use_llm:
            try:
                self.llm_client = AzureOpenAI(
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                )
                self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            except Exception as e:
                print(f"Warning: Could not initialize Azure OpenAI: {e}")
                self.use_llm = False
        
        # Common medical codes for realistic data
        self.allergies = [
            {"code": "227493005", "display": "Cashew nuts", "system": "http://snomed.info/sct"},
            {"code": "300916003", "display": "Latex allergy", "system": "http://snomed.info/sct"},
            {"code": "91935009", "display": "Allergy to peanuts", "system": "http://snomed.info/sct"},
            {"code": "293586001", "display": "Allergy to penicillin", "system": "http://snomed.info/sct"},
            {"code": "419199007", "display": "Allergy to substance", "system": "http://snomed.info/sct"},
        ]
        
        self.medications = [
            {"code": "318272", "display": "Metformin 500mg", "system": "http://www.nlm.nih.gov/research/umls/rxnorm"},
            {"code": "197361", "display": "Lisinopril 10mg", "system": "http://www.nlm.nih.gov/research/umls/rxnorm"},
            {"code": "1049221", "display": "Atorvastatin 20mg", "system": "http://www.nlm.nih.gov/research/umls/rxnorm"},
            {"code": "855332", "display": "Levothyroxine 50mcg", "system": "http://www.nlm.nih.gov/research/umls/rxnorm"},
            {"code": "309362", "display": "Omeprazole 20mg", "system": "http://www.nlm.nih.gov/research/umls/rxnorm"},
        ]
        
        self.conditions = [
            {"code": "44054006", "display": "Type 2 Diabetes Mellitus", "system": "http://snomed.info/sct"},
            {"code": "38341003", "display": "Hypertension", "system": "http://snomed.info/sct"},
            {"code": "13644009", "display": "Hypercholesterolemia", "system": "http://snomed.info/sct"},
            {"code": "195967001", "display": "Asthma", "system": "http://snomed.info/sct"},
            {"code": "40055000", "display": "Chronic sinusitis", "system": "http://snomed.info/sct"},
        ]
        
        # Irish-specific medical data
        if self.is_irish:
            # Common conditions in Irish population
            irish_conditions = [
                {"code": "13645005", "display": "Chronic obstructive pulmonary disease", "system": "http://snomed.info/sct"},
                {"code": "49601007", "display": "Cardiovascular disease", "system": "http://snomed.info/sct"},
                {"code": "363406005", "display": "Colon cancer", "system": "http://snomed.info/sct"},
                {"code": "74400008", "display": "Appendicitis", "system": "http://snomed.info/sct"},
            ]
            self.conditions.extend(irish_conditions)
            
            # Irish counties for addresses
            self.irish_counties = [
                "Dublin", "Cork", "Galway", "Limerick", "Waterford", "Kilkenny",
                "Wexford", "Kerry", "Clare", "Tipperary", "Mayo", "Donegal",
                "Kildare", "Wicklow", "Meath", "Louth", "Sligo", "Westmeath"
            ]
        
        self.immunizations = [
            {"code": "207", "display": "COVID-19 vaccine", "system": "http://hl7.org/fhir/sid/cvx"},
            {"code": "141", "display": "Influenza vaccine", "system": "http://hl7.org/fhir/sid/cvx"},
            {"code": "113", "display": "Td (adult) vaccine", "system": "http://hl7.org/fhir/sid/cvx"},
            {"code": "133", "display": "Pneumococcal conjugate vaccine", "system": "http://hl7.org/fhir/sid/cvx"},
            {"code": "121", "display": "Zoster vaccine", "system": "http://hl7.org/fhir/sid/cvx"},
        ]
        
        self.procedures = [
            {"code": "80146002", "display": "Appendectomy", "system": "http://snomed.info/sct"},
            {"code": "265764009", "display": "Renal dialysis", "system": "http://snomed.info/sct"},
            {"code": "71388002", "display": "Procedure", "system": "http://snomed.info/sct"},
            {"code": "86198006", "display": "Cesarean section", "system": "http://snomed.info/sct"},
            {"code": "232717009", "display": "Coronary artery bypass grafting", "system": "http://snomed.info/sct"},
        ]
    
    def _enrich_with_llm(self, prompt: str) -> Optional[str]:
        """Use Azure OpenAI to enrich medical data"""
        if not self.use_llm or not self.llm_client:
            return None
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a medical data expert specializing in Irish healthcare. Provide concise, realistic responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM enrichment failed: {e}")
            return None
    
    def generate_patient(self, patient_id: str | None = None) -> Patient:
        """Generate a synthetic patient resource"""
        if not patient_id:
            patient_id = f"patient-{self.fake.uuid4()[:8]}"
        
        # Generate basic demographics
        gender = random.choice(['male', 'female', 'other'])
        birth_date = self.fake.date_of_birth(minimum_age=18, maximum_age=90)
        
        # Create patient resource with Irish-specific data if applicable
        if self.is_irish:
            county = random.choice(self.irish_counties)
            identifier_system = "urn:oid:2.16.372.1.2.1.1"  # Irish PPS Number
            country_code = "IE"
        else:
            county = self.fake.state() if hasattr(self.fake, 'state') else None
            identifier_system = "urn:oid:2.16.840.1.113883.2.4.6.3"
            country_code = self.fake.country_code()
        
        patient = Patient.model_construct(
            id=patient_id,
            meta=Meta(profile=["http://hl7.org/fhir/uv/ips/StructureDefinition/Patient-uv-ips"]),
            identifier=[
                Identifier(
                    system=identifier_system,
                    value=self.fake.ssn()
                )
            ],
            name=[HumanName.model_construct(
                    family=self.fake.last_name(),
                    given=[self.fake.first_name()],
                    use="official"
                )
            ],
            gender=gender,
            birthDate=birth_date.isoformat(),
            address=[
                Address.model_construct(
                    use="home",
                    line=[self.fake.street_address()],
                    city=self.fake.city(),
                    state=county,
                    postalCode=self.fake.postcode(),
                    country=country_code
                )
            ],
            telecom=[
                ContactPoint(
                    system="phone",
                    value=self.fake.phone_number(),
                    use="home"
                ),
                ContactPoint(
                    system="email",
                    value=self.fake.email(),
                    use="home"
                )
            ]
        )
        
        return patient
    
    def generate_allergy(self, patient_id: str) -> AllergyIntolerance:
        """Generate a synthetic allergy intolerance resource"""
        allergy = random.choice(self.allergies)
        
        return AllergyIntolerance.model_construct(
            id=f"allergy-{self.fake.uuid4()[:8]}",
            meta=Meta(profile=["http://hl7.org/fhir/uv/ips/StructureDefinition/AllergyIntolerance-uv-ips"]),
            clinicalStatus=CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                    code="active",
                    display="Active"
                )]
            ),
            verificationStatus=CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                    code="confirmed",
                    display="Confirmed"
                )]
            ),
            category=[random.choice(["food", "medication", "environment", "biologic"])],
            criticality=random.choice(["low", "high", "unable-to-assess"]),
            code=CodeableConcept(
                coding=[Coding(
                    system=allergy["system"],
                    code=allergy["code"],
                    display=allergy["display"]
                )]
            ),
            patient=Reference(reference=f"Patient/{patient_id}"),
            onsetDateTime=(datetime.now(timezone.utc) - timedelta(days=random.randint(30, 3650))).isoformat()
        )
    
    def generate_medication(self, patient_id: str) -> MedicationStatement:
        """Generate a synthetic medication statement resource"""
        med = random.choice(self.medications)
        
        return MedicationStatement.model_construct(
            id=f"medication-{self.fake.uuid4()[:8]}",
            meta=Meta(profile=["http://hl7.org/fhir/uv/ips/StructureDefinition/MedicationStatement-uv-ips"]),
            status="active",
            medicationCodeableConcept=CodeableConcept(
                coding=[Coding(
                    system=med["system"],
                    code=med["code"],
                    display=med["display"]
                )]
            ),
            subject=Reference(reference=f"Patient/{patient_id}"),
            effectiveDateTime=(datetime.now(timezone.utc) - timedelta(days=random.randint(30, 730))).isoformat()
        )
    
    def generate_condition(self, patient_id: str) -> Condition:
        """Generate a synthetic condition/problem resource"""
        cond = random.choice(self.conditions)
        
        # Use LLM to generate additional clinical context if enabled
        clinical_note = None
        if self.use_llm and self.is_irish:
            prompt = f"Generate a brief 1-sentence clinical note for an Irish patient with {cond['display']}. Be realistic and concise."
            clinical_note = self._enrich_with_llm(prompt)
        
        condition = Condition.model_construct(
            id=f"condition-{self.fake.uuid4()[:8]}",
            meta=Meta(profile=["http://hl7.org/fhir/uv/ips/StructureDefinition/Condition-uv-ips"]),
            clinicalStatus=CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/condition-clinical",
                    code="active",
                    display="Active"
                )]
            ),
            verificationStatus=CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    code="confirmed",
                    display="Confirmed"
                )]
            ),
            category=[CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/condition-category",
                    code="problem-list-item",
                    display="Problem List Item"
                )]
            )],
            severity=CodeableConcept(
                coding=[Coding(
                    system="http://snomed.info/sct",
                    code=random.choice(["255604002", "371923003", "6736007"]),
                    display=random.choice(["Mild", "Moderate", "Severe"])
                )]
            ),
            code=CodeableConcept(
                coding=[Coding(
                    system=cond["system"],
                    code=cond["code"],
                    display=cond["display"]
                )],
                text=clinical_note if clinical_note else cond["display"]
            ),
            subject=Reference(reference=f"Patient/{patient_id}"),
            onsetDateTime=(datetime.now(timezone.utc) - timedelta(days=random.randint(90, 3650))).isoformat()
        )
        
        return condition
    
    def generate_immunization(self, patient_id: str) -> Immunization:
        """Generate a synthetic immunization resource"""
        imm = random.choice(self.immunizations)
        
        return Immunization.model_construct(
            id=f"immunization-{self.fake.uuid4()[:8]}",
            meta=Meta(profile=["http://hl7.org/fhir/uv/ips/StructureDefinition/Immunization-uv-ips"]),
            status="completed",
            vaccineCode=CodeableConcept(
                coding=[Coding(
                    system=imm["system"],
                    code=imm["code"],
                    display=imm["display"]
                )]
            ),
            patient=Reference(reference=f"Patient/{patient_id}"),
            occurrenceDateTime=(datetime.now(timezone.utc) - timedelta(days=random.randint(30, 1825))).isoformat()
        )
    
    def generate_procedure(self, patient_id: str) -> Procedure:
        """Generate a synthetic procedure resource"""
        proc = random.choice(self.procedures)
        
        return Procedure.model_construct(
            id=f"procedure-{self.fake.uuid4()[:8]}",
            meta=Meta(profile=["http://hl7.org/fhir/uv/ips/StructureDefinition/Procedure-uv-ips"]),
            status="completed",
            code=CodeableConcept(
                coding=[Coding(
                    system=proc["system"],
                    code=proc["code"],
                    display=proc["display"]
                )]
            ),
            subject=Reference(reference=f"Patient/{patient_id}"),
            performedDateTime=(datetime.now(timezone.utc) - timedelta(days=random.randint(180, 3650))).isoformat()
        )
    
    def generate_observation(self, patient_id: str, obs_type: str = "vital-signs") -> Observation:
        """Generate a synthetic observation resource (vital signs, labs)"""
        
        if obs_type == "vital-signs":
            # Blood Pressure
            obs = Observation.model_construct(
                id=f"observation-{self.fake.uuid4()[:8]}",
                meta=Meta(profile=["http://hl7.org/fhir/StructureDefinition/vitalsigns"]),
                status="final",
                category=[CodeableConcept(
                    coding=[Coding(
                        system="http://terminology.hl7.org/CodeSystem/observation-category",
                        code="vital-signs",
                        display="Vital Signs"
                    )]
                )],
                code=CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code="85354-9",
                        display="Blood pressure panel"
                    )]
                ),
                subject=Reference(reference=f"Patient/{patient_id}"),
                effectiveDateTime=(datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90))).isoformat(),
                component=[
                    ObservationComponent(
                        code=CodeableConcept(
                            coding=[Coding(
                                system="http://loinc.org",
                                code="8480-6",
                                display="Systolic blood pressure"
                            )]
                        ),
                        valueQuantity=Quantity(
                            value=Decimal(random.randint(110, 140)),
                            unit="mmHg",
                            system="http://unitsofmeasure.org",
                            code="mm[Hg]"
                        )
                    ),
                    ObservationComponent(
                        code=CodeableConcept(
                            coding=[Coding(
                                system="http://loinc.org",
                                code="8462-4",
                                display="Diastolic blood pressure"
                            )]
                        ),
                        valueQuantity=Quantity(
                            value=Decimal(random.randint(70, 90)),
                            unit="mmHg",
                            system="http://unitsofmeasure.org",
                            code="mm[Hg]"
                        )
                    )
                ]
            )
        else:
            # Laboratory result (e.g., Glucose)
            obs = Observation.model_construct(
                id=f"observation-{self.fake.uuid4()[:8]}",
                meta=Meta(profile=["http://hl7.org/fhir/uv/ips/StructureDefinition/Observation-results-laboratory-uv-ips"]),
                status="final",
                category=[CodeableConcept(
                    coding=[Coding(
                        system="http://terminology.hl7.org/CodeSystem/observation-category",
                        code="laboratory",
                        display="Laboratory"
                    )]
                )],
                code=CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code="2339-0",
                        display="Glucose [Mass/volume] in Blood"
                    )]
                ),
                subject=Reference(reference=f"Patient/{patient_id}"),
                effectiveDateTime=(datetime.now(timezone.utc) - timedelta(days=random.randint(1, 180))).isoformat(),
                valueQuantity=Quantity(
                    value=Decimal(str(round(random.uniform(70, 120), 1))),
                    unit="mg/dL",
                    system="http://unitsofmeasure.org",
                    code="mg/dL"
                )
            )
        
        return obs
    
    def generate_composition(self, patient_id: str, entries: List[Dict[str, str]]) -> Composition:
        """Generate a composition resource that structures the IPS document"""
        
        sections = []
        
        # Allergies section
        allergy_entries = [e for e in entries if e["type"] == "AllergyIntolerance"]
        if allergy_entries:
            sections.append(CompositionSection(
                title="Allergies and Intolerances",
                code=CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code="48765-2",
                        display="Allergies and adverse reactions Document"
                    )]
                ),
                entry=[Reference(reference=e["reference"]) for e in allergy_entries]
            ))
        
        # Medications section
        med_entries = [e for e in entries if e["type"] == "MedicationStatement"]
        if med_entries:
            sections.append(CompositionSection(
                title="Medication Summary",
                code=CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code="10160-0",
                        display="History of Medication use Narrative"
                    )]
                ),
                entry=[Reference(reference=e["reference"]) for e in med_entries]
            ))
        
        # Problems section
        cond_entries = [e for e in entries if e["type"] == "Condition"]
        if cond_entries:
            sections.append(CompositionSection(
                title="Problem List",
                code=CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code="11450-4",
                        display="Problem list - Reported"
                    )]
                ),
                entry=[Reference(reference=e["reference"]) for e in cond_entries]
            ))
        
        # Immunizations section
        imm_entries = [e for e in entries if e["type"] == "Immunization"]
        if imm_entries:
            sections.append(CompositionSection(
                title="History of Immunizations",
                code=CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code="11369-6",
                        display="History of Immunization Narrative"
                    )]
                ),
                entry=[Reference(reference=e["reference"]) for e in imm_entries]
            ))
        
        # Procedures section
        proc_entries = [e for e in entries if e["type"] == "Procedure"]
        if proc_entries:
            sections.append(CompositionSection(
                title="History of Procedures",
                code=CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code="47519-4",
                        display="History of Procedures Document"
                    )]
                ),
                entry=[Reference(reference=e["reference"]) for e in proc_entries]
            ))
        
        # Results section
        obs_entries = [e for e in entries if e["type"] == "Observation"]
        if obs_entries:
            sections.append(CompositionSection(
                title="Results",
                code=CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code="30954-2",
                        display="Relevant diagnostic tests/laboratory data Narrative"
                    )]
                ),
                entry=[Reference(reference=e["reference"]) for e in obs_entries]
            ))
        
        composition = Composition.model_construct(
            id=f"composition-{self.fake.uuid4()[:8]}",
            meta=Meta(profile=["http://hl7.org/fhir/uv/ips/StructureDefinition/Composition-uv-ips"]),
            status="final",
            type=CodeableConcept(
                coding=[Coding(
                    system="http://loinc.org",
                    code="60591-5",
                    display="Patient summary Document"
                )]
            ),
            subject=Reference(reference=f"Patient/{patient_id}"),
            date=datetime.now(timezone.utc).isoformat(),
            author=[Reference(reference=f"Patient/{patient_id}")],
            title="International Patient Summary",
            section=sections
        )
        
        return composition
    
    def generate_ips_bundle(self, num_allergies: int = 2, num_medications: int = 3,
                           num_conditions: int = 2, num_immunizations: int = 3,
                           num_procedures: int = 1, num_observations: int = 2) -> Bundle:
        """
        Generate a complete IPS document as a FHIR Bundle
        
        Args:
            num_allergies: Number of allergies to generate
            num_medications: Number of medications to generate
            num_conditions: Number of conditions to generate
            num_immunizations: Number of immunizations to generate
            num_procedures: Number of procedures to generate
            num_observations: Number of observations to generate
            
        Returns:
            FHIR Bundle containing the complete IPS document
        """
        
        # Generate patient
        patient = self.generate_patient()
        patient_id = str(patient.id)
        
        # Generate clinical resources
        allergies = [self.generate_allergy(patient_id) for _ in range(num_allergies)]
        medications = [self.generate_medication(patient_id) for _ in range(num_medications)]
        conditions = [self.generate_condition(patient_id) for _ in range(num_conditions)]
        immunizations = [self.generate_immunization(patient_id) for _ in range(num_immunizations)]
        procedures = [self.generate_procedure(patient_id) for _ in range(num_procedures)]
        observations = [self.generate_observation(patient_id, "vital-signs") for _ in range(num_observations)]
        
        # Collect all entry references for composition
        entries = []
        entries.extend([{"type": "AllergyIntolerance", "reference": f"AllergyIntolerance/{a.id}"} for a in allergies])
        entries.extend([{"type": "MedicationStatement", "reference": f"MedicationStatement/{m.id}"} for m in medications])
        entries.extend([{"type": "Condition", "reference": f"Condition/{c.id}"} for c in conditions])
        entries.extend([{"type": "Immunization", "reference": f"Immunization/{i.id}"} for i in immunizations])
        entries.extend([{"type": "Procedure", "reference": f"Procedure/{p.id}"} for p in procedures])
        entries.extend([{"type": "Observation", "reference": f"Observation/{o.id}"} for o in observations])
        
        # Generate composition
        composition = self.generate_composition(patient_id, entries)
        
        # Create bundle entries
        bundle_entries = [
            BundleEntry(
                fullUrl=f"urn:uuid:{composition.id}",
                resource=composition
            ),
            BundleEntry(
                fullUrl=f"urn:uuid:{patient.id}",
                resource=patient
            )
        ]
        
        # Add all clinical resources
        for allergy in allergies:
            bundle_entries.append(BundleEntry(
                fullUrl=f"urn:uuid:{allergy.id}",
                resource=allergy
            ))
        
        for medication in medications:
            bundle_entries.append(BundleEntry(
                fullUrl=f"urn:uuid:{medication.id}",
                resource=medication
            ))
        
        for condition in conditions:
            bundle_entries.append(BundleEntry(
                fullUrl=f"urn:uuid:{condition.id}",
                resource=condition
            ))
        
        for immunization in immunizations:
            bundle_entries.append(BundleEntry(
                fullUrl=f"urn:uuid:{immunization.id}",
                resource=immunization
            ))
        
        for procedure in procedures:
            bundle_entries.append(BundleEntry(
                fullUrl=f"urn:uuid:{procedure.id}",
                resource=procedure
            ))
        
        for observation in observations:
            bundle_entries.append(BundleEntry(
                fullUrl=f"urn:uuid:{observation.id}",
                resource=observation
            ))
        
        # Create the bundle
        bundle = Bundle.model_construct(
            id=f"ips-bundle-{self.fake.uuid4()[:8]}",
            meta=Meta(profile=["http://hl7.org/fhir/uv/ips/StructureDefinition/Bundle-uv-ips"]),
            type="document",
            timestamp=datetime.now(timezone.utc).isoformat(),
            entry=bundle_entries
        )
        
        return bundle


def main():
    """Main function to demonstrate IPS generation"""
    
    import sys
    
    # Check for Irish mode
    use_irish = '--irish' in sys.argv
    use_llm = '--llm' in sys.argv
    
    if use_irish:
        print("🇮🇪 Generating Irish Patient Summary with LLM enrichment..." if use_llm else "🇮🇪 Generating Irish Patient Summary...")
        generator = IPSGenerator(locale='en_IE', use_llm=use_llm)
    else:
        print("Generating FHIR International Patient Summary...")
        generator = IPSGenerator(locale='en_US', use_llm=use_llm)
    
    # Generate an IPS bundle
    ips_bundle = generator.generate_ips_bundle(
        num_allergies=2,
        num_medications=3,
        num_conditions=2,
        num_immunizations=3,
        num_procedures=1,
        num_observations=2
    )
    
    # Convert to JSON
    ips_json = json.loads(ips_bundle.json())
    
    # Save to file
    output_file = f"ips_sample_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ips_json, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ IPS Bundle generated successfully!")
    print(f"✓ Saved to: {output_file}")
    print(f"\n📊 Bundle Statistics:")
    if ips_bundle.entry:
        print(f"   - Total entries: {len(ips_bundle.entry)}")
    print(f"   - Bundle ID: {ips_bundle.id}")
    print(f"   - Timestamp: {ips_bundle.timestamp}")
    
    # Print summary of resources
    resource_types = {}
    if ips_bundle.entry:
        for entry in ips_bundle.entry:
            if entry.resource:
                resource_type = type(entry.resource).__name__
                resource_types[resource_type] = resource_types.get(resource_type, 0) + 1
    
    print(f"\n📋 Resource Summary:")
    for resource_type, count in sorted(resource_types.items()):
        print(f"   - {resource_type}: {count}")
    
    return ips_bundle


if __name__ == "__main__":
    main()
