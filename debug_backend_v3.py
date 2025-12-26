import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

print("--- Starting Backend Diagnostic V3 ---")

try:
    print("1. Attempting to import backend.repositories...")
    from backend.repositories import CSVEmailSettingsRepository
    print("   SUCCESS: CSVEmailSettingsRepository imported.")

    print("2. Attempting to instantiate CSVEmailSettingsRepository...")
    repo = CSVEmailSettingsRepository()
    print("   SUCCESS: CSVEmailSettingsRepository instantiated.")

    print("3. Attempting to import backend.services...")
    from backend.services import EmailSettingsService
    print("   SUCCESS: EmailSettingsService imported.")

    print("4. Attempting to instantiate EmailSettingsService...")
    service = EmailSettingsService(repo)
    print("   SUCCESS: EmailSettingsService instantiated.")

    print("5. Attempting to import backend.main...")
    import backend.main
    print("   SUCCESS: backend.main imported.")

except ImportError as e:
    print(f"   FAIL: ImportError: {e}")
except Exception as e:
    print(f"   FAIL: Exception: {e}")
    import traceback
    traceback.print_exc()

print("--- Diagnostic Complete ---")
