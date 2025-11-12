# receipt_generator.py
"""
PDF Receipt Generator for payment and collection receipts
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

# Register Greek-compatible fonts
try:
    # Try to register DejaVu fonts (common on most systems)
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Oblique', 'DejaVuSans-Oblique.ttf'))
    FONT_NAME = 'DejaVuSans'
    FONT_BOLD = 'DejaVuSans-Bold'
    FONT_OBLIQUE = 'DejaVuSans-Oblique'
except:
    # If DejaVu not found, try to find fonts in common locations
    import platform
    system = platform.system()

    try:
        if system == 'Windows':
            # Try Arial Unicode MS or other Windows fonts that support Greek
            pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:\\Windows\\Fonts\\arialbd.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Oblique', 'C:\\Windows\\Fonts\\ariali.ttf'))
            FONT_NAME = 'Arial'
            FONT_BOLD = 'Arial-Bold'
            FONT_OBLIQUE = 'Arial-Oblique'
        elif system == 'Linux':
            # Try Liberation Sans on Linux
            pdfmetrics.registerFont(TTFont('LiberationSans', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'))
            pdfmetrics.registerFont(TTFont('LiberationSans-Bold', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'))
            pdfmetrics.registerFont(TTFont('LiberationSans-Oblique', '/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf'))
            FONT_NAME = 'LiberationSans'
            FONT_BOLD = 'LiberationSans-Bold'
            FONT_OBLIQUE = 'LiberationSans-Oblique'
        else:
            # MacOS or fallback
            FONT_NAME = 'Helvetica'
            FONT_BOLD = 'Helvetica-Bold'
            FONT_OBLIQUE = 'Helvetica-Oblique'
    except:
        # Final fallback to Helvetica (won't show Greek properly but won't crash)
        FONT_NAME = 'Helvetica'
        FONT_BOLD = 'Helvetica-Bold'
        FONT_OBLIQUE = 'Helvetica-Oblique'

class ReceiptGenerator:
    def __init__(self, company_name="", company_address="", company_phone="", company_email="", company_tax_id="", logo_path=None, signature_path=None):
        self.company_name = company_name
        self.company_address = company_address
        self.company_phone = company_phone
        self.company_email = company_email
        self.company_tax_id = company_tax_id
        self.logo_path = logo_path
        self.signature_path = signature_path

    def generate_payment_receipt(self, output_path, receipt_number, customer_name, amount, service_description, payment_date=None, notes=""):
        """
        Generates a payment receipt (Απόδειξη Πληρωμής)
        """
        if payment_date is None:
            payment_date = datetime.now().strftime("%d/%m/%Y")

        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # Header section with logo and company info side by side
        y_pos = height - 2*cm

        # Logo on the left (if provided)
        logo_x = 2*cm
        company_info_x = 7*cm  # Company info starts here

        if self.logo_path and os.path.exists(self.logo_path):
            try:
                img = Image.open(self.logo_path)
                img_width, img_height = img.size
                aspect = img_height / float(img_width)
                logo_width = 4*cm
                logo_height = logo_width * aspect
                if logo_height > 3*cm:
                    logo_height = 3*cm
                    logo_width = logo_height / aspect
                c.drawImage(self.logo_path, logo_x, y_pos - logo_height, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
            except:
                pass

        # Company Header (to the right of logo)
        c.setFont(FONT_BOLD, 16)
        c.drawString(company_info_x, height - 2.5*cm, self.company_name if self.company_name else "Επωνυμία Εταιρείας")

        c.setFont(FONT_NAME, 10)
        y = height - 3.2*cm
        if self.company_address:
            c.drawString(company_info_x, y, f"Διεύθυνση: {self.company_address}")
            y -= 0.5*cm
        if self.company_phone:
            c.drawString(company_info_x, y, f"Τηλ: {self.company_phone}")
            y -= 0.5*cm
        if self.company_email:
            c.drawString(company_info_x, y, f"Email: {self.company_email}")
            y -= 0.5*cm
        if self.company_tax_id:
            c.drawString(company_info_x, y, f"ΑΦΜ: {self.company_tax_id}")

        # Receipt Title
        c.setFont(FONT_BOLD, 20)
        c.drawCentredString(width/2, height - 7*cm, "ΑΠΟΔΕΙΞΗ ΠΛΗΡΩΜΗΣ")

        # Receipt Number and Date
        c.setFont(FONT_NAME, 11)
        c.drawString(2*cm, height - 8.5*cm, f"Αριθμός Απόδειξης: {receipt_number}")
        c.drawRightString(width - 2*cm, height - 8.5*cm, f"Ημερομηνία: {payment_date}")

        # Draw line
        c.line(2*cm, height - 9*cm, width - 2*cm, height - 9*cm)

        # Customer Information
        y = height - 10*cm
        c.setFont(FONT_BOLD, 12)
        c.drawString(2*cm, y, "Στοιχεία Πελάτη:")
        y -= 0.7*cm
        c.setFont(FONT_NAME, 11)
        c.drawString(2*cm, y, f"Όνομα: {customer_name}")

        # Service and Amount
        y -= 1.5*cm
        c.setFont(FONT_BOLD, 12)
        c.drawString(2*cm, y, "Περιγραφή Υπηρεσίας:")
        y -= 0.7*cm
        c.setFont(FONT_NAME, 11)

        # Wrap service description if too long
        max_width = width - 4*cm
        lines = self._wrap_text(service_description, max_width, c, FONT_NAME, 11)
        for line in lines:
            c.drawString(2*cm, y, line)
            y -= 0.5*cm

        # Amount Box
        y -= 1*cm
        c.setFont(FONT_BOLD, 14)
        c.drawString(2*cm, y, "Ποσό Πληρωμής:")
        c.drawRightString(width - 2*cm, y, f"{amount:.2f} €")

        # Notes if provided
        if notes:
            y -= 1.5*cm
            c.setFont(FONT_BOLD, 11)
            c.drawString(2*cm, y, "Παρατηρήσεις:")
            y -= 0.6*cm
            c.setFont(FONT_NAME, 10)
            notes_lines = self._wrap_text(notes, max_width, c, FONT_NAME, 10)
            for line in notes_lines:
                c.drawString(2*cm, y, line)
                y -= 0.5*cm

        # Dual Signature Section
        sig_y = 5*cm

        # Left signature (Engineer/Company)
        if self.signature_path and os.path.exists(self.signature_path):
            try:
                c.drawImage(self.signature_path, 2*cm, sig_y, width=4*cm, height=2*cm, preserveAspectRatio=True, mask='auto')
            except:
                pass
        else:
            # Signature line for company
            c.line(2*cm, sig_y, 6*cm, sig_y)

        c.setFont(FONT_NAME, 9)
        c.drawCentredString(4*cm, sig_y - 0.5*cm, "Υπογραφή / Σφραγίδα Μηχανικού")

        # Right signature (Client)
        c.line(width - 8*cm, sig_y, width - 4*cm, sig_y)
        c.setFont(FONT_NAME, 9)
        c.drawCentredString(width - 6*cm, sig_y - 0.5*cm, "Υπογραφή / Σφραγίδα Πελάτη")

        # Footer
        c.setFont(FONT_OBLIQUE, 8)
        c.drawCentredString(width/2, 1.5*cm, "Ευχαριστούμε για την προτίμησή σας!")

        c.save()
        return output_path

    def generate_collection_receipt(self, output_path, receipt_number, customer_name, amount, service_description, collection_date=None, notes=""):
        """
        Generates a collection receipt (Απόδειξη Είσπραξης)
        """
        if collection_date is None:
            collection_date = datetime.now().strftime("%d/%m/%Y")

        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # Header section with logo and company info side by side
        y_pos = height - 2*cm

        # Logo on the left (if provided)
        logo_x = 2*cm
        company_info_x = 7*cm  # Company info starts here

        if self.logo_path and os.path.exists(self.logo_path):
            try:
                img = Image.open(self.logo_path)
                img_width, img_height = img.size
                aspect = img_height / float(img_width)
                logo_width = 4*cm
                logo_height = logo_width * aspect
                if logo_height > 3*cm:
                    logo_height = 3*cm
                    logo_width = logo_height / aspect
                c.drawImage(self.logo_path, logo_x, y_pos - logo_height, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
            except:
                pass

        # Company Header (to the right of logo)
        c.setFont(FONT_BOLD, 16)
        c.drawString(company_info_x, height - 2.5*cm, self.company_name if self.company_name else "Επωνυμία Εταιρείας")

        c.setFont(FONT_NAME, 10)
        y = height - 3.2*cm
        if self.company_address:
            c.drawString(company_info_x, y, f"Διεύθυνση: {self.company_address}")
            y -= 0.5*cm
        if self.company_phone:
            c.drawString(company_info_x, y, f"Τηλ: {self.company_phone}")
            y -= 0.5*cm
        if self.company_email:
            c.drawString(company_info_x, y, f"Email: {self.company_email}")
            y -= 0.5*cm
        if self.company_tax_id:
            c.drawString(company_info_x, y, f"ΑΦΜ: {self.company_tax_id}")

        # Receipt Title
        c.setFont(FONT_BOLD, 20)
        c.drawCentredString(width/2, height - 7*cm, "ΑΠΟΔΕΙΞΗ ΕΙΣΠΡΑΞΗΣ")

        # Receipt Number and Date
        c.setFont(FONT_NAME, 11)
        c.drawString(2*cm, height - 8.5*cm, f"Αριθμός Απόδειξης: {receipt_number}")
        c.drawRightString(width - 2*cm, height - 8.5*cm, f"Ημερομηνία: {collection_date}")

        # Draw line
        c.line(2*cm, height - 9*cm, width - 2*cm, height - 9*cm)

        # Customer Information
        y = height - 10*cm
        c.setFont(FONT_BOLD, 12)
        c.drawString(2*cm, y, "Είσπραξη από:")
        y -= 0.7*cm
        c.setFont(FONT_NAME, 11)
        c.drawString(2*cm, y, f"Όνομα: {customer_name}")

        # Service and Amount
        y -= 1.5*cm
        c.setFont(FONT_BOLD, 12)
        c.drawString(2*cm, y, "Περιγραφή:")
        y -= 0.7*cm
        c.setFont(FONT_NAME, 11)

        # Wrap service description if too long
        max_width = width - 4*cm
        lines = self._wrap_text(service_description, max_width, c, FONT_NAME, 11)
        for line in lines:
            c.drawString(2*cm, y, line)
            y -= 0.5*cm

        # Amount Box
        y -= 1*cm
        c.setFont(FONT_BOLD, 14)
        c.drawString(2*cm, y, "Ποσό Είσπραξης:")
        c.drawRightString(width - 2*cm, y, f"{amount:.2f} €")

        # Notes if provided
        if notes:
            y -= 1.5*cm
            c.setFont(FONT_BOLD, 11)
            c.drawString(2*cm, y, "Παρατηρήσεις:")
            y -= 0.6*cm
            c.setFont(FONT_NAME, 10)
            notes_lines = self._wrap_text(notes, max_width, c, FONT_NAME, 10)
            for line in notes_lines:
                c.drawString(2*cm, y, line)
                y -= 0.5*cm

        # Dual Signature Section
        sig_y = 5*cm

        # Left signature (Engineer/Company)
        if self.signature_path and os.path.exists(self.signature_path):
            try:
                c.drawImage(self.signature_path, 2*cm, sig_y, width=4*cm, height=2*cm, preserveAspectRatio=True, mask='auto')
            except:
                pass
        else:
            # Signature line for company
            c.line(2*cm, sig_y, 6*cm, sig_y)

        c.setFont(FONT_NAME, 9)
        c.drawCentredString(4*cm, sig_y - 0.5*cm, "Υπογραφή / Σφραγίδα Μηχανικού")

        # Right signature (Client)
        c.line(width - 8*cm, sig_y, width - 4*cm, sig_y)
        c.setFont(FONT_NAME, 9)
        c.drawCentredString(width - 6*cm, sig_y - 0.5*cm, "Υπογραφή / Σφραγίδα Πελάτη")

        # Footer
        c.setFont(FONT_OBLIQUE, 8)
        c.drawCentredString(width/2, 1.5*cm, "Ευχαριστούμε για την συνεργασία!")

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
