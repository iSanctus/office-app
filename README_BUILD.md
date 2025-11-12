# Οδηγίες Δημιουργίας ZisCRM Executable

## Προαπαιτούμενα

Βεβαιωθείτε ότι έχετε εγκαταστήσει όλα τα απαραίτητα packages:

```bash
pip install -r requirements.txt
```

Ή χειροκίνητα:
```bash
pip install customtkinter Pillow reportlab openpyxl pyinstaller
```

## Μέθοδος 1: Χρήση του Build Script (Συνιστάται) ⭐

Απλά τρέξτε:

```bash
python build_exe.py
```

Αυτό το script θα:
1. ✓ Καθαρίσει τους παλιούς φακέλους build
2. ✓ Εγκαταστήσει το PyInstaller αν δεν υπάρχει
3. ✓ Δημιουργήσει το **ZisCRM.exe** με το logo.ico

## Μέθοδος 2: Χρήση PyInstaller Απευθείας

### Με spec file:
```bash
pyinstaller ZisCRM.spec
```

### Χωρίς spec file:
```bash
pyinstaller --name=ZisCRM --onefile --windowed --icon=logo.ico ^
    --add-data="database.py;." ^
    --add-data="receipt_generator.py;." ^
    --hidden-import=customtkinter ^
    --hidden-import=PIL ^
    --hidden-import=reportlab ^
    --collect-all=customtkinter ^
    --collect-all=reportlab ^
    app.py
```

## Αποτέλεσμα

Το τελικό .exe θα βρίσκεται στον φάκελο: **`dist/ZisCRM.exe`** 📦

## Αρχεία του Project

```
office-app/
├── app.py                    # Κύριο αρχείο εφαρμογής
├── database.py               # Database module
├── receipt_generator.py      # PDF receipt generator
├── logo.ico                  # Εικονίδιο εφαρμογής ⭐
├── build_exe.py             # Build script
├── ZisCRM.spec              # PyInstaller configuration
├── requirements.txt          # Python dependencies
└── README_BUILD.md          # Αυτό το αρχείο
```

## Σημαντικές Σημειώσεις

### 1️⃣ Database Location

Το database path είναι ορισμένο στο `database.py`:
```python
SHARED_PATH = r"\\MYCLOUDEX2ULTRA\documentszis\Τα έγγραφά μου\CRM"
```

**Επιλογές διανομής:**

#### Α. Standalone (Κάθε χρήστης η δική του βάση)
Αλλάξτε σε:
```python
SHARED_PATH = "."
```

#### Β. Network Shared (Κοινόχρηστη βάση)
Κρατήστε το network path ή αλλάξτε σε:
```python
SHARED_PATH = r"\\YOUR-SERVER\Shared\CRM"
```

**ΣΗΜΑΝΤΙΚΟ:** Αλλάξτε το path **ΠΡΙΝ** τρέξετε το build!

### 2️⃣ Fonts για Ελληνικά στο PDF

Το πρόγραμμα υποστηρίζει αυτόματα:
- ✓ **Arial** (Windows - default, λειτουργεί πάντα)
- ✓ **DejaVu Sans** (αν είναι εγκατεστημένο)
- ✓ **Liberation Sans** (Linux)

Στα Windows, το Arial θα λειτουργεί χωρίς πρόβλημα.

### 3️⃣ Εικονίδιο (Icon)

Το **logo.ico** χρησιμοποιείται αυτόματα:
- ✓ Εμφανίζεται στο .exe αρχείο
- ✓ Εμφανίζεται στην taskbar
- ✓ Εμφανίζεται στα Windows

Αν θέλετε να αλλάξετε το icon:
1. Αντικαταστήστε το `logo.ico`
2. Ή αλλάξτε στο spec file: `icon='your_icon.ico'`

### 4️⃣ Πρώτη Εκτέλεση

Κατά την πρώτη εκτέλεση, το ZisCRM θα δημιουργήσει:
- 📁 `company_data.db` - Η βάση δεδομένων
- 📁 `attachments/` - Φάκελος για συνημμένα αρχεία

## Διανομή

### Για Standalone Χρήση:
```
📦 Πακέτο διανομής:
   └── ZisCRM.exe
```
Απλά δώστε το .exe - τα πάντα είναι ενσωματωμένα!

### Για Network Χρήση:
```
📦 Πακέτο διανομής:
   ├── ZisCRM.exe
   └── Οδηγίες:
       - Βεβαιωθείτε ότι όλοι έχουν πρόσβαση στο network path
       - Χρειάζονται δικαιώματα read/write
```

## Troubleshooting 🔧

### ❌ Πρόβλημα: "Failed to execute script"
**Λύση:**
1. Άλλαξε `console=False` σε `console=True` στο spec file
2. Rebuild για να δεις τα errors
3. Ελέγξτε αν λείπουν dependencies

### ❌ Πρόβλημα: Δεν φορτώνουν τα ελληνικά στο PDF
**Λύση:**
- Στα Windows το Arial λειτουργεί αυτόματα ✓
- Αν χρειάζεται, εγκαταστήστε DejaVu fonts

### ❌ Πρόβλημα: "ModuleNotFoundError"
**Λύση:**
1. Προσθέστε το module στα `hiddenimports` στο spec file
2. Rebuild

### ❌ Πρόβλημα: Το .exe είναι πολύ μεγάλο
**Λύση:**
- Αυτό είναι φυσιολογικό για `--onefile` builds (~50-80MB)
- Περιλαμβάνει Python runtime + όλα τα libraries
- Για μικρότερο μέγεθος, χρησιμοποιήστε `--onedir` αντί για `--onefile`

## Testing Checklist ✅

Πριν τη διανομή, δοκιμάστε:

- [ ] Άνοιγμα του προγράμματος
- [ ] Προσθήκη πελάτη
- [ ] Προσθήκη υπηρεσίας
- [ ] Δημιουργία συναλλαγής
- [ ] Δημιουργία PDF απόδειξης με ελληνικά
- [ ] Export σε Excel
- [ ] Import από Excel
- [ ] Αναζήτηση πελάτη
- [ ] Autocomplete λειτουργεί
- [ ] Φάκελος attachments δημιουργείται

## Versioning

Για να δημιουργήσετε νέα έκδοση:

1. ✏️ Κάντε τις αλλαγές στον κώδικα
2. 🔄 Τρέξτε `python build_exe.py`
3. ✓ Δοκιμάστε το νέο ZisCRM.exe
4. 📦 Διανείμετε

## Χρήσιμες Εντολές

```bash
# Καθαρισμός παλιών builds
python build_exe.py

# Ή χειροκίνητα:
pyinstaller ZisCRM.spec

# Για debug (με console window):
# Άλλαξε console=True στο ZisCRM.spec και rebuild
```

## Πληροφορίες Build

- **Όνομα:** ZisCRM.exe
- **Icon:** logo.ico
- **Type:** Single File Executable
- **Console:** Hidden (windowed mode)
- **Size:** ~50-80 MB (περιλαμβάνει όλα τα dependencies)

## Support

Για τεχνική υποστήριξη:
- Ελέγξτε ότι έχετε Python 3.8+
- Ελέγξτε ότι έχετε όλα τα dependencies εγκατεστημένα
- Σβήστε τους φακέλους build/ και dist/ και ξαναδοκιμάστε
- Τρέξτε με console=True για να δείτε errors

---

**🎉 Καλή επιτυχία με τη διανομή του ZisCRM!**
