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
descList: list  # value = [('PMI1', <function <lambda> at 0x00000292FAC80220>), ('PMI2', <function <lambda> at 0x00000292FAC80860>), ('PMI3', <function <lambda> at 0x00000292FAC809A0>), ('NPR1', <function <lambda> at 0x00000292FAC80A40>), ('NPR2', <function <lambda> at 0x00000292FAC80AE0>), ('RadiusOfGyration', <function <lambda> at 0x00000292FAC80B80>), ('InertialShapeFactor', <function <lambda> at 0x00000292FAC80C20>), ('Eccentricity', <function <lambda> at 0x00000292FAC80CC0>), ('Asphericity', <function <lambda> at 0x00000292FAC80D60>), ('SpherocityIndex', <function <lambda> at 0x00000292FAC80E00>), ('PBF', <function <lambda> at 0x00000292FAC80EA0>)]
