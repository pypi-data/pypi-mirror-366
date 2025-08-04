## StereoChemDecoder
A Python package to detect chiral centers and E/Z double bonds in SMILES strings using RDKit.


### Installation
Install the package using pip (RDKit must be installed separately):
```bash
pip install StereoChemDecoder
```

### Usage
```python
from StereoChemDecoder import StereoChemDecoder

# Initialize the decoder
decoder = StereoChemDecoder()

# Detect chiral centers
chiral_centers = decoder.detect_chirality("CC(C(=O)O)O")  # Lactic Acid
print(f"Chiral Centers: {chiral_centers}")  # e.g., [(2, '?')]

# Detect E/Z double bonds
ez_bonds = decoder.detect_ez("C/C=C/C") # Trans-2-Butene
print(f"E/Z Double Bonds: {ez_bonds}")  # e.g., [(1, 1, 2)]
```

### Requirements

- Python 3.7+
- RDKit (>=2023.3.1)

License
MIT License (see LICENSE file).
