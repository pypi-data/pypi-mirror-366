import base64

from .utils import get_clinical_summary


def convert_ccda_to_json(base64_string):
    xml_string = base64.b64decode(base64_string).decode("utf-8")
    return get_clinical_summary(xml_string)
