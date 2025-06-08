# Baruh Ifraimov - 208526012 | Dor Cohen - 211896279
'''
DNS Query Log Decoder for BIND9

This script parses BIND9 query logs to extract data exfiltrated via DNS queries.
It assumes data is hex-encoded and embedded as the first label in a specific subdomain.

Example query format expected: <hex_encoded_data_chunk>.exfil.mylocal.net
'''
import re
import argparse
import binascii
from datetime import datetime # Added import

# --- Configuration ---
# The unique label used in your DNS queries that identifies exfiltration attempts.
# For example, if queries are <data>.exfil.mylocal.net, then TARGET_LABEL is "exfil.mylocal.net".
# Queries not matching this pattern will be ignored.
DEFAULT_TARGET_DOMAIN_SUFFIX = "ns1.mylocal.net"

# Log file path
DEFAULT_LOG_FILE = "/var/log/named/query.log"

# Output file for decoded data
DEFAULT_OUTPUT_FILE = "received_data.txt" # Base name, will be timestamped

# Encoding of the data chunks (e.g., "hex", "base64", "plain")
DEFAULT_ENCODING = "base64"

# --- End Configuration ---

def decode_data(encoded_chunk, encoding_type):
    '''Decodes a single data chunk.'''
    if encoding_type == "hex":
        try:
            return binascii.unhexlify(encoded_chunk).decode('utf-8', 'replace')
        except binascii.Error:
            print(f"[!] Warning: Could not hex-decode chunk: {encoded_chunk}")
            return None
        except UnicodeDecodeError:
            print(f"[!] Warning: Could not UTF-8 decode chunk after hex decoding: {encoded_chunk}")
            # Return raw bytes if UTF-8 fails, or handle as error
            return binascii.unhexlify(encoded_chunk).decode('latin-1', 'replace') 
    elif encoding_type == "base64":
        try:
            # Correctly add padding if necessary.
            # A valid Base64 string length is a multiple of 4.
            # The unpadded string length can be L % 4 == 0 (no padding needed),
            # L % 4 == 2 (needs '=='), L % 4 == 3 (needs '=').
            # L % 4 == 1 is invalid but the library might catch it.
            missing_padding = len(encoded_chunk) % 4
            if missing_padding != 0:
                encoded_chunk += '=' * (4 - missing_padding)
            
            return binascii.a2b_base64(encoded_chunk).decode('utf-8', 'replace')
        except binascii.Error as e: # Catch specific error for better feedback
            print(f"[!] Warning: Could not base64-decode chunk: {encoded_chunk}. Error: {e}")
            return None
        except UnicodeDecodeError:
            print(f"[!] Warning: Could not UTF-8 decode chunk after base64 decoding: {encoded_chunk}")
            return binascii.a2b_base64(encoded_chunk).decode('latin-1', 'replace')
    elif encoding_type == "plain":
        return encoded_chunk
    else:
        raise ValueError(f"Unsupported encoding type: {encoding_type}")

