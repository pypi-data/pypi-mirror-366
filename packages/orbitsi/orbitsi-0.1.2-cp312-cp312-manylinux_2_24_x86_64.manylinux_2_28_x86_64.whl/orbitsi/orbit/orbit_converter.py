import numpy as np
import os

class OrbitMatrixConverter:
    def __init__(self):
        self.matrices = self._load_matrices()

    def _load_matrices(self):
        """Load conversion matrices as NumPy arrays, not matrix objects."""
        this_dir = os.path.dirname(__file__)
        matrices_path = os.path.join(this_dir, 'orbit_conversion_matrices.npz')
        matrices_file = np.load(matrices_path, allow_pickle=True)

        return {
            int(k.split('_')[1]): np.asarray(matrices_file[k])
            for k in matrices_file.files
        }

    def noninduced_to_induced(self, noninduced_matrix: np.ndarray) -> np.ndarray:
        """Convert non-induced orbit counts to induced counts."""
        mat = self.matrices
        T = np.asarray(noninduced_matrix.T)  # ensure ndarray

        if noninduced_matrix.shape[1] == 15:
            induced = np.vstack([
                T[0:1, :],
                np.linalg.solve(mat[3], T[1:4, :]),
                np.linalg.solve(mat[4], T[4:15, :])
            ])
        elif noninduced_matrix.shape[1] == 73:
            induced = np.vstack([
                T[0:1, :],
                np.linalg.solve(mat[3], T[1:4, :]),
                np.linalg.solve(mat[4], T[4:15, :]),
                np.linalg.solve(mat[5], T[15:, :])
            ])
        else:
            raise ValueError("Unsupported orbit count size for conversion.")

        return np.asarray(induced.T, dtype=int)

    def induced_to_noninduced(self, induced_matrix: np.ndarray) -> np.ndarray:
        """Convert induced orbit counts to non-induced counts."""
        mat = self.matrices
        T = np.asarray(induced_matrix.T)  # ensure ndarray

        if induced_matrix.shape[1] == 15:
            noninduced = np.vstack([
                T[0:1, :],
                mat[3] @ T[1:4, :],
                mat[4] @ T[4:15, :]
            ])
        elif induced_matrix.shape[1] == 73:
            noninduced = np.vstack([
                T[0:1, :],
                mat[3] @ T[1:4, :],
                mat[4] @ T[4:15, :],
                mat[5] @ T[15:, :]
            ])
        else:
            raise ValueError("Unsupported orbit count size for conversion.")

        return np.asarray(noninduced.T, dtype=int)
