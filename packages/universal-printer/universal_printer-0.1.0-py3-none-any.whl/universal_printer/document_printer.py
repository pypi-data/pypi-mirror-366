import os
import platform
import subprocess
import tempfile
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DocumentPrinter:
    """
    Cross-platform printer using only stdlib. 
    Provides a naive PDF fallback by manually constructing a minimal PDF.
    """

    def __init__(self):
        self.system = platform.system()
        self.downloads_path = Path.home() / "Downloads"

    def _write_temp_text(self, content) -> Path:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
        f.write(str(content))
        f.flush()
        f.close()
        return Path(f.name)

    def _write_minimal_pdf(self, content, output_path: Path) -> bool:
        """
        Very naive PDF writer: places text in a single page using default fonts.
        Not full-featured; works for basic ASCII lines. 
        """
        try:
            lines = str(content).splitlines()
            # PDF objects
            objs = []
            xref_offsets = []

            def add_obj(s):
                xref_offsets.append(len(b''.join(objs)))
                objs.append(s)
                return len(xref_offsets)  # object number

            # Catalog
            # Prepare content stream: simple text using BT/ET
            text_lines = []
            text_lines.append("BT /F1 12 Tf 50 750 Td")
            for line in lines:
                safe = line.replace("(", "\\(").replace(")", "\\)")
                text_lines.append(f"({safe}) Tj 0 -14 Td")
            text_stream = "\n".join(text_lines)
            stream = f"""q
1 0 0 1 0 0 cm
BT
/F1 12 Tf
50 750 Td
{text_stream}
ET
Q
"""
            # Create font object
            font_obj_num = add_obj(f"""<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>""".encode("utf-8"))
            # Content stream object
            content_stream_bytes = stream.encode("utf-8")
            content_obj_num = add_obj(
                f"""<< /Length {len(content_stream_bytes)} >>\nstream\n{stream}\nendstream""".encode("utf-8")
            )
            # Page object
            page_obj_num = add_obj(
                f"""<< /Type /Page /Parent 4 0 R /Resources << /Font << /F1 {font_obj_num} 0 R >> >> /Contents {content_obj_num} 0 R /MediaBox [0 0 612 792] >>""".encode("utf-8")
            )
            # Pages root
            pages_obj_num = add_obj(
                f"""<< /Type /Pages /Kids [ {page_obj_num} 0 R ] /Count 1 >>""".encode("utf-8")
            )
            # Catalog
            catalog_obj_num = add_obj(f"""<< /Type /Catalog /Pages {pages_obj_num} 0 R >>""".encode("utf-8"))

            # Build PDF binary
            pdf = b"%PDF-1.4\n"
            # write objects with numbering
            for idx, obj in enumerate(objs, start=1):
                xref_offsets[idx - 1] = len(pdf)
                pdf += f"{idx} 0 obj\n".encode("utf-8")
                if isinstance(obj, bytes):
                    pdf += obj
                else:
                    pdf += obj.encode("utf-8")
                pdf += b"\nendobj\n"
            # xref
            xref_start = len(pdf)
            pdf += b"xref\n"
            pdf += f"0 {len(objs)+1}\n".encode("utf-8")
            pdf += b"0000000000 65535 f \n"
            for offset in xref_offsets:
                pdf += f"{offset:010d} 00000 n \n".encode("utf-8")
            # trailer
            pdf += b"trailer\n"
            pdf += f"""<< /Size {len(objs)+1} /Root {catalog_obj_num} 0 R >>\n""".encode("utf-8")
            pdf += b"startxref\n"
            pdf += f"{xref_start}\n".encode("utf-8")
            pdf += b"%%EOF\n"

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(pdf)
            logger.info(f"Minimal PDF written to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write minimal PDF: {e}")
            return False

    def _fallback_pdf_save(self, content, filename=None):
        if not filename:
            filename = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        elif not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        pdf_path = self.downloads_path / filename
        success = self._write_minimal_pdf(content, pdf_path)
        if success:
            return pdf_path
        # Last-resort: plain text with .pdf extension (warn)
        try:
            with open(pdf_path, "w", encoding="utf-8") as f:
                f.write("<< WARNING: Could not build PDF, fallback to text >>\n")
                f.write(str(content))
            logger.info(f"Fallback text-as-.pdf written to {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Final fallback write failed: {e}")
            return None

    def _print_unix(self, file_path: Path, printer_name=None, to_pdf_path: Path = None):
        cmd = ["lp"]
        if printer_name:
            cmd += ["-d", printer_name]
        if to_pdf_path:
            # CUPS print-to-file (PDF) if supported
            cmd += ["-o", f"outputfile={to_pdf_path}"]
        cmd.append(str(file_path))
        return subprocess.run(cmd, capture_output=True, check=True)

    def _print_windows(self, file_path: Path, printer_name=None):
        # If the user wants Microsoft Print to PDF, the system normally pops up a dialog.
        if printer_name and "Microsoft Print to PDF" in printer_name:
            # Use ShellExecute print verb
            subprocess.run(
                ["rundll32.exe", "shell32.dll,ShellExec_RunDLL", str(file_path), "print"],
                check=True,
            )
            return
        # Generic print via shell verb
        try:
            subprocess.run(
                ["rundll32.exe", "shell32.dll,ShellExec_RunDLL", str(file_path), "print"],
                check=True,
            )
        except subprocess.CalledProcessError:
            # Fallback to notepad for .txt
            if file_path.suffix.lower() == ".txt":
                cmd = f'notepad /P "{file_path}"'
                subprocess.run(cmd, shell=True, check=True)
            else:
                raise

    def print_document(self, content, printer_name=None, fallback_to_pdf=True, pdf_filename=None):
        """
        Print the given content (string or existing filepath). If printing fails, optional PDF fallback.
        Returns: (success: bool, message: str, pdf_path_or_None)
        """
        temp_file = None
        try:
            if isinstance(content, str) and os.path.isfile(content):
                file_path = Path(content)
            else:
                file_path = self._write_temp_text(content)
                temp_file = file_path

            if self.system in ("Darwin", "Linux"):
                try:
                    # If printer_name indicates PDF, interpret as print-to-PDF
                    to_pdf = None
                    if printer_name and "pdf" in printer_name.lower():
                        default_pdf_name = pdf_filename or f"print_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        to_pdf = self.downloads_path / default_pdf_name
                    self._print_unix(file_path, printer_name=printer_name, to_pdf_path=to_pdf)
                    return True, "Printed successfully via lp.", None
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Unix print failed: {e}; stderr: {getattr(e, 'stderr', None)}")
                    raise

            elif self.system == "Windows":
                try:
                    self._print_windows(file_path, printer_name=printer_name)
                    return True, "Printed successfully on Windows.", None
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Windows print failed: {e}")
                    raise

            else:
                return False, f"Unsupported OS: {self.system}", None

        except Exception as e:
            logger.error(f"Printing error: {e}")
            if fallback_to_pdf:
                pdf_path = self._fallback_pdf_save(content, pdf_filename)
                if pdf_path:
                    return False, f"Printing failed. PDF fallback saved to: {pdf_path}", str(pdf_path)
                else:
                    return False, "Printing failed. PDF fallback also failed.", None
            else:
                return False, "Printing failed and fallback disabled.", None
        finally:
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    logger.debug("Could not delete temp file; ignoring.")
