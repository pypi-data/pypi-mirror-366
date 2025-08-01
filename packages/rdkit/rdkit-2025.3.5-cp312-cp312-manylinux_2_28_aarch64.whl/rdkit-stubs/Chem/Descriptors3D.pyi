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
descList: list  # value = [('PMI1', <function <lambda> at 0xffff9c9b7880>), ('PMI2', <function <lambda> at 0xffff9c9b7f60>), ('PMI3', <function <lambda> at 0xffff9b230040>), ('NPR1', <function <lambda> at 0xffff9b2300e0>), ('NPR2', <function <lambda> at 0xffff9b230180>), ('RadiusOfGyration', <function <lambda> at 0xffff9b230220>), ('InertialShapeFactor', <function <lambda> at 0xffff9b2302c0>), ('Eccentricity', <function <lambda> at 0xffff9b230360>), ('Asphericity', <function <lambda> at 0xffff9b230400>), ('SpherocityIndex', <function <lambda> at 0xffff9b2304a0>), ('PBF', <function <lambda> at 0xffff9b230540>)]
