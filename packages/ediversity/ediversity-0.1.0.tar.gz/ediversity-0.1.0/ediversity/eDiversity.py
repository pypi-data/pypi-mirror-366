"""
eDiversity – a minimal toolkit for molecular diversity
-----------------------------------------------------

This module bundles helper functions to compute diversity metrics on
collections of molecules.  Two measures are implemented:

* **Hamiltonian diversity** — the length of the shortest Hamiltonian
  cycle in the complete graph defined by pairwise molecular distances.
  Distances are derived from the Tanimoto dissimilarity of Morgan
  fingerprints.  A 2 opt heuristic is used to approximate the travelling
  salesman problem.

* **Vendi scores** — a family of similarity‑aware diversity indices
  parameterised by an order ``q``.  For ``q = 1`` the score reduces
  to the exponential of the Shannon entropy of the eigenvalues of a
  normalised similarity matrix【347232193401755†L23-L25】.  General values of
  ``q`` recover Rényi‑type diversity measures【462430457427090†L780-L807】.

The helper functions operate on lists of SMILES strings.  To load the
ZINC dataset using PyTorch Geometric use :func:`load_zinc_smiles`.

This docstring is intentionally concise; refer to the source code for
usage examples and additional details.
"""

from __future__ import annotations
from ediversity.utils import (
    read_smiles_file, 
    save_scores_to_csv, 
    plot_distributions, 
    tanimoto_distance_matrix, 
    save_individual_scores_to_csv,
)

from ediversity.vendi_score import vendi_scores
from ediversity.hamiltonian_score import hamiltonian_diversity

from typing import List
import pandas as pd


def compute_individual_scores(generated_smiles, input_smiles):
        scores = []
        for smi in generated_smiles:
            combined = input_smiles + [smi]
            vendi = vendi_scores(combined)[1.0]
            dist = tanimoto_distance_matrix(combined)
            hamiltonian = hamiltonian_diversity(dist)
            scores.append({
                'generated_smiles': smi,
                'vendi_score': vendi,
                'hamiltonian_diversity': hamiltonian
            })
        return pd.DataFrame(scores)

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Compute diversity metrics for molecular data")
    parser.add_argument('--input', type=str, required=True, help='Path to input SMILES file')
    parser.add_argument('--compare', type=str, required=True, help='Path to generated SMILES file')
    parser.add_argument('--output-path', type=str, required=True, help='Directory to save results')
    parser.add_argument(
        "--qs", type=str, default="1.0",
        help="Comma‑separated list of orders q at which to compute Vendi scores (e.g. '0.1,0.5,1,2,inf')."
    )
    parser.add_argument(
        "--radius", type=int, default=2,
        help="Radius of the Morgan fingerprint (default: 2)."
    )
    parser.add_argument(
        "--n_bits", type=int, default=2048,
        help="Number of bits for the Morgan fingerprint (default: 2048)."
    )
    parser.add_argument(
        "--no-hamiltonian", action="store_true",
        help="Skip computing the Hamiltonian diversity to save time."
    )
    parser.add_argument(
        "--no-individual-scores", action="store_true",
        help="Skip computing the individual scores."
    )
    parser.add_argument(
        "--no-combined-scores", action="store_true",
        help="Skip computing the combined scores."
    )
    parser.add_argument(
        "--no-plot", action="store_true",
        help="Skip plotting the distributions to save time."
    )
    args = parser.parse_args()

    # Parse SMILES input
    input_smiles = read_smiles_file(args.input)
    compare_smiles = read_smiles_file(args.compare)

    # Parse q values
    qs: List[float] = []
    for q_str in args.qs.split(","):
        q_str = q_str.strip()
        if not q_str:
            continue
        if q_str.lower() in {"inf", "infinity", "∞"}:
            qs.append(float("inf"))
        else:
            qs.append(float(q_str))
    
    combined_smiles = input_smiles + compare_smiles

    if not args.no_individual_scores:
        individual_scores = compute_individual_scores(compare_smiles, input_smiles)
        save_individual_scores_to_csv(individual_scores, args.output_path)

    if not args.no_combined_scores:
        print(f"Computing combined scores for {len(combined_smiles)} molecules")
        vendi = vendi_scores(combined_smiles, qs=qs, radius=args.radius, n_bits=args.n_bits)
        h_div = None
        if not args.no_hamiltonian:
            dist = tanimoto_distance_matrix(combined_smiles, radius=args.radius, n_bits=args.n_bits)
            h_div = hamiltonian_diversity(dist)
        
        print(f"Combined Vendi scores: {vendi}")
        print(f"Combined Hamiltonian diversity: {h_div}")
        save_scores_to_csv(vendi, h_div, args.output_path)
    if not args.no_plot:
        print(f"Plotting distributions to {args.output_path}, if number of molecules are high, skip this step using --no-plot")
        plot_distributions(input_smiles, compare_smiles, args.output_path, args.radius, args.n_bits)

if __name__ == '__main__':
    main()
