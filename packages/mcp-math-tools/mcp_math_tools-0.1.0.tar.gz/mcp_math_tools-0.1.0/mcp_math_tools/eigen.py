import numpy as np
import json

def eigen_vectors(matrix_str: str) -> str:
    try:
        matrix_list = json.loads(matrix_str)
        matrix = np.array(matrix_list, dtype=float)
        if matrix.shape[0] != matrix.shape[1]:
            return json.dumps({"error": "Matrix must be square to compute eigenvalues/vectors."})
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        result = {
            "eigenvalues": eigenvalues.tolist(),
            "eigenvectors": eigenvectors.tolist()
        }
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})
