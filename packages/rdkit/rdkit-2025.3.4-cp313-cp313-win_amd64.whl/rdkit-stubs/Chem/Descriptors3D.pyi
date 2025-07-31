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
descList: list  # value = [('PMI1', <function <lambda> at 0x000001D02FD06340>), ('PMI2', <function <lambda> at 0x000001D02FD06AC0>), ('PMI3', <function <lambda> at 0x000001D02FD06B60>), ('NPR1', <function <lambda> at 0x000001D02FD06C00>), ('NPR2', <function <lambda> at 0x000001D02FD06CA0>), ('RadiusOfGyration', <function <lambda> at 0x000001D02FD06D40>), ('InertialShapeFactor', <function <lambda> at 0x000001D02FD06DE0>), ('Eccentricity', <function <lambda> at 0x000001D02FD06E80>), ('Asphericity', <function <lambda> at 0x000001D02FD06F20>), ('SpherocityIndex', <function <lambda> at 0x000001D02FD06FC0>), ('PBF', <function <lambda> at 0x000001D02FD07060>)]
