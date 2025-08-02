from rdkit import Chem
from rdkit.Chem.rdMolDescriptors import CalcNumRotatableBonds
from rdkit.Chem import Lipinski

import pandas as pd
import networkx as nx
from joblib import Parallel, delayed
from tqdm.auto import tqdm
import multiprocessing

from polyfeatures.processing import process_polymer_smiles

def identify_backbone_atoms(mol, star_indices):
    if len(star_indices) < 2:
        # No clear backbone ends, assume whole molecule is backbone
        return set(range(mol.GetNumAtoms()))
    try:
        G = nx.from_numpy_array(Chem.GetAdjacencyMatrix(mol))
        path = nx.shortest_path(G, star_indices[0], star_indices[-1])
        return set(path)
    except:
        # Fallback: all atoms in backbone
        return set(range(mol.GetNumAtoms()))

def calculate_backbone_features(smiles):
    features = {'SMILES': smiles, 'backbone_length': 0.0, 'backbone_aromatic_fraction': 0.0, 'backbone_heavy_atom_count': 0.0, 'backbone_electronegative_count': 0.0}
    
    mol, star_indices = process_polymer_smiles(smiles)
    if mol is None:
        return features
    
    backbone_atoms = identify_backbone_atoms(mol, star_indices)
    
    aromatic_count = 0
    backbone_heavy_count = 0
    en_count = 0

    for idx in backbone_atoms:
        atom = mol.GetAtomWithIdx(idx)
        if atom.GetAtomicNum() > 1:
            backbone_heavy_count += 1
            if atom.GetIsAromatic():
                aromatic_count += 1

    for idx in backbone_atoms:
        atom = mol.GetAtomWithIdx(idx)
        if atom.GetSymbol() in ('O', 'N', 'F', 'Cl'):
            en_count += 1   
    
    if backbone_heavy_count > 0:
        features['backbone_aromatic_fraction'] = aromatic_count / backbone_heavy_count
        features['backbone_heavy_atom_count'] = backbone_heavy_count

    features['backbone_electronegative_count'] = en_count
    features['backbone_length'] = len(backbone_atoms)
    
    return features

def calculate_sidechain_features(smiles):
    features = {'SMILES': smiles, 'sidechain_length': 0.0, 'sidechain_heavy_atom_count': 0.0, 'sidechain_branch_count': 0.0, 'sidechain_electronegative_count': 0.0}
    
    mol, star_indices = process_polymer_smiles(smiles)
    if mol is None:
        return features
    
    backbone_atoms = identify_backbone_atoms(mol, star_indices)
    sidechain_atoms = set(range(mol.GetNumAtoms())) - backbone_atoms

    sidechain_heavy_count = 0
    hbond_donor_count = 0
    en_count = 0

    for idx in sidechain_atoms:
        atom = mol.GetAtomWithIdx(idx)
        if atom.GetAtomicNum() > 1:
            sidechain_heavy_count += 1

    sidechain_branches = 0
    visited = set()

    for atom in mol.GetAtoms():
        if atom.GetIdx() in backbone_atoms:
            for nbr in atom.GetNeighbors():
                nbr_idx = nbr.GetIdx()
                if nbr_idx not in backbone_atoms and nbr_idx not in visited:
                    sidechain_branches += 1
                    visited.add(nbr_idx)

    for idx in sidechain_atoms:
        atom = mol.GetAtomWithIdx(idx)
        if atom.GetSymbol() in ('O', 'N', 'F', 'Cl'):
            en_count += 1
            
    features['sidechain_heavy_atom_count'] = sidechain_heavy_count
    features['sidechain_branch_count'] = sidechain_branches
    features['sidechain_length'] = len(sidechain_atoms)
    features['sidechain_electronegative_count'] = en_count

    return features

def calculate_extra_features(smiles):
    features = {'SMILES': smiles, 'num_hbond_donors': 0.0, 'num_hbond_acceptors': 0.0, 'no_atom_count': 0.0}
    
    mol, star_indices = process_polymer_smiles(smiles)
    if mol is None:
        return features
    
    backbone_atoms = identify_backbone_atoms(mol, star_indices)
    sidechain_atoms = set(range(mol.GetNumAtoms())) - backbone_atoms

    hbond_donor_count = Lipinski.NumHDonors(mol)
    hbond_acc_count = Lipinski.NumHAcceptors(mol)
    no_count = Lipinski.NOCount(mol)
    
    features['num_hbond_donors'] = hbond_donor_count
    features['num_hbond_acceptors'] = hbond_acc_count
    features['no_atom_count'] = no_count

    return features