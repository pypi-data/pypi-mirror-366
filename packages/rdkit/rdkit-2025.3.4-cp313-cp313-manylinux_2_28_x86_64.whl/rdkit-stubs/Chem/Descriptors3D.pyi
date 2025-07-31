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
descList: list  # value = [('PMI1', <function <lambda> at 0x7f1b17193560>), ('PMI2', <function <lambda> at 0x7f1b17193740>), ('PMI3', <function <lambda> at 0x7f1b17193d80>), ('NPR1', <function <lambda> at 0x7f1b17193e20>), ('NPR2', <function <lambda> at 0x7f1b17193ec0>), ('RadiusOfGyration', <function <lambda> at 0x7f1b17193f60>), ('InertialShapeFactor', <function <lambda> at 0x7f1b1560c040>), ('Eccentricity', <function <lambda> at 0x7f1b1560c0e0>), ('Asphericity', <function <lambda> at 0x7f1b1560c180>), ('SpherocityIndex', <function <lambda> at 0x7f1b1560c220>), ('PBF', <function <lambda> at 0x7f1b1560c2c0>)]