def parse_log_file(log_file_path, target_domain_suffix, encoding_type):
    '''Parses the BIND9 query log file and extracts exfiltrated data.'''
    print(f"[*] Parsing log file: {log_file_path}")
    print(f"[*] Looking for queries ending with: .{target_domain_suffix}")
    print(f"[*] Assuming data chunks are encoded as: {encoding_type}")

    extracted_data_chunks_dict = {}
    # Using a raw string for the regex pattern is generally safer.
    # Corrected regex: use single backslash for literal parentheses.
    log_pattern = re.compile(r"client .* \((.*?)\): query: .* IN") # This is line 75
    # print(f"DEBUG: Using regex pattern: '{log_pattern.pattern}'") # Keep this commented for now


    try:
        with open(log_file_path, 'r') as f:
            for line_number, line in enumerate(f, 1):
                # print(f"DEBUG Attempting match on line {line_number}: [{line.rstrip()}]") # Ensure this is active
                match = log_pattern.search(line)
                if match:
                    queried_hostname = match.group(1)
                    # Activated DEBUG print
                    # print(f"DEBUG Line {line_number}: Regex matched. Captured hostname: '{queried_hostname}'")

                    if queried_hostname.endswith(target_domain_suffix):
                        # print(f"DEBUG Line {line_number}: Hostname '{queried_hostname}' MATCHED suffix '{target_domain_suffix}'.") # Re-enabled this
                        # Check if the hostname is longer than the suffix itself, implying there's a prefix.
                        if len(queried_hostname) > len(target_domain_suffix) and queried_hostname[-(len(target_domain_suffix) + 1)] == '.':
                            # print(f"DEBUG Line {line_number}: Hostname '{queried_hostname}' also has a preceding part.") # Keep this commented
                            
                            data_part_hostname = queried_hostname[:-(len(target_domain_suffix) + 1)]
                            parts = data_part_hostname.split('.')
                            
                            if len(parts) >= 2: # Expecting "chunk<N>" and "DATA"
                                sequence_id_str = parts[0]
                                encoded_chunk = parts[1] # This assumes data is always the second part after sequence_id
                                # What if data itself has dots? client script base64 encodes, so it shouldn't have dots unless the base64 alphabet was modified.
                                # Standard base64 (A-Z, a-z, 0-9, +, /) does not include '.'
                                # If parts has more than 2, e.g. chunk0.part1.part2.ns1.mylocal.net, this logic takes only part1.
                                # The client script generates chunk{i}.{encoded}.ns1.mylocal.net, so parts should be [chunk{i}, encoded]
                                
                                # print(f"DEBUG Line {line_number}: Extracted data_part: '{data_part_hostname}', sequence_id: '{sequence_id_str}', encoded_chunk: '{encoded_chunk}'")

                                seq_match = re.match(r"data(\d+)", sequence_id_str)
                                if seq_match:
                                    sequence_number = int(seq_match.group(1))
                                    raw_decoded_output = decode_data(encoded_chunk, encoding_type)
                                    # print(f"DEBUG Line {line_number}: Raw output from decode_data for '{encoded_chunk}': '{raw_decoded_output}' (Type: {type(raw_decoded_output)})")
                                    
                                    if raw_decoded_output:
                                        extracted_data_chunks_dict[sequence_number] = raw_decoded_output
                                        print(f"[+] Line {line_number}: Stored chunk {sequence_number} ('{encoded_chunk}'), decoded to '{raw_decoded_output[:30]}...'")
                                    else:
                                        print(f"[!] Line {line_number}: Decoded output for chunk {sequence_number} ('{encoded_chunk}') is None or empty, not storing.")
                                else:
                                    print(f"[!] Line {line_number}: Sequence ID '{sequence_id_str}' from '{queried_hostname}' did not match 'data<number>' format.")
                            else:
                                print(f"[!] Line {line_number}: Hostname '{queried_hostname}' matched suffix but data part '{data_part_hostname}' had < 2 parts after split (expected 'data<N>.data'). Parts: {parts}")
                        else:
                            # print(f"DEBUG Line {line_number}: Hostname '{queried_hostname}' matched suffix '{target_domain_suffix}' but is not of the form 'prefix.{target_domain_suffix}' or is too short.")
                            pass # Keep logic flow, but no verbose debug for non-matching internal structure
                    else:
                        # print(f"DEBUG Line {line_number}: Hostname '{queried_hostname}' DID NOT match suffix '{target_domain_suffix}' using endswith().")
                        pass # This is common for non-target queries, suppress debug
                else:
                    # Uncommented and enhanced this else block for clarity
                    # print(f"DEBUG Line {line_number}: No regex match for line: [{line.rstrip()}]")
                    pass # This is common for non-query lines, suppress debug
    except FileNotFoundError:
        print(f"[!] Error: Log file not found: {log_file_path}")
        return ""
    except Exception as e:
        print(f"[!] An error occurred while reading the log file: {e}")
        return ""

    # Sort chunks by sequence number and join
    if not extracted_data_chunks_dict: # Check if dictionary is empty
        return ""

    sorted_chunks = [extracted_data_chunks_dict[key] for key in sorted(extracted_data_chunks_dict.keys())]
    return "".join(sorted_chunks)

def main():
    parser = argparse.ArgumentParser(description="Decode data exfiltrated via BIND9 DNS query logs.")
    parser.add_argument("--log-file", default=DEFAULT_LOG_FILE,
                        help=f"Path to the BIND9 query log file (default: {DEFAULT_LOG_FILE})")
    parser.add_argument("--target-suffix", default=DEFAULT_TARGET_DOMAIN_SUFFIX,
                        help=f"The domain suffix that identifies exfiltration queries (e.g., exfil.mylocal.net) (default: {DEFAULT_TARGET_DOMAIN_SUFFIX})")
    # Output file argument will be used as a base if provided, otherwise default base name
    parser.add_argument("--output-file-base", default=DEFAULT_OUTPUT_FILE, 
                        help=f"Base name for the output file (timestamp will be added) (default: {DEFAULT_OUTPUT_FILE})")
    parser.add_argument("--encoding", default=DEFAULT_ENCODING, choices=["hex", "base64", "plain"],
                        help=f"Encoding type of the data chunks (default: {DEFAULT_ENCODING})")

    args = parser.parse_args()

    print("DNS Log Decoder Started")
    decoded_content = parse_log_file(args.log_file, args.target_suffix, args.encoding)

    if decoded_content:
        # Generate timestamped output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Ensure the base name ends with .txt or similar, or handle it
        if '.' in args.output_file_base:
            name_part, ext_part = args.output_file_base.rsplit('.', 1)
            output_filename = f"{name_part}_{timestamp}.{ext_part}"
        else:
            output_filename = f"{args.output_file_base}_{timestamp}.txt"

        try:
            with open(output_filename, 'w') as f:
                f.write(decoded_content)
            print(f"[+] Decoded data successfully written to: {output_filename}")
            print(f"[*] --- Decoded Content (first 500 chars) ---")
            print(decoded_content[:500])
            print("[*] --- End of Preview ---")
        except IOError as e:
            print(f"[!] Error writing to output file {output_filename}: {e}")
    else:
        print("[-] No data extracted or decoded.")

    print("DNS Log Decoder Finished")

if __name__ == "__main__":
    main()
