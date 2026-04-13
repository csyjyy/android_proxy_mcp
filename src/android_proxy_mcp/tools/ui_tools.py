"""
MCP Tools for UI automation - dump, tap, input
"""

import os
import tempfile
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

from android_proxy_mcp.ui.parser import UIParser, tap, input_text


def register_ui_tools(mcp: FastMCP) -> None:
    """Register all UI automation MCP tools"""

    @mcp.tool()
    def ui_dump() -> Dict[str, Any]:
        """
        Dump current UI hierarchy from device and extract interactive elements.
        Returns list of clickable/focusable elements with their coordinates and labels.
        """
        parser = UIParser()
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                xml_file = os.path.join(tmpdir, "ui_dump.xml")
                parser.dump_ui(xml_file)
                elements = parser.parse_ui(xml_file)
                
                return {
                    "elements_count": len(elements),
                    "elements": elements,
                    "summary": "\n".join([
                        f"[{e['id']}] \"{e['label']}\" @ ({e['center_x']},{e['center_y']}) { 'clickable' if e['clickable'] else '' } { 'focusable' if e['focusable'] else '' }"
                        for e in elements
                    ])
                }
        except Exception as e:
            return {
                "error": str(e),
                "hint": "Make sure ADB is connected and device is available"
            }

    @mcp.tool()
    def ui_tap(element_id: int) -> Dict[str, Any]:
        """
        Tap on an element by its ID from ui_dump.
        
        Args:
            element_id: Element ID from the ui_dump output
        """
        parser = UIParser()
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                xml_file = os.path.join(tmpdir, "ui_dump.xml")
                parser.dump_ui(xml_file)
                elements = parser.parse_ui(xml_file)
                
                elem = next((e for e in elements if e['id'] == element_id), None)
                if elem is None:
                    return {
                        "error": f"Element {element_id} not found",
                        "available_elements": [e['id'] for e in elements]
                    }
                
                tap(elem['center_x'], elem['center_y'])
                
                return {
                    "success": True,
                    "tapped": elem['label'],
                    "coordinates": (elem['center_x'], elem['center_y'])
                }
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def ui_tap_by_label(label_contains: str) -> Dict[str, Any]:
        """
        Tap on the first element whose label contains the given text.
        Convenience method to avoid looking up element IDs.
        
        Args:
            label_contains: Text that the label should contain (case-insensitive)
        """
        parser = UIParser()
        
        try:
            elements = parser.get_interactive_elements()
            elem = parser.find_by_label(elements, label_contains)
            
            if elem is None:
                return {
                    "error": f"No element containing '{label_contains}' found",
                    "available_labels": [e['label'] for e in elements if e['label']]
                }
            
            tap(elem['center_x'], elem['center_y'])
            
            return {
                "success": True,
                "tapped": elem['label'],
                "coordinates": (elem['center_x'], elem['center_y'])
            }
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def ui_input_text(element_id: int, text: str) -> Dict[str, Any]:
        """
        Tap on an input element and input text.
        
        Args:
            element_id: Element ID from ui_dump
            text: Text to input
        """
        parser = UIParser()
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                xml_file = os.path.join(tmpdir, "ui_dump.xml")
                parser.dump_ui(xml_file)
                elements = parser.parse_ui(xml_file)
                
                elem = next((e for e in elements if e['id'] == element_id), None)
                if elem is None:
                    return {
                        "error": f"Element {element_id} not found",
                        "available_elements": [e['id'] for e in elements]
                    }
                
                # Tap first to focus
                tap(elem['center_x'], elem['center_y'])
                # Then input
                input_text(text)
                
                return {
                    "success": True,
                    "element": elem['label'],
                    "text_input": text
                }
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def ui_input_by_label(label_contains: str, text: str) -> Dict[str, Any]:
        """
        Find input by label and input text.
        
        Args:
            label_contains: Text that the label contains
            text: Text to input
        """
        parser = UIParser()
        
        try:
            elements = parser.get_interactive_elements()
            elem = parser.find_by_label(elements, label_contains)
            
            if elem is None:
                return {
                    "error": f"No element containing '{label_contains}' found"
                }
            
            # Tap first to focus
            tap(elem['center_x'], elem['center_y'])
            # Then input
            input_text(text)
            
            return {
                "success": True,
                "element": elem['label'],
                "text_input": text
            }
        except Exception as e:
            return {"error": str(e)}
