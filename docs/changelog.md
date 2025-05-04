# Changelog

## 2023-08-23 - Removed Deprecated Gematria Methods

### Hebrew Methods Removed:
- Mispar Neelam (Hidden Value)
- Mispar Katan (Reduced Value)
- Mispar Katan Mispari (Integral Reduced)
- Mispar Haakhor (Achoring Value)
- Mispar Hamerubah Haklali (General Square Value)
- Mispar Hapanim (Face Value)

### Greek Methods Removed:
- Greek Reduced (Arithmos Mikros)
- Greek Integral Reduced (Arithmos Mikros Olistikos)
- Greek Large (Arithmos Megalos)
- Greek Individual Squared (Arithmos Atomikos)

### Files Updated:
- `gematria/models/calculation_type.py`: Removed enum values
- `gematria/services/gematria_service.py`: Removed calculation methods
- `gematria/ui/widgets/word_abacus_widget.py`: Updated UI categories
- `gematria/ui/dialogs/gematria_help_dialog.py`: Removed help text
- `gematria/ui/dialogs/custom_cipher_dialog.py`: Removed references to methods
- `document_manager/ui/panels/document_analysis_panel.py`: Removed references

### New Script:
- Created `scripts/purge_calculation_methods.py` to remove calculations using deprecated methods from the database.

### Rationale:
This cleanup reduces redundant and rarely-used methods to simplify the interface and calculation operations. Most of these methods were duplicative of other methods or not historically significant in gematria practice. 