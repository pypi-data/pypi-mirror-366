from rdkit import Chem
from rdkit import Chem
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Lipinski
import networkx as nx
from joblib import Parallel, delayed
from tqdm.auto import tqdm
import multiprocessing

from polyfeatures.calculate_features import calculate_backbone_features, calculate_sidechain_features, calculate_extra_features

def analyze_polymers(smiles_list, n_jobs=-1):
    if n_jobs == -1:
        n_jobs = multiprocessing.cpu_count()
    
    backbone_results = Parallel(n_jobs=n_jobs)(
        delayed(calculate_backbone_features)(smiles) for smiles in tqdm(smiles_list)
    )
    
    sidechain_results = Parallel(n_jobs=n_jobs)(
        delayed(calculate_sidechain_features)(smiles) for smiles in tqdm(smiles_list)
    )

    extra_results = Parallel(n_jobs=n_jobs)(
        delayed(calculate_extra_features)(smiles) for smiles in tqdm(smiles_list)
    )

    backbone_results = pd.DataFrame(backbone_results).set_index('SMILES')
    sidechain_results = pd.DataFrame(sidechain_results).set_index('SMILES')
    extra_results = pd.DataFrame(extra_results).set_index('SMILES')
    
    x = pd.concat([backbone_results, sidechain_results], axis=1)
    return pd.concat([x, extra_results], axis=1)