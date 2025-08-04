from rdkit import Chem

class StereoChemDecoder:
    """A class to detect chiral centers and E/Z double bonds in SMILES strings."""
    
    def __init__(self, smiles_string=None):
        """Initialize the decoder, optionally with a SMILES string.
        
        Args:
            smiles_string (str, optional): The SMILES string to decode. Defaults to None.
        """
        self.smiles_string = smiles_string
        self.mol = self._initialize_molecule(smiles_string) if smiles_string else None

    def _initialize_molecule(self, smiles):
        """Initialize the RDKit molecule for a SMILES string.
        
        Args:
            smiles (str): The SMILES string to parse.
            
        Returns:
            Chem.Mol: RDKit molecule object, or None if invalid.
            
        Raises:
            ValueError: If the SMILES string is empty or None.
        """
        if not smiles:
            raise ValueError("SMILES string must be provided")
        try:
            mol = Chem.MolFromSmiles(smiles, sanitize=True)
            if mol is None:
                print(f"Error: Invalid SMILES string {smiles}")
                return None
            Chem.AssignStereochemistry(mol, force=True, cleanIt=True)
            return mol
        except Exception as e:
            print(f"Error processing SMILES {smiles}: {e}")
            return None

    def detect_chirality(self, smiles_string=None):
        """Detect potential chiral centers in a SMILES string.
        
        Args:
            smiles_string (str, optional): The SMILES string to decode. If None, uses initialized SMILES.
            
        Returns:
            list: List of (atom_idx, '?') for chiral centers, or None if invalid.
            
        Raises:
            ValueError: If no SMILES string is provided and none was initialized.
        """
        if smiles_string:
            self.smiles_string = smiles_string
            self.mol = self._initialize_molecule(smiles_string)
        elif not self.smiles_string or not self.mol:
            raise ValueError("No SMILES string provided or initialized")

        if self.mol is None:
            return None

        chiral_centers = []
        for atom in self.mol.GetAtoms():
            if atom.GetSymbol() != 'C':
                continue
            if atom.GetTotalDegree() != 4:
                continue
            neighbors = atom.GetNeighbors()
            if len(neighbors) > 4:
                continue
            substituents = []
            for nbr in neighbors:
                bond = self.mol.GetBondBetweenAtoms(atom.GetIdx(), nbr.GetIdx())
                bond_type = bond.GetBondTypeAsDouble()
                nbr_neighbors = sorted([n.GetSymbol() for n in nbr.GetNeighbors() if n.GetIdx() != atom.GetIdx()])
                substituent = (nbr.GetSymbol(), tuple(nbr_neighbors), bond_type)
                substituents.append(substituent)
            num_hydrogens = atom.GetTotalNumHs(includeNeighbors=False)
            for _ in range(num_hydrogens):
                substituents.append(('H', (), 1.0))
            if len(substituents) != 4:
                continue
            if len(set(substituents)) == 4:
                chiral_centers.append((atom.GetIdx(), '?'))

        return chiral_centers

    def detect_ez(self, smiles_string=None):
        """Detect potential E/Z double bonds in a SMILES string.
        
        Args:
            smiles_string (str, optional): The SMILES string to decode. If None, uses initialized SMILES.
            
        Returns:
            list: List of (bond_idx, begin_atom_idx, end_atom_idx) for E/Z double bonds, or None if invalid.
            
        Raises:
            ValueError: If no SMILES string is provided and none was initialized.
        """
        if smiles_string:
            self.smiles_string = smiles_string
            self.mol = self._initialize_molecule(smiles_string)
        elif not self.smiles_string or not self.mol:
            raise ValueError("No SMILES string provided or initialized")

        if self.mol is None:
            return None

        potential_ez = []
        for bond in self.mol.GetBonds():
            if bond.GetBondType() == Chem.rdchem.BondType.DOUBLE and not bond.IsInRing():
                begin_atom = bond.GetBeginAtom()
                end_atom = bond.GetEndAtom()
                begin_neighbors = []
                end_neighbors = []
                for nbr in begin_atom.GetNeighbors():
                    if nbr.GetIdx() != end_atom.GetIdx():
                        begin_neighbors.append(nbr.GetSymbol())
                begin_neighbors += ["H"] * begin_atom.GetTotalNumHs(includeNeighbors=False)
                for nbr in end_atom.GetNeighbors():
                    if nbr.GetIdx() != begin_atom.GetIdx():
                        end_neighbors.append(nbr.GetSymbol())
                end_neighbors += ["H"] * end_atom.GetTotalNumHs(includeNeighbors=False)
                if len(begin_neighbors) >= 1 and len(end_neighbors) >= 1:
                    if len(set(begin_neighbors)) > 1 or len(set(end_neighbors)) > 1:
                        potential_ez.append((bond.GetIdx(), begin_atom.GetIdx(), end_atom.GetIdx()))

        return potential_ez
