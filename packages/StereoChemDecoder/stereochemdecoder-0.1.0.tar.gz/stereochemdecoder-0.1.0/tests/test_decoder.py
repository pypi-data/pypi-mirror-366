import statistics
from StereoChemDecoder import StereoChemDecoder

def main():
    smiles_list = [
        "C1CCC=CC1", "CC(C)=C(C)C", "C/C=C/C", "CC=CC", "CC(C)(F)Cl", "CC(C)Br",
        "CC(C(=O)O)O", "CC(C(C)Br)Cl", "C1CCCCC1", "CC(=O)O", "C#C", "CCO",
        "CC(=O)C", "c1ccccc1", "CC(C)(C)O", "C/C=C\\C", "CC(C)C(=O)O",
        "CC(Cl)C(F)Cl", "CC(N)C", "C1CCOC1", "CC#CC", "CC(C)(C)Cl", "CC(=O)OC",
        "c1ccncc1", "CC(C)CO", "C/C=C/C=C/C", "CC(F)(Cl)Br", "CC(C)[NH2]",
        "C1CCSC1", "CC(C)=O", "CC(C)(O)C", "C/C=C\\C=C/C", "CC(C)CBr",
        "CC(O)C(=O)O", "C1CCNCC1", "CC(C)C(=O)C", "CC(Br)C(Cl)F", "CC(=O)CC",
        "c1ccoc1", "CC(C)(C)[NH2]", "C/C=C/C(=O)O", "CC(O)C(O)C", "CC(C)=CC",
        "CC(F)C(O)C", "C1CCCCC1[OH]", "CC(C)C(=O)OC", "CC(Cl)C(=O)O",
        "c1ccccc1[OH]", "CC(C)(C)C(=O)O", "CC([NH2])C(O)C",
        "CC(C)C", "CC(=O)Cl", "C1CCOCC1", "CC(C)O", "C/C=C/C=C\\C", "CC(F)Cl",
        "CC(C)Cl", "CC(O)C", "c1ccsc1", "CC(=O)[NH2]", "C1CCCC1", "CC#C",
        "CC(C)(C)F", "CC(O)CC", "C/C=C\\C(=O)O", "CC(C)(O)Cl", "CC([NH2])CC",
        "C1CCSCC1", "CC(C)C=O", "CC(O)C(O)O", "c1ccncc1C", "CC(C)C[NH2]",
        "C/C=C/C=C\\C", "CC(F)(F)F", "CC(Cl)C(O)C", "C1CCCCC1[NH2]", "CC(C)C(=O)[NH2]",
        "CC(Br)C(F)Cl", "CC(=O)CC=O", "c1cocc1", "CC(C)(C)Br", "C/C=C/C(O)C",
        "CC(O)C([NH2])C", "CC(C)=C", "CC(F)C(=O)O", "C1CCCCC1F", "CC(C)C(=O)Cl",
        "CC(Cl)C(O)O", "c1ccccc1[NH2]", "CC(C)(C)C(=O)[NH2]", "CC([NH2])C(O)O",
        "CC(C)=C(C)O", "CC(F)C([NH2])C", "C1CCCCC1Cl", "CC(C)C(=O)CC",
        "CC(Br)C(=O)O", "c1ccccc1F", "CC(C)(C)C(O)C", "CC([NH2])C(=O)O",
        "CC(C)=C(O)C",
        "CCC(=O)O", "C1CCCCCC1", "CC(C)(C)[OH]", "C/C=C\\C(=O)C", "CC(F)C(Cl)C",
        "CC([NH2])C(=O)C", "c1ccccc1Cl", "C1CCNCC1[OH]", "CC(C)C(=O)[OH]",
        "C/C=C/C[NH2]", "CC(=O)CC(O)C", "C1CCOCC1F", "CC(C)(Br)Cl",
        "CC(O)C(F)C", "c1ccncc1[OH]", "CC(C)C[OH]", "C/C=C/C=C\\C(=O)O",
        "CC(F)C([NH2])C(O)C", "C1CCCCC1Br", "CC(C)C(=O)[NH2]", "CC(Cl)C(=O)C",
        "c1ccccc1[OH]", "CC(C)(C)C(=O)CC", "CC([NH2])C(O)C(=O)O",
        "CC(C)=C(C)[NH2]", "CC(F)C(Cl)[OH]", "C1CCCCC1[NH2]", "CC(C)C(=O)OCC",
        "CC(Br)C(O)O", "c1ccccc1Br", "CC(C)(C)C(O)CC", "CC([NH2])C(=O)[OH]",
        "CC(C)=C(O)CC", "CC(F)C([NH2])[OH]", "C1CCCCC1[OH]", "CC(C)C(=O)CC=O",
        "CC(Cl)C(O)C(=O)O", "c1ccccc1[NH2]", "CC(C)(C)C(=O)OCC",
        "CC([NH2])C(O)C(O)C", "CC(C)=C(C)C(=O)O", "CC(F)C(Cl)C(=O)O",
        "C1CCCCC1C(=O)O", "CC(C)C(=O)CC(O)C", "CC(Br)C(O)C(=O)C",
        "c1ccccc1C(=O)O", "CC(C)(C)C(O)C(=O)O", "CC([NH2])C(O)C(=O)[OH]",
        "CC(C)=C(O)C(=O)O", "CC(F)C([NH2])C(O)C", "C1CCCCC1C(=O)[OH]",
        "CC(C)C(=O)CC[NH2]", "CC(Cl)C(O)C(=O)[OH]", "c1ccccc1C(=O)[NH2]",
        "CC(C)(C)C(O)C(=O)C", "CC([NH2])C(O)C(=O)C", "CC(C)=C(C)C(O)C",
        "CC(F)C(Cl)C(O)C", "C1CCCCC1C(=O)C", "CC(C)C(=O)CC(O)[OH]",
        "CC(Br)C(O)C(O)C", "c1ccccc1C(=O)OC", "CC(C)(C)C(O)C(O)C",
        "CC([NH2])C(O)C(O)[OH]", "CC(C)=C(C)C(O)[OH]", "CC(F)C(Cl)C(O)[OH]",
        "C1CCCCC1C(=O)CC", "CC(C)C(=O)CC(O)C(=O)O", "CC(Br)C(O)C(O)[OH]",
        "c1ccccc1C(=O)OCC", "CC(C)(C)C(O)C(O)[OH]", "CC([NH2])C(O)C(O)C(=O)O",
        "CC(C)=C(C)C(O)C(=O)O", "CC(F)C(Cl)C(O)C(=O)O", "C1CCCCC1C(=O)OCC",
        "CC(C)C(=O)CC(O)C(O)C", "CC(Br)C(O)C(O)C(=O)O", "c1ccccc1C(=O)OCC(O)C",
        "CC(C)(C)C(O)C(O)C(O)C", "CC([NH2])C(O)C(O)C(O)C", "CC(C)=C(C)C(O)C(O)C",
        "CC(F)C(Cl)C(O)C(O)C", "C1CCCCC1C(=O)CC(O)C", "CC(C)C(=O)CC(O)C(O)[OH]",
        "CC(Br)C(O)C(O)C(O)[OH]", "c1ccccc1C(=O)OCC(O)[OH]", "CC(C)(C)C(O)C(O)C(O)[OH]",
        "CC([NH2])C(O)C(O)C(O)[OH]", "CC(C)=C(C)C(O)C(O)C(=O)O", "CC(F)C(Cl)C(O)C(O)C(=O)O",
        "C1CCCCC1C(=O)CC(O)C(=O)O", "CCCC", "CC(F)C", "CC(Cl)C", "CC(Br)C", "CC([OH])C",
        "CC([NH2])C", "CCC(F)C", "CCC(Cl)C", "CCC(Br)C", "CCC([OH])C", "CCC([NH2])C",
        "CCCC(F)", "CCCC(Cl)", "CCCC(Br)", "CCCC[OH]", "CCCC[NH2]",
        "CC(F)C(F)C", "CC(Cl)C(Cl)C", "CC(Br)C(Br)C", "CC([OH])C([OH])C",
        "CC([NH2])C([NH2])C", "C/C=C/CC", "C/C=C\\CC", "C/C=C/C(F)C",
        "C/C=C\\C(Cl)C", "C/C=C/C(Br)C", "C/C=C/C([OH])C", "C/C=C/C([NH2])C",
        "CCCC(=O)O", "CC(F)C(=O)O", "CC(Cl)C(=O)O", "CC(Br)C(=O)O",
        "CC([OH])C(=O)O", "CC([NH2])C(=O)O", "CCC(F)C(=O)O", "CCC(Cl)C(=O)O",
        "CCC(Br)C(=O)O", "CCC([OH])C(=O)O", "CCC([NH2])C(=O)O", "CCCC(=O)[OH]",
        "CCCC(=O)[NH2]", "C1CCCC1[OH]", "C1CCCC1[NH2]", "C1CCCC1F", "C1CCCC1Cl",
        "C1CCCC1Br", "c1ccccc1C", "c1ccccc1C(F)", "c1ccccc1C(Cl)", "c1ccccc1C(Br)",
        "c1ccccc1C[OH]", "c1ccccc1C[NH2]", "C1CCNCC1C", "C1CCNCC1F", "C1CCNCC1Cl",
        "C1CCNCC1Br", "C1CCNCC1[OH]", "C1CCNCC1[NH2]", "C1CCOCC1C", "C1CCOCC1[OH]",
        "C1CCOCC1[NH2]", "c1ccncc1F", "c1ccncc1Cl", "c1ccncc1Br", "c1ccncc1[OH]",
        "c1ccncc1[NH2]", "C/C=C/C=C/C(=O)O", "C/C=C\\C=C/C(=O)O", "C/C=C/C=C\\C(=O)[OH]",
        "CC(F)C(Cl)C(=O)[OH]", "CC(Br)C([NH2])C(=O)O", "CC([OH])C(F)C(=O)O",
        "C1CCCCCC1F", "C1CCCCCC1Cl", "C1CCCCCC1Br", "C1CCCCCC1[OH]", "C1CCCCCC1[NH2]",
        "CC(C)(C)C(=O)C", "CC(C)(C)C(=O)[OH]", "CC(C)(C)C(=O)[NH2]", "CC(C)C(F)C",
        "CC(C)C(Cl)C", "CC(C)C(Br)C", "CC(C)C([OH])C", "CC(C)C([NH2])C",
        "C/C=C/C(F)C(=O)O", "C/C=C\\C(Cl)C(=O)O", "C/C=C/C(Br)C(=O)O",
        "C/C=C/C([OH])C(=O)O", "C/C=C/C([NH2])C(=O)O", "c1ccsc1F", "c1ccsc1Cl",
        "c1ccsc1Br", "c1ccsc1[OH]", "c1ccsc1[NH2]", "C1CCSCC1F", "C1CCSCC1Cl",
        "C1CCSCC1Br", "C1CCSCC1[OH]", "C1CCSCC1[NH2]", "CC(F)C(O)C(O)C",
        "CC(Cl)C(O)C(O)C", "CC(Br)C(O)C(O)C", "CC([NH2])C(O)C(O)C",
        "C/C=C/C(O)C(O)C", "C/C=C\\C(O)C(O)C", "C1CCCCC1C(F)C", "C1CCCCC1C(Cl)C",
        "C1CCCCC1C(Br)C", "C1CCCCC1C([OH])C", "C1CCCCC1C([NH2])C", "c1ccccc1C(=O)C",
        "c1ccccc1C(=O)CC", "c1ccccc1C(=O)[OH]", "c1ccccc1C(=O)[NH2]", "CC(C)C(=O)OCC(O)C",
        "CC(F)C(=O)OCC(O)C", "CC(Cl)C(=O)OCC(O)C", "CC(Br)C(=O)OCC(O)C",
        "CC([NH2])C(=O)OCC(O)C", "C/C=C/C(=O)OCC", "C/C=C\\C(=O)OCC",
        "C1CCCCC1C(=O)OCC(O)C", "C1CCCCC1C(=O)CC(O)[OH]", "C1CCNCC1C(=O)O",
        "C1CCNCC1C(=O)[OH]", "C1CCNCC1C(=O)[NH2]", "c1ccncc1C(=O)O",
        "c1ccncc1C(=O)[OH]", "c1ccncc1C(=O)[NH2]", "CC(C)(F)C(O)C", "CC(C)(Cl)C(O)C",
        "CC(C)(Br)C(O)C", "CC(C)([NH2])C(O)C", "C/C=C/C(F)C(O)C", "C/C=C\\C(Cl)C(O)C",
        "C1CCCC1C(O)C", "C1CCCC1C(F)C", "C1CCCC1C(Cl)C", "C1CCCC1C(Br)C",
        "C1CCCC1C([NH2])C", "c1ccccc1C(F)C(O)C", "c1ccccc1C(Cl)C(O)C",
        "c1ccccc1C(Br)C(O)C", "c1ccccc1C([OH])C(O)C", "c1ccccc1C([NH2])C(O)C",
        "CC(F)C(O)C(=O)[OH]", "CC(Cl)C(O)C(=O)[OH]", "CC(Br)C(O)C(=O)[OH]",
        "CC([NH2])C(O)C(=O)[OH]", "C/C=C/C(O)C(=O)[OH]", "C/C=C\\C(O)C(=O)[OH]",
        "C1CCCCC1C(O)C(=O)O", "C1CCCCC1C(F)C(=O)O", "C1CCCCC1C(Cl)C(=O)O",
        "C1CCCCC1C(Br)C(=O)O", "C1CCCCC1C([NH2])C(=O)O", "c1ccccc1C(O)C(=O)O",
        "c1ccccc1C(F)C(=O)O", "c1ccccc1C(Cl)C(=O)O", "c1ccccc1C(Br)C(=O)O",
        "c1ccccc1C([NH2])C(=O)O", "CC(C)C(O)C(O)[OH]", "CC(F)C(O)C(O)[OH]",
        "CC(Cl)C(O)C(O)[OH]", "CC(Br)C(O)C(O)[OH]", "CC([NH2])C(O)C(O)[OH]",
        "C/C=C/C(O)C(O)[OH]", "C/C=C\\C(O)C(O)[OH]", "C1CCCCC1C(O)C(O)[OH]",
        "C1CCCCC1C(F)C(O)[OH]", "C1CCCCC1C(Cl)C(O)[OH]", "C1CCCCC1C(Br)C(O)[OH]",
        "C1CCCCC1C([NH2])C(O)[OH]", "c1ccccc1C(O)C(O)[OH]", "c1ccccc1C(F)C(O)[OH]",
        "c1ccccc1C(Cl)C(O)[OH]", "c1ccccc1C(Br)C(O)[OH]", "c1ccccc1C([NH2])C(O)[OH]",
        "CC(C)C(O)C(O)C(=O)O", "CC(F)C(O)C(O)C(=O)O", "CC(Cl)C(O)C(O)C(=O)O",
        "CC(Br)C(O)C(O)C(=O)O", "CC([NH2])C(O)C(O)C(=O)O", "C/C=C/C(O)C(O)C(=O)O",
        "C/C=C\\C(O)C(O)C(=O)O", "C1CCCCC1C(O)C(O)C(=O)O", "C1CCCCC1C(F)C(O)C(=O)O",
        "C1CCCCC1C(Cl)C(O)C(=O)O", "C1CCCCC1C(Br)C(O)C(=O)O", "C1CCCCC1C([NH2])C(O)C(=O)O",
        "c1ccccc1C(O)C(O)C(=O)O", "c1ccccc1C(F)C(O)C(=O)O", "c1ccccc1C(Cl)C(O)C(=O)O",
        "c1ccccc1C(Br)C(O)C(=O)O", "c1ccccc1C([NH2])C(O)C(=O)O", "CC(C)C(O)C(O)C(O)C",
        "CC(F)C(O)C(O)C(O)C", "CC(Cl)C(O)C(O)C(O)C", "CC(Br)C(O)C(O)C(O)C",
        "CC([NH2])C(O)C(O)C(O)C", "C/C=C/C(O)C(O)C(O)C", "C/C=C\\C(O)C(O)C(O)C",
        "C1CCCCC1C(O)C(O)C(O)C", "C1CCCCC1C(F)C(O)C(O)C", "C1CCCCC1C(Cl)C(O)C(O)C",
        "C1CCCCC1C(Br)C(O)C(O)C", "C1CCCCC1C([NH2])C(O)C(O)C", "c1ccccc1C(O)C(O)C(O)C",
        "c1ccccc1C(F)C(O)C(O)C", "c1ccccc1C(Cl)C(O)C(O)C", "c1ccccc1C(Br)C(O)C(O)C",
        "c1ccccc1C([NH2])C(O)C(O)C", "CC(C)C(=O)OCC(O)[OH]", "CC(F)C(=O)OCC(O)[OH]",
        "CC(Cl)C(=O)OCC(O)[OH]", "CC(Br)C(=O)OCC(O)[OH]", "CC([NH2])C(=O)OCC(O)[OH]",
        "C/C=C/C(=O)OCC(O)[OH]", "C/C=C\\C(=O)OCC(O)[OH]", "C1CCCCC1C(=O)OCC(O)[OH]",
        "C1CCCCC1C(F)C(=O)OCC", "C1CCCCC1C(Cl)C(=O)OCC", "C1CCCCC1C(Br)C(=O)OCC",
        "C1CCCCC1C([NH2])C(=O)OCC", "c1ccccc1C(=O)OCC(O)[OH]", "c1ccccc1C(F)C(=O)OCC",
        "c1ccccc1C(Cl)C(=O)OCC", "c1ccccc1C(Br)C(=O)OCC", "c1ccccc1C([NH2])C(=O)OCC",
        "CC(C)C(=O)CC(O)C(O)[OH]", "CC(F)C(=O)CC(O)C(O)[OH]", "CC(Cl)C(=O)CC(O)C(O)[OH]",
        "CC(Br)C(=O)CC(O)C(O)[OH]", "CC([NH2])C(=O)CC(O)C(O)[OH]", "C/C=C/C(=O)CC(O)C(O)[OH]",
        "C/C=C\\C(=O)CC(O)C(O)[OH]", "C1CCCCC1C(=O)CC(O)C(O)[OH]", "C1CCCCC1C(F)C(=O)CC(O)[OH]",
        "C1CCCCC1C(Cl)C(=O)CC(O)[OH]", "C1CCCCC1C(Br)C(=O)CC(O)[OH]", "C1CCCCC1C([NH2])C(=O)CC(O)[OH]",
        "c1ccccc1C(=O)CC(O)C(O)[OH]", "c1ccccc1C(F)C(=O)CC(O)[OH]", "c1ccccc1C(Cl)C(=O)CC(O)[OH]",
        "c1ccccc1C(Br)C(=O)CC(O)[OH]", "c1ccccc1C([NH2])C(=O)CC(O)[OH]", "CC(C)C(=O)CC(O)C(O)C(=O)O",
        "CC(F)C(=O)CC(O)C(O)C(=O)O", "CC(Cl)C(=O)CC(O)C(O)C(=O)O", "CC(Br)C(=O)CC(O)C(O)C(=O)O",
        "CC([NH2])C(=O)CC(O)C(O)C(=O)O", "C/C=C/C(=O)CC(O)C(O)C(=O)O", "C/C=C\\C(=O)CC(O)C(O)C(=O)O",
        "C1CCCCC1C(=O)CC(O)C(O)C(=O)O", "C1CCCCC1C(F)C(=O)CC(O)C(=O)O", "C1CCCCC1C(Cl)C(=O)CC(O)C(=O)O",
        "C1CCCCC1C(Br)C(=O)CC(O)C(=O)O", "C1CCCCC1C([NH2])C(=O)CC(O)C(=O)O",
        "c1ccccc1C(=O)CC(O)C(O)C(=O)O", "c1ccccc1C(F)C(=O)CC(O)C(=O)O",
        "c1ccccc1C(Cl)C(=O)CC(O)C(=O)O", "c1ccccc1C(Br)C(=O)CC(O)C(=O)O",
        "c1ccccc1C([NH2])C(=O)CC(O)C(=O)O", "CC(C)C(=O)CC(O)C(O)C(O)C",
        "CC(F)C(=O)CC(O)C(O)C(O)C", "CC(Cl)C(=O)CC(O)C(O)C(O)C", "CC(Br)C(=O)CC(O)C(O)C(O)C",
        "CC([NH2])C(=O)CC(O)C(O)C(O)C", "C/C=C/C(=O)CC(O)C(O)C(O)C",
        "C/C=C\\C(=O)CC(O)C(O)C(O)C", "C1CCCCC1C(=O)CC(O)C(O)C(O)C",
        "C1CCCCC1C(F)C(=O)CC(O)C(O)C", "C1CCCCC1C(Cl)C(=O)CC(O)C(O)C",
        "C1CCCCC1C(Br)C(=O)CC(O)C(O)C", "C1CCCCC1C([NH2])C(=O)CC(O)C(O)C",
        "c1ccccc1C(=O)CC(O)C(O)C(O)C", "c1ccccc1C(F)C(=O)CC(O)C(O)C",
        "c1ccccc1C(Cl)C(=O)CC(O)C(O)C", "c1ccccc1C(Br)C(=O)CC(O)C(O)C",
        "c1ccccc1C([NH2])C(=O)CC(O)C(O)C", "CC(C)C(=O)CC(O)C(O)C(O)[OH]",
        "CC(F)C(=O)CC(O)C(O)C(O)[OH]", "CC(Cl)C(=O)CC(O)C(O)C(O)[OH]",
        "CC(Br)C(=O)CC(O)C(O)C(O)[OH]", "CC([NH2])C(=O)CC(O)C(O)C(O)[OH]",
        "C/C=C/C(=O)CC(O)C(O)C(O)[OH]", "C/C=C\\C(=O)CC(O)C(O)C(O)[OH]",
        "C1CCCCC1C(=O)CC(O)C(O)C(O)[OH]", "C1CCCCC1C(F)C(=O)CC(O)C(O)[OH]",
        "C1CCCCC1C(Cl)C(=O)CC(O)C(O)[OH]", "C1CCCCC1C(Br)C(=O)CC(O)C(O)[OH]",
        "C1CCCCC1C([NH2])C(=O)CC(O)C(O)[OH]", "c1ccccc1C(=O)CC(O)C(O)C(O)[OH]",
        "c1ccccc1C(F)C(=O)CC(O)C(O)[OH]", "c1ccccc1C(Cl)C(=O)CC(O)C(O)[OH]",
        "c1ccccc1C(Br)C(=O)CC(O)C(O)[OH]", "c1ccccc1C([NH2])C(=O)CC(O)C(O)[OH]",
        "CC(C)C(=O)CC(O)C(O)C(O)C(=O)O", "CC(F)C(=O)CC(O)C(O)C(O)C(=O)O",
        "CC(Cl)C(=O)CC(O)C(O)C(O)C(=O)O", "CC(Br)C(=O)CC(O)C(O)C(O)C(=O)O",
        "CC([NH2])C(=O)CC(O)C(O)C(O)C(=O)O", "C/C=C/C(=O)CC(O)C(O)C(O)C(=O)O",
        "C/C=C\\C(=O)CC(O)C(O)C(O)C(=O)O", "C1CCCCC1C(=O)CC(O)C(O)C(O)C(=O)O",
        "C1CCCCC1C(F)C(=O)CC(O)C(O)C(=O)O", "C1CCCCC1C(Cl)C(=O)CC(O)C(O)C(=O)O",
        "C1CCCCC1C(Br)C(=O)CC(O)C(O)C(=O)O", "C1CCCCC1C([NH2])C(=O)CC(O)C(O)C(=O)O",
        "c1ccccc1C(=O)CC(O)C(O)C(O)C(=O)O", "c1ccccc1C(F)C(=O)CC(O)C(O)C(=O)O",
        "c1ccccc1C(Cl)C(=O)CC(O)C(O)C(=O)O", "c1ccccc1C(Br)C(=O)CC(O)C(O)C(=O)O",
        "c1ccccc1C([NH2])C(=O)CC(O)C(O)C(=O)O", "CC(C)C(=O)CC(O)C(O)C(O)C(O)C",
        "CC(F)C(=O)CC(O)C(O)C(O)C(O)C", "CC(Cl)C(=O)CC(O)C(O)C(O)C(O)C",
        "CC(Br)C(=O)CC(O)C(O)C(O)C(O)C", "CC([NH2])C(=O)CC(O)C(O)C(O)C(O)C",
        "C/C=C/C(=O)CC(O)C(O)C(O)C(O)C", "C/C=C\\C(=O)CC(O)C(O)C(O)C(O)C",
        "C1CCCCC1C(=O)CC(O)C(O)C(O)C(O)C", "C1CCCCC1C(F)C(=O)CC(O)C(O)C(O)C",
        "C1CCCCC1C(Cl)C(=O)CC(O)C(O)C(O)C", "C1CCCCC1C(Br)C(=O)CC(O)C(O)C(O)C",
        "C1CCCCC1C([NH2])C(=O)CC(O)C(O)C(O)C", "c1ccccc1C(=O)CC(O)C(O)C(O)C(O)C",
        "c1ccccc1C(F)C(=O)CC(O)C(O)C(O)C", "c1ccccc1C(Cl)C(=O)CC(O)C(O)C(O)C",
        "c1ccccc1C(Br)C(=O)CC(O)C(O)C(O)C", "c1ccccc1C([NH2])C(=O)CC(O)C(O)C(O)C",
        "CC(C)C(=O)CC(O)C(O)C(O)C(O)[OH]", "CC(F)C(=O)CC(O)C(O)C(O)C(O)[OH]",
        "CC(Cl)C(=O)CC(O)C(O)C(O)C(O)[OH]", "CC(Br)C(=O)CC(O)C(O)C(O)C(O)[OH]",
        "CC([NH2])C(=O)CC(O)C(O)C(O)C(O)[OH]", "C/C=C/C(=O)CC(O)C(O)C(O)C(O)[OH]",
        "C/C=C\\C(=O)CC(O)C(O)C(O)C(O)[OH]", "C1CCCCC1C(=O)CC(O)C(O)C(O)C(O)[OH]",
        "C1CCCCC1C(F)C(=O)CC(O)C(O)C(O)[OH]", "C1CCCCC1C(Cl)C(=O)CC(O)C(O)C(O)[OH]",
        "C1CCCCC1C(Br)C(=O)CC(O)C(O)C(O)[OH]", "C1CCCCC1C([NH2])C(=O)CC(O)C(O)C(O)[OH]",
        "c1ccccc1C(=O)CC(O)C(O)C(O)C(O)[OH]", "c1ccccc1C(F)C(=O)CC(O)C(O)C(O)[OH]",
        "c1ccccc1C(Cl)C(=O)CC(O)C(O)C(O)[OH]", "c1ccccc1C(Br)C(=O)CC(O)C(O)C(O)[OH]",
        "c1ccccc1C([NH2])C(=O)CC(O)C(O)C(O)[OH]", "CC(C)C(=O)CC(O)C(O)C(O)C(O)C(=O)O",
        "CC(F)C(=O)CC(O)C(O)C(O)C(O)C(=O)O", "CC(Cl)C(=O)CC(O)C(O)C(O)C(O)C(=O)O",
        "CC(Br)C(=O)CC(O)C(O)C(O)C(O)C(=O)O", "CC([NH2])C(=O)CC(O)C(O)C(O)C(O)C(=O)O",
        "C/C=C/C(=O)CC(O)C(O)C(O)C(O)C(=O)O", "C/C=C\\C(=O)CC(O)C(O)C(O)C(O)C(=O)O",
        "C1CCCCC1C(=O)CC(O)C(O)C(O)C(O)C(=O)O", "C1CCCCC1C(F)C(=O)CC(O)C(O)C(O)C(=O)O",
        "C1CCCCC1C(Cl)C(=O)CC(O)C(O)C(O)C(=O)O", "C1CCCCC1C(Br)C(=O)CC(O)C(O)C(O)C(=O)O",
        "C1CCCCC1C([NH2])C(=O)CC(O)C(O)C(O)C(=O)O", "c1ccccc1C(=O)CC(O)C(O)C(O)C(O)C(=O)O",
        "c1ccccc1C(F)C(=O)CC(O)C(O)C(O)C(=O)O", "c1ccccc1C(Cl)C(=O)CC(O)C(O)C(O)C(=O)O",
        "c1ccccc1C(Br)C(=O)CC(O)C(O)C(O)C(=O)O", "c1ccccc1C([NH2])C(=O)CC(O)C(O)C(O)C(=O)O",
        "CC(C)C(=O)CC(O)C(O)C(O)C(O)C(O)C", "CC(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C",
        "CC(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C", "CC(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C",
        "CC([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C", "C/C=C/C(=O)CC(O)C(O)C(O)C(O)C(O)C",
        "C/C=C\\C(=O)CC(O)C(O)C(O)C(O)C(O)C", "C1CCCCC1C(=O)CC(O)C(O)C(O)C(O)C(O)C",
        "C1CCCCC1C(F)C(=O)CC(O)C(O)C(O)C(O)C", "C1CCCCC1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C",
        "C1CCCCC1C(Br)C(=O)CC(O)C(O)C(O)C(O)C", "C1CCCCC1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C",
        "c1ccccc1C(=O)CC(O)C(O)C(O)C(O)C(O)C", "c1ccccc1C(F)C(=O)CC(O)C(O)C(O)C(O)C",
        "c1ccccc1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C", "c1ccccc1C(Br)C(=O)CC(O)C(O)C(O)C(O)C",
        "c1ccccc1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C", "CC(C)C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]",
        "CC(F)C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]", "CC(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]",
        "CC(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]", "CC([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]",
        "C/C=C/C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]", "C/C=C\\C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]",
        "C1CCCCC1C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]", "C1CCCCC1C(F)C(=O)CC(O)C(O)C(O)C(O)[OH]",
        "C1CCCCC1C(Cl)C(=O)CC(O)C(O)C(O)C(O)[OH]", "C1CCCCC1C(Br)C(=O)CC(O)C(O)C(O)C(O)[OH]",
        "C1CCCCC1C([NH2])C(=O)CC(O)C(O)C(O)C(O)[OH]", "c1ccccc1C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]",
        "c1ccccc1C(F)C(=O)CC(O)C(O)C(O)C(O)[OH]", "c1ccccc1C(Cl)C(=O)CC(O)C(O)C(O)C(O)[OH]",
        "c1ccccc1C(Br)C(=O)CC(O)C(O)C(O)C(O)[OH]", "c1ccccc1C([NH2])C(=O)CC(O)C(O)C(O)C(O)[OH]",
        "CC(C)C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O", "CC(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O",
        "CC(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O", "CC(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O",
        "CC([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O", "C/C=C/C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O",
        "C/C=C\\C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O", "C1CCCCC1C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O",
        "C1CCCCC1C(F)C(=O)CC(O)C(O)C(O)C(O)C(=O)O", "C1CCCCC1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C(=O)O",
        "C1CCCCC1C(Br)C(=O)CC(O)C(O)C(O)C(O)C(=O)O", "C1CCCCC1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C(=O)O",
        "c1ccccc1C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O", "c1ccccc1C(F)C(=O)CC(O)C(O)C(O)C(O)C(=O)O",
        "c1ccccc1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C(=O)O", "c1ccccc1C(Br)C(=O)CC(O)C(O)C(O)C(O)C(=O)O",
        "c1ccccc1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C(=O)O", "CC(C)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C",
        "CC(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C", "CC(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C",
        "CC(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C", "CC([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C",
        "C/C=C/C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C", "C/C=C\\C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C",
        "C1CCCCC1C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C", "C1CCCCC1C(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C",
        "C1CCCCC1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C", "C1CCCCC1C(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C",
        "C1CCCCC1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C", "c1ccccc1C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C",
        "c1ccccc1C(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C", "c1ccccc1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C",
        "c1ccccc1C(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C", "c1ccccc1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C",
        "CC(C)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]", "CC(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "CC(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]", "CC(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "CC([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]", "C/C=C/C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "C/C=C\\C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]", "C1CCCCC1C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "C1CCCCC1C(F)C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]", "C1CCCCC1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]",
        "C1CCCCC1C(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]", "C1CCCCC1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]",
        "c1ccccc1C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]", "c1ccccc1C(F)C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]",
        "c1ccccc1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]", "c1ccccc1C(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]",
        "c1ccccc1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)[OH]", "CC(C)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(=O)O",
        "CC(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(=O)O", "CC(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(=O)O",
        "CC(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(=O)O", "CC([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(=O)O",
        "C/C=C/C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(=O)O", "C/C=C\\C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(=O)O",
        "C1CCCCC1C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(=O)O", "C1CCCCC1C(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O",
        "C1CCCCC1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O", "C1CCCCC1C(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O",
        "C1CCCCC1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O",
        "c1ccccc1C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(=O)O", "c1ccccc1C(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O",
        "c1ccccc1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O", "c1ccccc1C(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O",
        "c1ccccc1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C(=O)O", "CC(C)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)C",
        "CC(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)C", "CC(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)C",
        "CC(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)C", "CC([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)C",
        "C/C=C/C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)C", "C/C=C\\C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)C",
        "C1CCCCC1C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)C", "C1CCCCC1C(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C",
        "C1CCCCC1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C", "C1CCCCC1C(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C",
        "C1CCCCC1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C",
        "c1ccccc1C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)C", "c1ccccc1C(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C",
        "c1ccccc1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C", "c1ccccc1C(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C",
        "c1ccccc1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C", "CC(C)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "CC(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)[OH]", "CC(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "CC(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "CC([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "C/C=C/C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "C/C=C\\C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "C1CCCCC1C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "C1CCCCC1C(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "C1CCCCC1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "C1CCCCC1C(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "C1CCCCC1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "c1ccccc1C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "c1ccccc1C(F)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "c1ccccc1C(Cl)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "c1ccccc1C(Br)C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]",
        "c1ccccc1C([NH2])C(=O)CC(O)C(O)C(O)C(O)C(O)C(O)[OH]"
    ]

    # Ensure unique SMILES (though all 17 are unique; [:1000] is redundant but preserved)
    smiles_list = list(dict.fromkeys(smiles_list))[:1000]

    # Collect data for statistical analysis
    chiral_counts = []
    ez_counts = []
    valid_molecules = 0
    results = []
    invalid_smiles = []

    decoder = StereoChemDecoder()
    for smiles in smiles_list:
        try:
            chiral_centers = decoder.detect_chirality(smiles)
            potential_ez = decoder.detect_ez(smiles)
            # Use 'or' condition as per previous code
            if chiral_centers is not None or potential_ez is not None:
                valid_molecules += 1
                chiral_count = len(chiral_centers) if chiral_centers is not None else 0
                ez_count = len(potential_ez) if potential_ez is not None else 0
                chiral_counts.append(chiral_count)
                ez_counts.append(ez_count)
                results.append((smiles, chiral_count, ez_count))
            else:
                invalid_smiles.append(smiles)
        except ValueError as e:
            print(e)
            invalid_smiles.append(smiles)

    # Statistical analysis
    print("\nStatistical Analysis of Stereochemistry for", valid_molecules, "Molecules:")
    print("--------------------------------------------------")
    print(f"Invalid SMILES strings: {len(invalid_smiles)}")
    if invalid_smiles:
        print("Examples of invalid SMILES:", invalid_smiles[:5])

    # Chiral centers statistics
    chiral_mean = statistics.mean(chiral_counts) if chiral_counts else 0
    chiral_std = statistics.stdev(chiral_counts) if len(chiral_counts) > 1 else 0
    chiral_min = min(chiral_counts) if chiral_counts else 0
    chiral_max = max(chiral_counts) if chiral_counts else 0
    chiral_nonzero = sum(1 for c in chiral_counts if c > 0)

    print("\nChiral Centers:")
    print(f"  Mean number of chiral centers: {chiral_mean:.2f}")
    print(f"  Standard deviation: {chiral_std:.2f}")
    print(f"  Range: {chiral_min} to {chiral_max}")
    print(f"  Molecules with at least one chiral center: {chiral_nonzero} ({chiral_nonzero/valid_molecules*100:.1f}%)")

    # E/Z double bonds statistics
    ez_mean = statistics.mean(ez_counts) if ez_counts else 0
    ez_std = statistics.stdev(ez_counts) if len(ez_counts) > 1 else 0
    ez_min = min(ez_counts) if ez_counts else 0
    ez_max = max(ez_counts) if ez_counts else 0
    ez_nonzero = sum(1 for e in ez_counts if e > 0)

    print("\nE/Z Double Bonds:")
    print(f"  Mean number of E/Z double bonds: {ez_mean:.2f}")
    print(f"  Standard deviation: {ez_std:.2f}")
    print(f"  Range: {ez_min} to {ez_max}")
    print(f"  Molecules with at least one E/Z double bond: {ez_nonzero} ({ez_nonzero/valid_molecules*100:.1f}%)")

    # Additional statistics
    both_chiral_and_ez = sum(1 for _, chiral_count, ez_count in results if chiral_count > 0 and ez_count > 0)
    no_chiral_no_ez = sum(1 for _, chiral_count, ez_count in results if chiral_count == 0 and ez_count == 0)

    print("\nAdditional Statistics:")
    print(f"  Molecules with both chiral centers and E/Z double bonds: {both_chiral_and_ez} ({both_chiral_and_ez/valid_molecules*100:.1f}%)")
    print(f"  Molecules with no chiral centers and no E/Z double bonds: {no_chiral_no_ez} ({no_chiral_no_ez/valid_molecules*100:.1f}%)")

    # Test specific SMILES strings
    test_smiles_list = [
        "CC(C(=O)O)O",              # Lactic acid
        "C[C@H](O)C(=O)O",         # Lactic acid (explicit chirality)
        "C/C=C/C",                  # (E)-But-2-ene
        "C/C=C\\F",                 # (E)-1-Fluoropropene
        "C/C=C/Cl",                 # (E)-1-Chloropropene
        "F/C=C/F",                  # (E)-1,2-Difluoroethene
        "CC(F)C(O)C(O)C(=O)O",     # 2,3-Dihydroxy-4-fluorobutanoic acid
        "c1ccncc1C(=O)[OH]",       # Nicotinic acid
        "CC(Cl)C(O)C(O)[OH]",      # 2,3-Dihydroxy-1-chloropropane
        "C1CCCCC1C(=O)OCC",        # Cyclohexylacetic acid ethyl ester
        "c1ccccc1C(Br)C(O)C",      # 1-Phenyl-2-bromoethanol
        "CC(C)C(O)C(O)C(O)C",      # 2,3,4-Trihydroxy-5-methylhexane
        "CC(C)(C)C(O)C(=O)O",      # 2-Hydroxy-3,3-dimethylbutanoic acid
        "CC([NH2])C(O)C(O)C",      # 2-Amino-3,4-dihydroxybutane
        "C1CCCCC1C(F)C(=O)O",      # 1-Cyclohexyl-2-fluoroacetic acid
        "CC(Br)C(O)C(O)C",         # 2-Bromo-3,4-dihydroxybutane
        "CC(C)C(=O)OCC(O)C",       # 2-Methylpropanoic acid 2-hydroxyethyl ester
        "C/C=C/C(O)C(O)[OH]",      # (E)-4,5-Dihydroxypent-2-en-1-ol
        "CC(F)C(Cl)C(=O)O",        # 2-Fluoro-3-chlorobutanoic acid
        "C1CCCCC1C(O)C(=O)O",      # 1-Cyclohexyl-2-hydroxyacetic acid
        "C/C=C\\Br",                # (Z)-1-Bromopropene
        "F/C=C/Cl",                 # (Z)-1-Fluoro-2-chloroethene
        "C/C=C/CC",                 # (E)-Pent-2-ene
        "C/C=C\\CC",                # (Z)-Pent-2-ene
        "C/C=C/C(=O)O",             # (E)-But-2-enoic acid
        "C/C=C\\C(=O)O",            # (Z)-But-2-enoic acid
        "CC=CC",                    # But-1-ene
        "C/C=C\\C",                # (Z)-But-2-ene
        "C/C=C/[NH2]",              # (E)-Prop-1-en-1-amine
        "C/C=C\\Cl",                # (Z)-1-Chloropropene
        "C/C=C\\C(Cl)C(O)C",       # (Z)-4-Chloro-5-hydroxypent-2-ene
        "C/C=C/C([NH2])C(=O)O",    # (E)-4-Aminopent-2-enoic acid
        "C/C=C/C(O)C(=O)O",        # (E)-4-Hydroxypent-2-enoic acid
        "C/C=C\\C(O)C(O)C",        # (Z)-4,5-Dihydroxypent-2-ene
        "C/C=C/C(F)C(O)C",         # (E)-4-Fluoro-5-hydroxypent-2-ene
        "C/C=C\\C(Br)C(O)[OH]",    # (Z)-4-Bromo-5-hydroxypent-2-en-1-ol
        "C/C=C/C(O)C(O)C(=O)O",    # (E)-4,5-Dihydroxypent-2-enoic acid
        "C/C=C\\C([NH2])C(O)C",    # (Z)-4-Amino-5-hydroxypent-2-ene
        "C/C=C/C(Cl)C(O)[OH]",     # (E)-4-Chloro-5-hydroxypent-2-en-1-ol
        "c1ccccc1",                # Benzene
        "C1CCCCC1",                # Cyclohexane
        "CC(=O)O",                 # Acetic acid
        "CCO",                     # Ethanol
        "CC(Cl)C(O)C(O)C",         # 2-Chloro-3,4-dihydroxybutane
        "CC(F)C([NH2])C(O)C",      # 2-Fluoro-3-amino-4-hydroxybutane
        "CC(C)C(=O)OCC(O)[OH]",    # 2-Methylpropanoic acid 2-hydroxyethanol ester
        "c1ccccc1C(Cl)C(O)[OH]",   # 1-Phenyl-2-chloroethanol
        "CC(C)C(O)C(O)C",          # 3,4-Dihydroxy-5-methylhexane
        "CC([NH2])C(O)C(O)[OH]",   # 2-Amino-3,4-dihydroxypropan-1-ol
        "c1ccccc1C([NH2])C(O)C"    # 1-Phenyl-2-aminoethanol
    ]
    print("\nTesting specific SMILES strings:")
    for test_smiles in test_smiles_list:
        chiral_centers = decoder.detect_chirality(test_smiles)
        ez_bonds = decoder.detect_ez(test_smiles)
        print(f"Testing {test_smiles}")
        print(f"  Chirality       : {chiral_centers}")
        print(f"  E/Z double bond : {ez_bonds}")

if __name__ == "__main__":
    main()
