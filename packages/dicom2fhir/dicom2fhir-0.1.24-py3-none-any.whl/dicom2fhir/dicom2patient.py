
# -*- coding: utf-8 -*-
import re
import datetime
import uuid
from typing import Union
from pydicom.valuerep import PersonName
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.address import Address
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.fhirtypes import DateType
from fhir.resources.R4B.extension import Extension
from fhir.resources.R4B.quantity import Quantity
from dicom2fhir.helpers import get_or
from dicom2fhir.dicom_json_proxy import DicomJsonProxy

DATE8_REGEX = re.compile(r'^(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])$')

def dicom_name_to_fhir(name: str) -> HumanName:
    """
    Convert DICOM PersonName to FHIR HumanName.

    DICOM name format: 'Family^Given^Middle^Prefix^Suffix'
    """
    pname = PersonName(name)
    if pname is None:
        return HumanName.model_construct()

    return HumanName.model_construct(
        family      = pname.family_name,
        given       = [n for n in [pname.given_name, pname.middle_name] if n],
        prefix      = [pname.name_prefix] if pname.name_prefix else None,
        suffix      = [pname.name_suffix] if pname.name_suffix else None,
    )


def dicom_birthdate_to_fhir(birthdate: str) -> DateType | None:
     """
     Convert DICOM PatientBirthDate (YYYYMMDD) to FHIR-compliant date.
     Returns a datetime.date or None if invalid.
     """
     if not isinstance(birthdate, str) or not DATE8_REGEX.match(birthdate):
         return None

     try:
         year = int(birthdate[:4])
         month = int(birthdate[4:6])
         day = int(birthdate[6:])
         return datetime.date(year, month, day)
     except ValueError:
         return None

def dicom_gender_to_fhir(sex: str) -> str:
    """
    Map DICOM PatientSex to FHIR gender.
    - 'M' -> 'male'
    - 'F' -> 'female'
    - 'O' or other -> 'other'
    """
    mapping = {
        'M': 'male',
        'F': 'female',
        'O': 'other'
    }
    return mapping.get(str(sex).upper(), 'unknown') if sex else 'unknown'

def dicom_address_to_fhir(address_str: str) -> Address:
    """
    Convert DICOM address string to FHIR Address.
    Format: 'Street^OtherDesignation^City^State^PostalCode^Country'
    """
    if not address_str:
        return Address.model_construct()

    parts = address_str.split("^")
    return Address.model_construct(
        line=[parts[0]] if parts[0] else None,
        city=parts[2] if len(parts) > 2 else None,
        state=parts[3] if len(parts) > 3 else None,
        postalCode=parts[4] if len(parts) > 4 else None,
        country=parts[5] if len(parts) > 5 else None
    )

def build_patient_resource(ds: DicomJsonProxy, config: dict) -> Patient:

    patient = Patient.model_construct()

    # Identifier
    if "PatientID" in ds:

        assigner = None
        issuer_of_patient_id = ds.get("IssuerOfPatientID", None)
        if issuer_of_patient_id is not None and len(str(issuer_of_patient_id)) > 0:
            assigner = {
                "display": str(issuer_of_patient_id)
            }

        patient.id = config['id_function']('Patient', ds)
        patient.identifier = [
            Identifier.model_construct(
                use="usual",
                system="urn:dicom:patient-id",
                value=str(ds.PatientID),
                assigner=assigner
            )
        ]
    else:
        patient.id = str(uuid.uuid4())

    # Name
    if "PatientName" in ds:
        patient.name = [dicom_name_to_fhir(str(ds.PatientName))]

    # BirthDate
    if "PatientBirthDate" in ds:
        patient.birthDate = dicom_birthdate_to_fhir(str(ds.PatientBirthDate))

    # Gender
    if "PatientSex" in ds:
        patient.gender = dicom_gender_to_fhir(str(ds.PatientSex))

    # Address
    if "PatientAddress" in ds:
        patient.address = [dicom_address_to_fhir(str(ds.PatientAddress))]

    # Telecom
    if "PatientTelephoneNumbers" in ds:
        tel = ds.PatientTelephoneNumbers
        if not isinstance(tel, list):
            tel = [tel]
        patient.telecom = [
            ContactPoint.model_construct(system="phone", value=str(phone), use="home") for phone in tel
        ]

    return patient