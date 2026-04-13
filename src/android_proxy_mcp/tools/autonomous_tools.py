"""
MCP Tools for autonomous operations - batch decryption, automated exploration
"""

import json
import re
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

from android_proxy_mcp.frida.rpc_client import UnionPayRPCClient
from android_proxy_mcp.core.sqlite_store import TrafficStore


def register_autonomous_tools(mcp: FastMCP) -> None:
    """Register autonomous automation tools"""

    @mcp.tool()
    def autonomous_decrypt_all_captured_traffic(db_path: str = "traffic.db") -> Dict[str, Any]:
        """
        Autonomously decrypt all ciphertexts found in captured traffic using Frida RPC.
        Extracts all long hex strings from response bodies and tries to decrypt them.
        
        Args:
            db_path: Path to SQLite database with captured traffic
        """
        try:
            # Connect Frida
            client = UnionPayRPCClient("com.unionpay.android")
            script_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '../../../../frida-scripts/bypass-capture.js'
            ))
            client.attach(script_path)
            
            # Open traffic store
            store = TrafficStore(db_path)
            flows = store.get_all_flows()
            
            results = []
            total_checked = 0
            total_decrypted = 0
            
            for flow in flows:
                # Check response body for hex ciphertexts
                if flow.response_body:
                    body = flow.response_body
                    if isinstance(body, bytes):
                        try:
                            body = body.decode('utf-8', errors='replace')
                        except:
                            body = ""
                    
                    # Find all long hex strings with even length
                    hex_candidates = re.findall(r'[0-9A-Fa-f]{32,}')
                    hex_candidates = [c for c in hex_candidates if len(c) % 2 == 0]
                    total_checked += len(hex_candidates)
                    
                    for ct in hex_candidates:
                        try:
                            plaintext = client.decrypt(ct)
                            if plaintext and plaintext.strip() and plaintext != ct:
                                total_decrypted += 1
                                results.append({
                                    'flow_id': flow.id,
                                    'url': flow.request.url,
                                    'ciphertext': ct,
                                    'plaintext': plaintext
                                })
                        except:
                            continue
            
            client.detach()
            
            return {
                "total_flows_processed": len(flows),
                "total_hex_candidates": total_checked,
                "successfully_decrypted": total_decrypted,
                "results": results[:50]  # First 50 results
            }
                        
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def run_autonomous_sequence(sequence: List[Dict]) -> Dict[str, Any]:
        """
        Run an automated sequence of UI actions: tap and input.
        Sequence format: [{"type": "tap_by_label", "label": "我的"}, {"type": "input_by_label", "label": "手机号", "text": "13800138000"}, ...]
        
        Args:
            sequence: List of actions to perform
        """
        from android_proxy_mcp.ui.parser import UIParser, tap, input_text
        
        parser = UIParser()
        results = []
        success_count = 0
        
        for i, action in enumerate(sequence):
            action_type = action.get('type')
            results.append({
                'step': i + 1,
                'action': action_type,
                'success': False
            })
            
            try:
                elements = parser.get_interactive_elements()
                
                if action_type == 'tap_by_label':
                    label = action.get('label', '')
                    elem = parser.find_by_label(elements, label)
                    if elem is None:
                        results[-1]['error'] = f"Element '{label}' not found"
                        continue
                    tap(elem['center_x'], elem['center_y'])
                    results[-1]['success'] = True
                    results[-1]['tapped'] = elem['label']
                    success_count += 1
                
                elif action_type == 'input_by_label':
                    label = action.get('label', '')
                    text = action.get('text', '')
                    elem = parser.find_by_label(elements, label)
                    if elem is None:
                        results[-1]['error'] = f"Element '{label}' not found"
                        continue
                    tap(elem['center_x'], elem['center_y'])
                    input_text(text)
                    results[-1]['success'] = True
                    results[-1]['input'] = text
                    success_count += 1
                
                elif action_type == 'tap':
                    elem_id = action.get('element_id')
                    elem = next((e for e in elements if e['id'] == elem_id), None)
                    if elem is None:
                        results[-1]['error'] = f"Element {elem_id} not found"
                        continue
                    tap(elem['center_x'], elem['center_y'])
                    results[-1]['success'] = True
                    success_count += 1
                
                # Wait for screen update
                import time
                time.sleep(2)
                
            except Exception as e:
                results[-1]['error'] = str(e)
        
        return {
            "total_steps": len(sequence),
            "successful_steps": success_count,
            "results": results
        }
