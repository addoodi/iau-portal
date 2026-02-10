"""
DOCX to PDF converter using LibreOffice headless mode.

Requires LibreOffice to be installed:
- Docker: apt-get install libreoffice-writer
- Ubuntu: sudo apt install libreoffice-writer
- Windows: Install LibreOffice and add to PATH
"""
import subprocess
import tempfile
import os
import logging
from io import BytesIO

logger = logging.getLogger(__name__)


def convert_docx_to_pdf(docx_stream: BytesIO) -> BytesIO:
    """
    Convert a DOCX byte stream to PDF using LibreOffice headless.

    Args:
        docx_stream: BytesIO containing the DOCX document

    Returns:
        BytesIO containing the PDF document

    Raises:
        RuntimeError: If LibreOffice conversion fails
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        docx_path = os.path.join(tmpdir, "document.docx")
        with open(docx_path, "wb") as f:
            f.write(docx_stream.read())

        try:
            # Use writer_pdf_Export filter with options for better compatibility
            # SelectPdfVersion=1 = PDF/A-1, ExportFormFields=false flattens form fields
            result = subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--norestore",
                    "--nofirststartwizard",
                    "--convert-to", "pdf:writer_pdf_Export:{'ExportFormFields':{'type':'boolean','value':'false'},'SelectPdfVersion':{'type':'long','value':'0'}}",
                    "--outdir", tmpdir,
                    docx_path
                ],
                check=True,
                timeout=60,
                capture_output=True,
                text=True,
                env={**os.environ, "HOME": tmpdir}  # Set HOME to avoid profile issues
            )
            logger.debug(f"LibreOffice output: {result.stdout}")
        except FileNotFoundError:
            raise RuntimeError(
                "LibreOffice is not installed or not in PATH. "
                "Install with: apt-get install libreoffice-writer"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("PDF conversion timed out after 60 seconds")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"PDF conversion failed: {e.stderr}")

        pdf_path = os.path.join(tmpdir, "document.pdf")
        if not os.path.exists(pdf_path):
            raise RuntimeError("PDF conversion produced no output file")

        with open(pdf_path, "rb") as f:
            return BytesIO(f.read())
