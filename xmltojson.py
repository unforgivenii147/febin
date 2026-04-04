#!/data/data/com.termux/files/usr/bin/python
import xml.etree.ElementTree as ET
import json
from pathlib import Path
import sys


def etree_to_dict(element):
    d = {element.tag: {} if element.attrib else None}
    children = list(element)
    if children:
        dd = {}
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                if k in dd:
                    if not isinstance(dd[k], list):
                        dd[k] = [dd[k]]
                    dd[k].append(v)
                else:
                    dd[k] = v
        d = {element.tag: dd}
    if element.attrib:
        d[element.tag].update({"@attributes": element.attrib})
    if element.text and element.text.strip():
        if d[element.tag] is None:
            d[element.tag] = element.text.strip()
        else:
            d[element.tag]["#text"] = element.text.strip()
    return d


def xml_to_json(xml_file_path):
    json_file_path = Path(xml_file_path).with_suffix(".json")
    try:
        # Parse the XML file
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        json_data = etree_to_dict(root)

        with json_file_path.open("w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, indent=2, ensure_ascii=False)
        print(f"Successfully converted '{xml_file_path}' to '{json_file_path}'")
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")


if __name__ == "__main__":
    input_xml_file = sys.argv[1]
    xml_to_json(input_xml_file)
