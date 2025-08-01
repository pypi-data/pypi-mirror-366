from __future__ import annotations

from typing import Dict, List, Sequence

import math
import numpy as np
import scipy
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs
from ediversity.utils import read_smiles_file

def vendi_scores(
    smiles: Sequence[str],
    qs: Sequence[float] = (1.0,),
    radius: int = 2,
    n_bits: int = 2048,
) -> Dict[float, float]:
    """Compute Vendi scores of various orders for a set of molecules.

    The Vendi score of order ``q`` for a collection of items is defined as

    .. code::

        VS_q = exp( (1/(1 - q)) * log( sum_i λ_i**q ) )

    where ``λ_i`` are the eigenvalues of the normalised similarity matrix
    ``K / tr(K)``【462430457427090†L780-L807】.  When ``q == 1`` the score is the
    exponential of the Shannon entropy of the eigenvalues
    【347232193401755†L23-L25】.  As ``q → ∞`` the score approaches the
    reciprocal of the largest eigenvalue.

    Parameters
    ----------
    smiles : Sequence[str]
        List of SMILES strings representing the molecules.
    qs : Sequence[float], optional
        Orders ``q`` at which to evaluate the Vendi score.  Each value must be
        positive.  The default computes the classical Vendi score (``q=1``).
    radius : int, optional
        Radius of the Morgan fingerprint used to compute similarity.  Default 2.
    n_bits : int, optional
        Length of the fingerprint bit vector.  Default 2048.

    Returns
    -------
    dict[float, float]
        Mapping from order ``q`` to the corresponding Vendi score.

    Raises
    ------
    ValueError
        If any SMILES string cannot be parsed or if ``q`` is negative.
    """
    # Compute fingerprints once
    fps: List[DataStructs.cDataStructs.ExplicitBitVect] = []
    for s in smiles:
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            raise ValueError(f"Invalid SMILES string: {s}")
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
        fps.append(fp)

    n = len(fps)
    # Build similarity matrix (Gram matrix)
    sim_matrix = np.zeros((n, n), dtype=float)
    for i in range(n):
        sim_matrix[i, i] = 1.0  # self‑similarity
        for j in range(i + 1, n):
            sim = DataStructs.TanimotoSimilarity(fps[i], fps[j])
            sim_matrix[i, j] = sim_matrix[j, i] = sim

    # Normalise similarity matrix so that its trace sums to 1
    tr = np.trace(sim_matrix)
    if tr <= 0:
        raise ValueError("Similarity matrix has non‑positive trace")
    norm_sim = sim_matrix / tr
    # Compute eigenvalues
    # The matrix is symmetric and positive semi‑definite, so eigenvalues are real
    eigenvals = scipy.linalg.eigvalsh(norm_sim)
    # Ensure numerical stability: clip small negative values
    eigenvals = np.clip(eigenvals, 0.0, None)
    # Avoid division by zero; for q=1 we need normalised eigenvalues
    vendi: Dict[float, float] = {}
    for q in qs:
        if q < 0:
            raise ValueError(f"Order q must be non‑negative, got {q}")
        if math.isinf(q):
            # Reciprocal of maximum eigenvalue
            max_eig = eigenvals.max()
            vendi[q] = 1.0 / max_eig if max_eig > 0 else float('inf')
            continue
        if abs(q - 1.0) < 1e-12:
            # Shannon entropy
            # Normalise eigenvalues to sum to 1
            lam = eigenvals / eigenvals.sum()
            entropy = -np.sum(lam * np.log(lam + 1e-12))
            vendi[q] = float(np.exp(entropy))
        else:
            # Rényi entropy generalisation
            sum_power = np.sum(np.power(eigenvals, q))
            if sum_power <= 0:
                vendi[q] = 0.0
            else:
                vendi[q] = float(np.exp(np.log(sum_power) / (1.0 - q)))
    return vendi

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compute Vendi scores for a set of molecules")
    parser.add_argument("--input", type=str, required=True, help="Path to input SMILES file")
    parser.add_argument("--qs", type=str, default="1.0", help="Comma-separated list of orders q at which to compute Vendi scores (e.g. '0.1,0.5,1,2,inf')")
    parser.add_argument("--radius", type=int, default=2, help="Radius of the Morgan fingerprint (default: 2)")
    parser.add_argument("--n_bits", type=int, default=2048, help="Number of bits for the Morgan fingerprint (default: 2048)")
    args = parser.parse_args()
    input_smiles = read_smiles_file(args.input)
    vendi = vendi_scores(input_smiles, qs=args.qs, radius=args.radius, n_bits=args.n_bits)
    print(vendi)