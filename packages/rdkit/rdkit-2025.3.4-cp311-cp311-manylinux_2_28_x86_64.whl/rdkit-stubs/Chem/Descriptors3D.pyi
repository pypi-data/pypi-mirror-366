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
descList: list  # value = [('PMI1', <function <lambda> at 0x7fcf38698540>), ('PMI2', <function <lambda> at 0x7fcf28107920>), ('PMI3', <function <lambda> at 0x7fcf28107a60>), ('NPR1', <function <lambda> at 0x7fcf28107b00>), ('NPR2', <function <lambda> at 0x7fcf28107ba0>), ('RadiusOfGyration', <function <lambda> at 0x7fcf28107c40>), ('InertialShapeFactor', <function <lambda> at 0x7fcf28107ce0>), ('Eccentricity', <function <lambda> at 0x7fcf28107d80>), ('Asphericity', <function <lambda> at 0x7fcf28107e20>), ('SpherocityIndex', <function <lambda> at 0x7fcf28107ec0>), ('PBF', <function <lambda> at 0x7fcf28107f60>)]
