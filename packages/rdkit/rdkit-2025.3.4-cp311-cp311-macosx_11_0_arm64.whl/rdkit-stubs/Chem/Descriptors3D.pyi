"""
 Descriptors derived from a molecule's 3D structure

"""
from __future__ import annotations
from rdkit.Chem.Descriptors import _isCallable
from rdkit.Chem import rdMolDescriptors
__all__ = ['CalcMolDescriptors3D', 'descList', 'rdMolDescriptors']
def CalcMolDescriptors3D(mol, confId = None):
    """
    
        Compute all 3D descriptors of a molecule
        
        Arguments:
        - mol: the molecule to work with
        - confId: conformer ID to work with. If not specified the default (-1) is used
        
        Return:
        
        dict
            A dictionary with decriptor names as keys and the descriptor values as values
    
        raises a ValueError 
            If the molecule does not have conformers
        
    """
def _setupDescriptors(namespace):
    ...
descList: list  # value = [('PMI1', <function <lambda> at 0x100f8e5c0>), ('PMI2', <function <lambda> at 0x104008d60>), ('PMI3', <function <lambda> at 0x104008ea0>), ('NPR1', <function <lambda> at 0x104008f40>), ('NPR2', <function <lambda> at 0x104008fe0>), ('RadiusOfGyration', <function <lambda> at 0x104009080>), ('InertialShapeFactor', <function <lambda> at 0x104009120>), ('Eccentricity', <function <lambda> at 0x1040091c0>), ('Asphericity', <function <lambda> at 0x104009260>), ('SpherocityIndex', <function <lambda> at 0x104009300>), ('PBF', <function <lambda> at 0x1040093a0>)]
