#!/usr/bin/env python3
"""
Simple script to run the EDF Reader test suite.
"""
import sys
import subprocess

def main():
    """Run the test suite with pytest."""
    print("Running EDF Reader test suite...")
    
    try:
        # Run pytest with verbose output
        result = subprocess.run(
            ["pytest", "-v"],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Print the output
        print(result.stdout)
        
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
        
        print("All tests passed successfully!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print("Test execution failed:")
        print(e.stdout)
        print(e.stderr)
        return 1
    except FileNotFoundError:
        print("Error: pytest not found. Please install it with:")
        print("pip install -e .[dev]")
        return 1

if __name__ == "__main__":
    sys.exit(main())