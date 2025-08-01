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
descList: list  # value = [('PMI1', <function <lambda> at 0x7f94c4e0f9d0>), ('PMI2', <function <lambda> at 0x7f94b55cd160>), ('PMI3', <function <lambda> at 0x7f94b55cd1f0>), ('NPR1', <function <lambda> at 0x7f94b55cd280>), ('NPR2', <function <lambda> at 0x7f94b55cd310>), ('RadiusOfGyration', <function <lambda> at 0x7f94b55cd3a0>), ('InertialShapeFactor', <function <lambda> at 0x7f94b55cd430>), ('Eccentricity', <function <lambda> at 0x7f94b55cd4c0>), ('Asphericity', <function <lambda> at 0x7f94b55cd550>), ('SpherocityIndex', <function <lambda> at 0x7f94b55cd5e0>), ('PBF', <function <lambda> at 0x7f94b55cd670>)]
