import xml.etree.ElementTree as ET
from datetime import datetime


# Helper to parse and reformat dates
def format_date(date_str):
    if not date_str or date_str.strip() == "":
        return ""
    for fmt in ("%m/%d/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def format_diagnosis(diagnosis_data_string):
    diagnosis_list = diagnosis_data_string.strip().replace(" and ", ";").split(";")
    return [diagnosis_code.strip() for diagnosis_code in diagnosis_list]


def get_medication_summary(med_section, ns):
    try:
        tbody = med_section.find(
            ".//hl7:section/hl7:text/hl7:table/hl7:tbody",
            namespaces=ns,
        )
        if tbody is not None:
            meds = []
            for row in tbody.findall(".//hl7:tr", namespaces=ns):
                cells = row.findall(".//hl7:td", namespaces=ns)
                if len(cells) >= 6:
                    med_info = {
                        "medication_name": cells[0].text.strip()
                        if cells[0].text
                        else "",
                        "route": cells[1].text.strip() if cells[1].text else "",
                        "notes": cells[2].text.strip() if cells[2].text else "",
                        "start_date": format_date(
                            cells[3].text if cells[3].text else "",
                        ),
                        "end_date": format_date(cells[4].text if cells[4].text else ""),
                        "status": cells[5].text.strip() if cells[5].text else "",
                    }
                    meds.append(med_info)
            return meds
        return []
    except Exception as e:
        print(e)
        return []


def get_encounter_summary(encounter_section, ns):
    try:
        tbody = encounter_section.find(
            ".//hl7:section/hl7:text/hl7:table/hl7:tbody",
            namespaces=ns,
        )
        if tbody is not None:
            encounters = []
            for row in tbody.findall(".//hl7:tr", namespaces=ns):
                cells = row.findall(".//hl7:td", namespaces=ns)
                if len(cells) >= 5:
                    encounter_info = {
                        "encounter": cells[0].text.strip() if cells[0].text else "",
                        "location": cells[1].text.strip() if cells[1].text else "",
                        "encounter_date": format_date(
                            cells[2].text if cells[2].text else "",
                        ),
                        "provider": cells[3].text.strip() if cells[3].text else "",
                        "diagnosis_codes": format_diagnosis(
                            cells[4].text.strip() if cells[4].text else "",
                        ),
                    }
                    encounters.append(encounter_info)
            return encounters
        return []
    except Exception as e:
        print(e)
        return []


def get_allergies_summary(allergies_section, ns):
    try:
        tbody = allergies_section.find(
            ".//hl7:section/hl7:text/hl7:table/hl7:tbody",
            namespaces=ns,
        )
        if tbody is not None:
            allergies = []
            for row in tbody.findall(".//hl7:tr", namespaces=ns):
                cells = row.findall(".//hl7:td", namespaces=ns)
                if len(cells) >= 6:
                    allergy_info = {
                        "allergy": cells[0].text.strip() if cells[0].text else "",
                        "drug_non_drug": cells[1].text.strip() if cells[1].text else "",
                        "reaction": cells[2].text.strip() if cells[2].text else "",
                        "allergy_type": cells[3].text.strip() if cells[3].text else "",
                        "onset_date": format_date(
                            cells[4].text if cells[4].text else "",
                        ),
                        "status": cells[5].text.strip() if cells[5].text else "",
                    }
                    allergies.append(allergy_info)
            return allergies
        return []
    except Exception as e:
        print(e)
        return []


def get_referral_summary(referral_section, ns):
    try:
        extracted_tables = []
        tables = referral_section.findall(
            ".//hl7:section/hl7:text/hl7:table",
            namespaces=ns,
        )
        for table in tables:
            table_data = {}
            referring_first = referring_last = ""

            for tr in table.findall(".//hl7:tr", namespaces=ns):
                th = tr.find(".//hl7:th", namespaces=ns)
                td = tr.find(".//hl7:td", namespaces=ns)
                if th is not None and td is not None:
                    key = th.text.strip() if th.text else ""
                    value = td.text.strip() if td.text else ""

                    # Normalize keys
                    key_lower = key.lower()
                    if key_lower == "reason":
                        table_data["reason"] = value
                    elif key_lower == "diagnosis 1":
                        table_data["diagnosis"] = [value]
                    elif key_lower == "diagnosis 2":
                        table_data["diagnosis"].append(value)
                    elif key_lower == "referral organization":
                        table_data["referral_organization"] = value
                    elif key_lower == "referring provider first name":
                        referring_first = value
                    elif key_lower == "referring provider last name":
                        referring_last = value
                    elif key_lower == "referring provider speciality":
                        table_data["referring_provider_specialty"] = value
                    elif key_lower == "referred provider":
                        table_data["referred_provider"] = value
                    elif key_lower == "referred provider specialty":
                        table_data["referred_provider_specialty"] = value
                    elif key_lower == "referral priority":
                        table_data["referral_priority"] = value

            # Combine provider name
            if referring_first or referring_last:
                table_data["referring_provider_name"] = (
                    f"{referring_first} {referring_last}".strip()
                )

            if table_data:
                extracted_tables.append(table_data)
        return extracted_tables
    except Exception as e:
        print(e)
        return []


def get_problems_summary(problem_section, ns):
    try:
        tbody = problem_section.find(
            ".//hl7:section/hl7:text/hl7:table/hl7:tbody",
            namespaces=ns,
        )
        if tbody is not None:
            problems = []
            for row in tbody.findall(".//hl7:tr", namespaces=ns):
                cells = row.findall(".//hl7:td", namespaces=ns)
                if len(cells) >= 6:
                    allergy_info = {
                        "problem_type": cells[0].text.strip() if cells[0].text else "",
                        "snomed_code": cells[1].text.strip() if cells[1].text else "",
                        "icd_code": cells[2].text.strip() if cells[2].text else "",
                        "onset_date": format_date(
                            cells[3].text if cells[3].text else "",
                        ),
                        "prblem_status": cells[4].text.strip() if cells[4].text else "",
                        "wu_status": cells[5].text.strip() if cells[5].text else "",
                        "risk": cells[6].text.strip() if cells[6].text else "",
                        "notes": cells[7].text.strip() if cells[7].text else "",
                    }
                    problems.append(allergy_info)
            return problems
        return []
    except Exception as e:
        print(e)
        return []


def get_care_plan_summary(care_plan_section, ns):
    try:
        tables = care_plan_section.findall(
            ".//hl7:section/hl7:text/hl7:table",
            namespaces=ns,
        )
        care_plan = []
        if tables:
            table = tables[0]
            tbody = table.find(
                ".//hl7:tbody",
                namespaces=ns,
            )
            if tbody is not None:
                for row in tbody.findall(".//hl7:tr", namespaces=ns):
                    cells = row.findall(".//hl7:td", namespaces=ns)
                    if len(cells) >= 1:
                        allergy_info = {
                            "test_name": cells[0].text.strip() if cells[0].text else "",
                            "order_date_utc": format_date(
                                cells[1].text.strip() if cells[1].text else "",
                            ),
                        }
                        care_plan.append(allergy_info)
        return care_plan
    except Exception as e:
        print(e)
        return []


def get_clinical_summary(xml_string):
    try:
        tree = ET.ElementTree(ET.fromstring(xml_string))
        root = tree.getroot()
        ns = {"hl7": "urn:hl7-org:v3"}

        # Step 1: Find <component> with <title>Medications
        components = root.findall(".//hl7:structuredBody/hl7:component", namespaces=ns)

        med_section = None
        medication_summary = []
        encounter_section = None
        encounter_summary = []
        allergies_section = None
        allergies_summary = []
        referral_section = None
        referral_summary = []
        problems_section = None
        problems_summary = []
        care_plan_section = None
        care_plan_summary = []

        for component in components:
            title_elem = component.find(".//hl7:section/hl7:title", namespaces=ns)
            if (
                title_elem is not None
                and title_elem.text.strip().lower() == "medications"
            ):
                med_section = component

            if (
                title_elem is not None
                and title_elem.text.strip().lower() == "encounters"
            ):
                encounter_section = component

            if (
                title_elem is not None
                and title_elem.text.strip().lower() == "allergies"
            ):
                allergies_section = component

            if (
                title_elem is not None
                and title_elem.text.strip().lower() == "reason for referral"
            ):
                referral_section = component

            if title_elem is not None and title_elem.text.strip().lower() == "problems":
                problems_section = component

            if (
                title_elem is not None
                and title_elem.text.strip().lower() == "plan of treatment"
            ):
                care_plan_section = component

        # Step 2: Extract data from the <text>/<table>/<tbody>
        if med_section is not None:
            medication_summary = get_medication_summary(med_section, ns)

        if encounter_section is not None:
            encounter_summary = get_encounter_summary(
                encounter_section,
                ns,
            )

        if allergies_section is not None:
            allergies_summary = get_allergies_summary(
                allergies_section,
                ns,
            )

        if referral_section is not None:
            referral_summary = get_referral_summary(referral_section, ns)

        if problems_section is not None:
            problems_summary = get_problems_summary(problems_section, ns)

        if care_plan_section is not None:
            care_plan_summary = get_care_plan_summary(care_plan_section, ns)

        return {  # noqa: TRY300
            "medication_summary": medication_summary,
            "encounter_summary": encounter_summary,
            "allergies_summary": allergies_summary,
            "referral_summary": referral_summary,
            "problems_summary": problems_summary,
            "care_plan_summary": care_plan_summary,
        }

    except Exception as e:
        print(e)
        return {
            "medication_summary": [],
            "encounter_summary": [],
            "allergies_summary": [],
            "referral_summary": [],
            "problems_summary": [],
            "care_plan_summary": [],
        }
