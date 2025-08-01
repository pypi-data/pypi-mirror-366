#!/usr/bin/env python3
# basic usage example for ntparse

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import ntparse
sys.path.insert(0, str(Path(__file__).parent.parent))

from ntparse import (
    parse_ntdll, 
    to_json, 
    to_csv, 
    to_asm, 
    to_python_dict
)


def main():
    """Main example function"""
    print("=== ntparse Basic Usage Example ===\n")
    
    try:
        # Parse syscalls from the default ntdll.dll
        print("Parsing syscalls from ntdll.dll...")
        syscalls = parse_ntdll()
        
        if not syscalls:
            print("No syscalls found!")
            return
        
        print(f"Found {len(syscalls)} syscalls\n")
        
        # Show first few syscalls
        print("First 5 syscalls:")
        sorted_syscalls = sorted(syscalls.items(), key=lambda x: x[1])
        for i, (func_name, syscall_num) in enumerate(sorted_syscalls[:5]):
            print(f"  {func_name}: {syscall_num} (0x{syscall_num:02X})")
        
        print("\n" + "="*50 + "\n")
        
        # Demonstrate different output formats
        print("1. JSON Output:")
        json_output = to_json(syscalls)
        print(json_output[:500] + "..." if len(json_output) > 500 else json_output)
        
        print("\n" + "="*50 + "\n")
        
        print("2. CSV Output:")
        csv_output = to_csv(syscalls)
        print(csv_output[:300] + "..." if len(csv_output) > 300 else csv_output)
        
        print("\n" + "="*50 + "\n")
        
        print("3. Assembly Output (first few functions):")
        asm_output = to_asm(syscalls)
        # Show only first few functions
        asm_lines = asm_output.split('\n')
        header_lines = asm_lines[:10]  # Header
        func_lines = []
        for i, line in enumerate(asm_lines[10:], 10):
            if 'PROC' in line and len(func_lines) >= 30:  # Stop after ~3 functions
                break
            func_lines.append(line)
        
        print('\n'.join(header_lines + func_lines) + "\n...")
        
        print("\n" + "="*50 + "\n")
        
        print("4. Python Dictionary Output:")
        py_output = to_python_dict(syscalls)
        # Show only first few entries
        py_lines = py_output.split('\n')
        show_lines = []
        for i, line in enumerate(py_lines):
            if len(show_lines) >= 15:  # Limit output
                break
            show_lines.append(line)
        
        print('\n'.join(show_lines) + "\n...")
        
        print("\n" + "="*50 + "\n")
        
        # Save outputs to files
        print("Saving outputs to files...")
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "syscalls.json", 'w') as f:
            to_json(syscalls, f)
        
        with open(output_dir / "syscalls.csv", 'w') as f:
            to_csv(syscalls, f)
        
        with open(output_dir / "syscalls.asm", 'w') as f:
            to_asm(syscalls, f)
        
        with open(output_dir / "syscalls.py", 'w') as f:
            to_python_dict(syscalls, f)
        
        print(f"Files saved to {output_dir.absolute()}/")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 