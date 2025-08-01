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
descList: list  # value = [('PMI1', <function <lambda> at 0xffff8771b600>), ('PMI2', <function <lambda> at 0xffff8771b7e0>), ('PMI3', <function <lambda> at 0xffff8771be20>), ('NPR1', <function <lambda> at 0xffff8771bec0>), ('NPR2', <function <lambda> at 0xffff8771bf60>), ('RadiusOfGyration', <function <lambda> at 0xffff85764040>), ('InertialShapeFactor', <function <lambda> at 0xffff857640e0>), ('Eccentricity', <function <lambda> at 0xffff85764180>), ('Asphericity', <function <lambda> at 0xffff85764220>), ('SpherocityIndex', <function <lambda> at 0xffff857642c0>), ('PBF', <function <lambda> at 0xffff85764360>)]
