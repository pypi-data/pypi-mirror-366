from __future__ import annotations
from typing import List

import numpy as np
from ediversity.utils import read_smiles_file, tanimoto_distance_matrix

def hamiltonian_diversity(dist_matrix: np.ndarray) -> float:
    """Approximate the Hamiltonian diversity via a 2 opt heuristic.

    Given a symmetric matrix of pairwise distances, this function
    constructs an approximate shortest Hamiltonian cycle visiting each
    index exactly once.  The algorithm proceeds in two stages:

    1. **Nearest neighbour tour:** Starting from index ``0``, successively
       visit the nearest unvisited node until all nodes have been visited.
    2. **2 opt optimisation:** Repeatedly examine pairs of edges and swap
       segments when doing so shortens the overall tour.  Terminate when
       no swaps reduce the cycle length.

    The length of the resulting cycle is returned as the Hamiltonian
    diversity.

    Parameters
    ----------
    dist_matrix : numpy.ndarray
        A symmetric matrix of distances with zeros on the diagonal.

    Returns
    -------
    float
        Total length of the approximated shortest Hamiltonian cycle.
    """
    n = dist_matrix.shape[0]
    if n == 0:
        return 0.0

    # Construct an initial tour using a simple nearest neighbour heuristic
    unvisited = set(range(1, n))
    tour = [0]
    current = 0
    while unvisited:
        next_city = min(unvisited, key=lambda j: dist_matrix[current, j])
        tour.append(next_city)
        unvisited.remove(next_city)
        current = next_city
    # Complete the cycle
    tour.append(0)

    def tour_length(t: List[int]) -> float:
        return sum(dist_matrix[t[i], t[i + 1]] for i in range(len(t) - 1))

    improved = True
    while improved:
        improved = False
        # 2 opt: iterate over pairs of edges (i,i+1) and (j,j+1)
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                if j - i == 1:
                    continue  # edges are consecutive; skip
                # cost difference if we reverse segment [i:j]
                a, b = tour[i - 1], tour[i]
                c, d = tour[j - 1], tour[j]
                delta = (
                    dist_matrix[a, c]
                    + dist_matrix[b, d]
                    - dist_matrix[a, b]
                    - dist_matrix[c, d]
                )
                if delta < -1e-12:
                    # Reverse the segment
                    tour[i:j] = reversed(tour[i:j])
                    improved = True
        # End for j
    # End while improved
    return tour_length(tour)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compute Hamiltonian diversity for a set of molecules")
    parser.add_argument("--input", type=str, required=True, help="Path to input SMILES file")
    args = parser.parse_args()
    input_smiles = read_smiles_file(args.input)
    dist = tanimoto_distance_matrix(input_smiles, radius=args.radius, n_bits=args.n_bits)
    h_div = hamiltonian_diversity(dist)
    print(h_div)