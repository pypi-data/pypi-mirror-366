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
descList: list  # value = [('PMI1', <function <lambda> at 0xffffb7858250>), ('PMI2', <function <lambda> at 0xffffa92b2a30>), ('PMI3', <function <lambda> at 0xffffa92b2ae0>), ('NPR1', <function <lambda> at 0xffffa92b2b90>), ('NPR2', <function <lambda> at 0xffffa92b2c40>), ('RadiusOfGyration', <function <lambda> at 0xffffa92b2cf0>), ('InertialShapeFactor', <function <lambda> at 0xffffa92b2da0>), ('Eccentricity', <function <lambda> at 0xffffa92b2e50>), ('Asphericity', <function <lambda> at 0xffffa92b2f00>), ('SpherocityIndex', <function <lambda> at 0xffffa92b2fb0>), ('PBF', <function <lambda> at 0xffffa92b3060>)]
