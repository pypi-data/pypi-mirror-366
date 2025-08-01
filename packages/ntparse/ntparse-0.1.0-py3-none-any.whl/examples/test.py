from ntparse import parse_ntdll, to_json, to_csv

# Parse syscalls from default ntdll.dll
syscalls = parse_ntdll()

# Parse from custom path
syscalls = parse_ntdll("C:\\Users\\devil\\Desktop\\ntdell.dll")

# Convert to different formats
json_output = to_json(syscalls)
csv_output = to_csv(syscalls)

print(f"Found {len(syscalls)} syscalls")
print(json_output)