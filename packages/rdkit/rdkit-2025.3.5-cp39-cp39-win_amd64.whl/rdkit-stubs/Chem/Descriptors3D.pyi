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
descList: list  # value = [('PMI1', <function <lambda> at 0x00000265E1E28280>), ('PMI2', <function <lambda> at 0x00000265EA0CDA60>), ('PMI3', <function <lambda> at 0x00000265EA0CDAF0>), ('NPR1', <function <lambda> at 0x00000265EA0CDB80>), ('NPR2', <function <lambda> at 0x00000265EA0CDC10>), ('RadiusOfGyration', <function <lambda> at 0x00000265EA0CDCA0>), ('InertialShapeFactor', <function <lambda> at 0x00000265EA0CDD30>), ('Eccentricity', <function <lambda> at 0x00000265EA0CDDC0>), ('Asphericity', <function <lambda> at 0x00000265EA0CDE50>), ('SpherocityIndex', <function <lambda> at 0x00000265EA0CDEE0>), ('PBF', <function <lambda> at 0x00000265EA0CDF70>)]
