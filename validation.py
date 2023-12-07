import os
import xml.etree.ElementTree as ET

def validate_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        print(f"{xml_file} валиден.")
    except ET.ParseError as e:
        print(f"{xml_file} невалиден. Ошибка: {e}")

def validate_xml_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            xml_file_path = os.path.join(folder_path, filename)
            validate_xml(xml_file_path)

folder_path = "xml"

validate_xml_folder(folder_path)
