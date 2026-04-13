"""
UI Parsing for Android Automated Testing
Extracts interactive elements (clickable, focusable) from UI Automator XML dump
"""

import os
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional


class UIParser:
    def __init__(self):
        self.interactive_classes = set([
            'android.widget.Button',
            'android.widget.TextView',
            'android.widget.EditText',
            'android.widget.ImageView',
            'android.widget.CheckBox',
            'android.widget.RadioButton',
            'android.widget.Switch',
            'com.google.android.material.button.MaterialButton',
        ])

    def dump_ui(self, output_file: str = "ui_dump.xml") -> str:
        """Dump current UI hierarchy using uiautomator via ADB"""
        cmd = f"adb shell uiautomator dump /sdcard/{output_file}"
        os.system(cmd)
        # Pull it back to host
        os.system(f"adb pull /sdcard/{output_file} {output_file} > /dev/null 2>&1")
        return output_file

    def parse_ui(self, xml_file: str) -> List[Dict]:
        """Parse XML and extract interactive elements"""
        tree = ET.parse(xml_file)
        root = tree.getroot()

        elements = []
        seen_positions = set()

        for node in root.iter('node'):
            clickable = node.get('clickable') == 'true'
            focusable = node.get('focusable') == 'true'
            class_name = node.get('class', '')

            # Include if clickable/focusable OR it's a known interactive class
            if not (clickable or focusable or class_name in self.interactive_classes):
                continue

            bounds = node.get('bounds')
            if not bounds:
                continue

            # Parse bounds: "[left,top][right,bottom]"
            try:
                coords = list(map(int, re.findall(r'\d+', bounds)))
                left, top, right, bottom = coords
                center_x = (left + right) // 2
                center_y = (top + bottom) // 2
            except Exception:
                continue

            # Deduplicate by position (round to avoid near-duplicates)
            pos_key = (center_x // 10, center_y // 10)
            if pos_key in seen_positions:
                continue
            seen_positions.add(pos_key)

            text = node.get('text', '')
            content_desc = node.get('content-desc', '')
            resource_id = node.get('resource-id', '')

            # Use content_desc if text is empty
            label = text.strip() if text.strip() else content_desc.strip()
            if not label and resource_id:
                label = resource_id.split('/')[-1]

            elements.append({
                'id': len(elements) + 1,
                'label': label,
                'class': class_name,
                'resource_id': resource_id,
                'center_x': center_x,
                'center_y': center_y,
                'bounds': (left, top, right, bottom),
                'clickable': clickable,
                'focusable': focusable,
            })

        return elements

    def find_by_label(self, elements: List[Dict], label_contains: str) -> Optional[Dict]:
        """Find first element containing label (case-insensitive)"""
        label_lower = label_contains.lower()
        for elem in elements:
            if label_lower in elem['label'].lower():
                return elem
        return None

    def get_interactive_elements(self) -> List[Dict]:
        """One-shot: dump and parse current UI"""
        xml_file = self.dump_ui()
        return self.parse_ui(xml_file)


def tap(x: int, y: int) -> None:
    """Tap at coordinates via ADB"""
    os.system(f"adb shell input tap {x} {y}")


def input_text(text: str) -> None:
    """Input text via ADB"""
    # adb input text handles space as %s
    escaped = text.replace(' ', '%s')
    os.system(f"adb shell input text '{escaped}'")
