import numpy as np
import json
def multiply_matrices(matrix1_str: str, matrix2_str: str) -> str:
    try:
        matrix1_list=json.loads(matrix1_str)
        matrix2_list=json.loads(matrix2_str)
        mat1=np.array(matrix1_list,dtype=float)
        mat2=np.array(matrix2_list,dtype=float)
        if mat1.shape[1]!=mat2.shape[0]:
            raise ValueError("Number of columns in the first matrix must equal the number of rows in the second matrix.")
        result_matrix=np.matmul(mat1,mat2)
        return json.dumps({"result_matrix": result_matrix.tolist()})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred during matrix multiplication: {e}"})