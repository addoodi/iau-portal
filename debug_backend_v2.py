import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

print("--- Starting Backend Diagnostic ---")

try:
    print("1. Attempting to import backend.main...")
    import backend.main
    print("   SUCCESS: backend.main imported.")
except ImportError as e:
    print(f"   FAIL: ImportError: {e}")
except Exception as e:
    print(f"   FAIL: Exception: {e}")
    import traceback
    traceback.print_exc()

print("--- Diagnostic Complete ---")