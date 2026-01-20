import sys
import importlib.util

def check_install(package):
    spec = importlib.util.find_spec(package)
    return spec is not None

lib = None
if check_install("pypdf"):
    lib = "pypdf"
    from pypdf import PdfReader
elif check_install("PyPDF2"):
    lib = "PyPDF2"
    from PyPDF2 import PdfReader

if lib is None:
    print("MISSING_LIBS")
    sys.exit(0)

try:
    reader = PdfReader("VikasRaoot_M.pdf")
    text = ""
    for page in reader.pages:
        # Try to use layout mode if available, otherwise default
        try:
            text += page.extract_text(extraction_mode="layout") + "\n"
        except TypeError:
            text += page.extract_text() + "\n"
    
    with open("resume_text_v2.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Extraction complete.")
except Exception as e:
    print(f"ERROR: {e}")
