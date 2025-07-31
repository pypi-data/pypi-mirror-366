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
descList: list  # value = [('PMI1', <function <lambda> at 0x7efc9300c820>), ('PMI2', <function <lambda> at 0x7efc83ae1ea0>), ('PMI3', <function <lambda> at 0x7efc83ae1f30>), ('NPR1', <function <lambda> at 0x7efc83ae1fc0>), ('NPR2', <function <lambda> at 0x7efc83ae2050>), ('RadiusOfGyration', <function <lambda> at 0x7efc83ae20e0>), ('InertialShapeFactor', <function <lambda> at 0x7efc83ae2170>), ('Eccentricity', <function <lambda> at 0x7efc83ae2200>), ('Asphericity', <function <lambda> at 0x7efc83ae2290>), ('SpherocityIndex', <function <lambda> at 0x7efc83ae2320>), ('PBF', <function <lambda> at 0x7efc83ae23b0>)]
