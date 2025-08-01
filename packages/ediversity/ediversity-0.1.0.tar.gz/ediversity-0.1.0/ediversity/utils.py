import os
from typing import Sequence, List
import pandas as pd
import matplotlib.pyplot as plt
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs
from sklearn.manifold import TSNE
import numpy as np
from rdkit import RDLogger

RDLogger.DisableLog('rdApp.*')
RDLogger.logger().setLevel(RDLogger.CRITICAL)

def tanimoto_distance_matrix(
    smiles: Sequence[str],
    radius: int = 2,
    n_bits: int = 2048,
) -> np.ndarray:
    """Compute a matrix of Tanimoto distances between molecules.

    Each SMILES string is parsed into an RDKit molecule and converted into
    an Extended Connectivity Fingerprint (also called Morgan fingerprint).  The
    Tanimoto similarity between two binary fingerprints ``a`` and ``b`` is

    .. code:: python

        similarity = DataStructs.TanimotoSimilarity(a, b)

    The distance is defined as ``1 - similarity``.  The returned matrix is
    symmetric with zeros on the diagonal.

    Parameters
    ----------
    smiles : Sequence[str]
        List of SMILES strings to compare.
    radius : int, optional
        Radius of the Morgan fingerprint.  Default is 2.
    n_bits : int, optional
        Length of the fingerprint bit vector.  Default is 2048.

    Returns
    -------
    numpy.ndarray
        A square ``N×N`` matrix of pairwise distances.

    Raises
    ------
    ValueError
        If any SMILES string cannot be parsed into an RDKit molecule.
    """
    n = len(smiles)
    fps: List[DataStructs.cDataStructs.ExplicitBitVect] = []
    for s in smiles:
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            raise ValueError(f"Invalid SMILES string: {s}")
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
        fps.append(fp)

    dist_matrix = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            sim = DataStructs.TanimotoSimilarity(fps[i], fps[j])
            dist = 1.0 - sim
            dist_matrix[i, j] = dist_matrix[j, i] = dist
    return dist_matrix

def read_smiles_file(file_path):
    with open(file_path, 'r') as f:
        smiles_list = [line.strip() for line in f if line.strip()]
    return smiles_list

def save_scores_to_csv(vendi, hamiltonian, output_path):
    df = pd.DataFrame([{
        'vendi_score': vendi,
        'hamiltonian_diversity': hamiltonian
    }])
    os.makedirs(output_path, exist_ok=True)
    csv_path = os.path.join(output_path, 'combined_scores.csv')
    df.to_csv(csv_path, index=False)
    print(f"Scores saved to {csv_path}")

def smiles_to_fps(smiles, radius=2, n_bits=2048):
    fps = []
    for smi in smiles:
        mol = Chem.MolFromSmiles(smi)
        if mol:
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
            arr = np.zeros((1,))
            DataStructs.ConvertToNumpyArray(fp, arr)
            fps.append(arr)
    return np.array(fps)

def plot_distributions(input_smiles, compare_smiles, output_path, radius=2, n_bits=2048):
    input_fps = smiles_to_fps(input_smiles, radius, n_bits)
    compare_fps = smiles_to_fps(compare_smiles, radius, n_bits)

    all_fps = np.vstack([input_fps, compare_fps])
    labels = ['Input'] * len(input_fps) + ['Generated'] * len(compare_fps)

    perplexity = min(30, max(1, len(all_fps) // 3))
    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
    reduced = tsne.fit_transform(all_fps)

    reduced_input = reduced[:len(input_fps)]
    reduced_generated = reduced[len(input_fps):]

    plt.figure(figsize=(10, 8))
    plt.scatter(reduced_input[:, 0], reduced_input[:, 1], alpha=0.6, label='Input SMILES', marker='o')
    plt.scatter(reduced_generated[:, 0], reduced_generated[:, 1], alpha=0.6, label='Generated SMILES', marker='x')
    plt.xlabel('TSNE-1')
    plt.ylabel('TSNE-2')
    plt.title('t-SNE Projection of SMILES Fingerprints')
    plt.legend()

    os.makedirs(output_path, exist_ok=True)
    plot_path = os.path.join(output_path, 'distribution_plot.png')
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")

def save_individual_scores_to_csv(individual_scores, output_path):
    os.makedirs(output_path, exist_ok=True)
    individual_scores.to_csv(os.path.join(output_path, 'individual_scores.csv'), index=False)
    print(f"Individual scores saved to {os.path.join(output_path, 'individual_scores.csv')}")
