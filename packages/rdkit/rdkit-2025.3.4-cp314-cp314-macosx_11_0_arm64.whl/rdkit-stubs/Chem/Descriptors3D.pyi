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
descList: list  # value = [('PMI1', <function <lambda> at 0x104c82770>), ('PMI2', <function <lambda> at 0x107ebdfe0>), ('PMI3', <function <lambda> at 0x107ebe090>), ('NPR1', <function <lambda> at 0x107ebe140>), ('NPR2', <function <lambda> at 0x107ebe1f0>), ('RadiusOfGyration', <function <lambda> at 0x107ebe2a0>), ('InertialShapeFactor', <function <lambda> at 0x107ebe350>), ('Eccentricity', <function <lambda> at 0x107ebe400>), ('Asphericity', <function <lambda> at 0x107ebe4b0>), ('SpherocityIndex', <function <lambda> at 0x107ebe560>), ('PBF', <function <lambda> at 0x107ebe610>)]
