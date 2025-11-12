# receipt_generator.py
"""
PDF Receipt Generator for payment and collection receipts with Greek support
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image
import sys

class ReceiptGenerator:
    def __init__(self, company_name="", company_address="", company_phone="", company_email="", company_tax_id="", logo_path=None, signature_path=None):
        self.company_name = company_name
        self.company_address = company_address
        self.company_phone = company_phone
        self.company_email = company_email
        self.company_tax_id = company_tax_id
        self.logo_path = logo_path
        self.signature_path = signature_path

        # Try to register Greek-compatible fonts
        self.greek_font = "Helvetica"
        self.greek_font_bold = "Helvetica-Bold"

        try:
            # Try to find and register Arial font (supports Greek)
            if sys.platform == "win32":
                font_path = "C:\\Windows\\Fonts\\arial.ttf"
                font_bold_path = "C:\\Windows\\Fonts\\arialbd.ttf"
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('ArialUnicode', font_path))
                    self.greek_font = 'ArialUnicode'
                if os.path.exists(font_bold_path):
                    pdfmetrics.registerFont(TTFont('ArialUnicodeBold', font_bold_path))
                    self.greek_font_bold = 'ArialUnicodeBold'
        except:
            # Fallback to Helvetica
            pass

    def _format_date(self, date_str):
        """Convert date from YYYY-MM-DD to DD/MM/YY format"""
        try:
            if '/' in date_str:
                # Already in DD/MM/YY format
                return date_str
            # Parse YYYY-MM-DD format
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.strftime('%d/%m/%y')
        except:
            return date_str

    def generate_payment_receipt(self, output_path, receipt_number, customer_name, amount, service_description, payment_date=None, notes="", custom_notes=""):
        """
        Generates a payment receipt (Απόδειξη Πληρωμής)
        """
        if payment_date is None:
            payment_date = datetime.now().strftime("%d/%m/%y")
        else:
            payment_date = self._format_date(payment_date)

        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # Draw logo if provided
        y_pos = height - 2*cm
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                img = Image.open(self.logo_path)
                img_width, img_height = img.size
                aspect = img_height / float(img_width)
                logo_width = 3*cm
                logo_height = logo_width * aspect
                if logo_height > 2*cm:
                    logo_height = 2*cm
                    logo_width = logo_height / aspect
                c.drawImage(self.logo_path, 2*cm, y_pos - logo_height, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
            except:
                pass

        # Company Header
        c.setFont(self.greek_font_bold, 16)
        c.drawString(8*cm, height - 2.5*cm, self.company_name if self.company_name else "Company Name")

        c.setFont(self.greek_font, 10)
        y = height - 3.2*cm
        if self.company_address:
            c.drawString(8*cm, y, f"Address: {self.company_address}")
            y -= 0.5*cm
        if self.company_phone:
            c.drawString(8*cm, y, f"Phone: {self.company_phone}")
            y -= 0.5*cm
        if self.company_email:
            c.drawString(8*cm, y, f"Email: {self.company_email}")
            y -= 0.5*cm
        if self.company_tax_id:
            c.drawString(8*cm, y, f"Tax ID: {self.company_tax_id}")

        # Receipt Title
        c.setFont(self.greek_font_bold, 20)
        c.drawCentredString(width/2, height - 7*cm, "PAYMENT RECEIPT")

        # Receipt Number and Date
        c.setFont(self.greek_font, 11)
        c.drawString(2*cm, height - 8.5*cm, f"Receipt No: {receipt_number}")
        c.drawRightString(width - 2*cm, height - 8.5*cm, f"Date: {payment_date}")

        # Draw line
        c.line(2*cm, height - 9*cm, width - 2*cm, height - 9*cm)

        # Customer Information
        y = height - 10*cm
        c.setFont(self.greek_font_bold, 12)
        c.drawString(2*cm, y, "Customer Details:")
        y -= 0.7*cm
        c.setFont(self.greek_font, 11)
        c.drawString(2*cm, y, f"Name: {customer_name}")

        # Service and Amount
        y -= 1.5*cm
        c.setFont(self.greek_font_bold, 12)
        c.drawString(2*cm, y, "Service Description:")
        y -= 0.7*cm
        c.setFont(self.greek_font, 11)

        # Wrap service description if too long
        max_width = width - 4*cm
        lines = self._wrap_text(service_description, max_width, c, self.greek_font, 11)
        for line in lines:
            c.drawString(2*cm, y, line)
            y -= 0.5*cm

        # Amount Box
        y -= 1*cm
        c.setFont(self.greek_font_bold, 14)
        c.drawString(2*cm, y, "Payment Amount:")
        c.drawRightString(width - 2*cm, y, f"{amount:.2f} EUR")

        # Transaction Notes (from database)
        if notes:
            y -= 1.5*cm
            c.setFont(self.greek_font_bold, 11)
            c.drawString(2*cm, y, "Transaction Notes:")
            y -= 0.6*cm
            c.setFont(self.greek_font, 10)
            notes_lines = self._wrap_text(notes, max_width, c, self.greek_font, 10)
            for line in notes_lines:
                c.drawString(2*cm, y, line)
                y -= 0.5*cm

        # Custom Notes (from receipt dialog)
        if custom_notes:
            y -= 1*cm
            c.setFont(self.greek_font_bold, 11)
            c.drawString(2*cm, y, "Additional Notes:")
            y -= 0.6*cm
            c.setFont(self.greek_font, 10)
            custom_notes_lines = self._wrap_text(custom_notes, max_width, c, self.greek_font, 10)
            for line in custom_notes_lines:
                c.drawString(2*cm, y, line)
                y -= 0.5*cm

        # Signature
        if self.signature_path and os.path.exists(self.signature_path):
            try:
                sig_y = 5*cm
                c.drawImage(self.signature_path, width - 8*cm, sig_y, width=4*cm, height=2*cm, preserveAspectRatio=True, mask='auto')
                c.setFont(self.greek_font, 9)
                c.drawCentredString(width - 6*cm, sig_y - 0.5*cm, "Signature / Stamp")
            except:
                pass
        else:
            # Signature line
            sig_y = 5*cm
            c.line(width - 8*cm, sig_y, width - 4*cm, sig_y)
            c.setFont(self.greek_font, 9)
            c.drawCentredString(width - 6*cm, sig_y - 0.5*cm, "Signature / Stamp")

        # Footer
        c.setFont(self.greek_font, 8)
        c.drawCentredString(width/2, 1.5*cm, "Thank you for your business!")

        c.save()
        return output_path

    def generate_collection_receipt(self, output_path, receipt_number, customer_name, amount, service_description, collection_date=None, notes="", custom_notes=""):
        """
        Generates a collection receipt (Απόδειξη Είσπραξης)
        """
        if collection_date is None:
            collection_date = datetime.now().strftime("%d/%m/%y")
        else:
            collection_date = self._format_date(collection_date)

        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # Draw logo if provided
        y_pos = height - 2*cm
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                img = Image.open(self.logo_path)
                img_width, img_height = img.size
                aspect = img_height / float(img_width)
                logo_width = 3*cm
                logo_height = logo_width * aspect
                if logo_height > 2*cm:
                    logo_height = 2*cm
                    logo_width = logo_height / aspect
                c.drawImage(self.logo_path, 2*cm, y_pos - logo_height, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
            except:
                pass

        # Company Header
        c.setFont(self.greek_font_bold, 16)
        c.drawString(8*cm, height - 2.5*cm, self.company_name if self.company_name else "Company Name")

        c.setFont(self.greek_font, 10)
        y = height - 3.2*cm
        if self.company_address:
            c.drawString(8*cm, y, f"Address: {self.company_address}")
            y -= 0.5*cm
        if self.company_phone:
            c.drawString(8*cm, y, f"Phone: {self.company_phone}")
            y -= 0.5*cm
        if self.company_email:
            c.drawString(8*cm, y, f"Email: {self.company_email}")
            y -= 0.5*cm
        if self.company_tax_id:
            c.drawString(8*cm, y, f"Tax ID: {self.company_tax_id}")

        # Receipt Title
        c.setFont(self.greek_font_bold, 20)
        c.drawCentredString(width/2, height - 7*cm, "COLLECTION RECEIPT")

        # Receipt Number and Date
        c.setFont(self.greek_font, 11)
        c.drawString(2*cm, height - 8.5*cm, f"Receipt No: {receipt_number}")
        c.drawRightString(width - 2*cm, height - 8.5*cm, f"Date: {collection_date}")

        # Draw line
        c.line(2*cm, height - 9*cm, width - 2*cm, height - 9*cm)

        # Customer Information
        y = height - 10*cm
        c.setFont(self.greek_font_bold, 12)
        c.drawString(2*cm, y, "Collected from:")
        y -= 0.7*cm
        c.setFont(self.greek_font, 11)
        c.drawString(2*cm, y, f"Name: {customer_name}")

        # Service and Amount
        y -= 1.5*cm
        c.setFont(self.greek_font_bold, 12)
        c.drawString(2*cm, y, "Description:")
        y -= 0.7*cm
        c.setFont(self.greek_font, 11)

        # Wrap service description if too long
        max_width = width - 4*cm
        lines = self._wrap_text(service_description, max_width, c, self.greek_font, 11)
        for line in lines:
            c.drawString(2*cm, y, line)
            y -= 0.5*cm

        # Amount Box
        y -= 1*cm
        c.setFont(self.greek_font_bold, 14)
        c.drawString(2*cm, y, "Collection Amount:")
        c.drawRightString(width - 2*cm, y, f"{amount:.2f} EUR")

        # Transaction Notes (from database)
        if notes:
            y -= 1.5*cm
            c.setFont(self.greek_font_bold, 11)
            c.drawString(2*cm, y, "Transaction Notes:")
            y -= 0.6*cm
            c.setFont(self.greek_font, 10)
            notes_lines = self._wrap_text(notes, max_width, c, self.greek_font, 10)
            for line in notes_lines:
                c.drawString(2*cm, y, line)
                y -= 0.5*cm

        # Custom Notes (from receipt dialog)
        if custom_notes:
            y -= 1*cm
            c.setFont(self.greek_font_bold, 11)
            c.drawString(2*cm, y, "Additional Notes:")
            y -= 0.6*cm
            c.setFont(self.greek_font, 10)
            custom_notes_lines = self._wrap_text(custom_notes, max_width, c, self.greek_font, 10)
            for line in custom_notes_lines:
                c.drawString(2*cm, y, line)
                y -= 0.5*cm

        # Signature
        if self.signature_path and os.path.exists(self.signature_path):
            try:
                sig_y = 5*cm
                c.drawImage(self.signature_path, width - 8*cm, sig_y, width=4*cm, height=2*cm, preserveAspectRatio=True, mask='auto')
                c.drawCentredString(width - 6*cm, sig_y - 0.5*cm, "Signature / Stamp")
            except:
                pass
        else:
            # Signature line
            sig_y = 5*cm
            c.line(width - 8*cm, sig_y, width - 4*cm, sig_y)
            c.setFont(self.greek_font, 9)
            c.drawCentredString(width - 6*cm, sig_y - 0.5*cm, "Signature / Stamp")

        # Footer
        c.setFont(self.greek_font, 8)
        c.drawCentredString(width/2, 1.5*cm, "Thank you for your cooperation!")

        c.save()
        return output_path

    def _wrap_text(self, text, max_width, canvas_obj, font_name, font_size):
        """Helper function to wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if canvas_obj.stringWidth(test_line, font_name, font_size) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else [text]
