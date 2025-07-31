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
descList: list  # value = [('PMI1', <function <lambda> at 0x1049a6160>), ('PMI2', <function <lambda> at 0x1049a6840>), ('PMI3', <function <lambda> at 0x1049a68e0>), ('NPR1', <function <lambda> at 0x1049a6980>), ('NPR2', <function <lambda> at 0x1049a6a20>), ('RadiusOfGyration', <function <lambda> at 0x1049a6ac0>), ('InertialShapeFactor', <function <lambda> at 0x1049a6b60>), ('Eccentricity', <function <lambda> at 0x1049a6c00>), ('Asphericity', <function <lambda> at 0x1049a6ca0>), ('SpherocityIndex', <function <lambda> at 0x1049a6d40>), ('PBF', <function <lambda> at 0x1049a6de0>)]
