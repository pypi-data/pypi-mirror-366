def add_mat(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """
    Adds two matrices element-wise.
    Args:
        a (list[list[float]]): First matrix.
        b (list[list[float]]): Second matrix.
    Returns:
        list[list[float]]: Resulting matrix after addition.
    Raises:
        ValueError: If matrices are empty or have incompatible shapes.
    """
    if not a or not a[0] or not b or not b[0]:
        raise ValueError("Matrices must not be empty")
    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])
    if rows_a != rows_b or cols_a != cols_b:
        raise ValueError("Matrices must have the same shape for addition")
    if any(len(row) != cols_a for row in a) or any(len(row) != cols_b for row in b):
        raise ValueError("All rows in matrices must have the same length")
    
    return [[a[i][j] + b[i][j] for j in range(cols_a)] for i in range(rows_a)]

def sub_mat(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """
    Subtracts matrix b from matrix a element-wise.
    Args:
        a (list[list[float]]): First matrix.
        b (list[list[float]]): Second matrix.
    Returns:
        list[list[float]]: Resulting matrix after subtraction.
    Raises:
        ValueError: If matrices are empty or have incompatible shapes.
    """
    if not a or not a[0] or not b or not b[0]:
        raise ValueError("Matrices must not be empty")
    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])
    if rows_a != rows_b or cols_a != cols_b:
        raise ValueError("Matrices must have the same shape for subtraction")
    if any(len(row) != cols_a for row in a) or any(len(row) != cols_b for row in b):
        raise ValueError("All rows in matrices must have the same length")
    
    return [[a[i][j] - b[i][j] for j in range(cols_a)] for i in range(rows_a)]

def scalar_mul_mat(scalar: float, a: list[list[float]]) -> list[list[float]]:
    """
    Multiplies a matrix by a scalar.
    Args:
        scalar (float): The scalar value.
        a (list[list[float]]): The input matrix.
    Returns:
        list[list[float]]: Resulting matrix after scalar multiplication.
    Raises:
        ValueError: If the matrix is empty.
    """
    if not a or not a[0]:
        raise ValueError("Matrix must not be empty")
    rows, cols = len(a), len(a[0])
    if any(len(row) != cols for row in a):
        raise ValueError("All rows in matrix must have the same length")
    
    return [[scalar * a[i][j] for j in range(cols)] for i in range(rows)]

def mat_vec_mul(a: list[list[float]], b: list[float]) -> list[float]:
    """
    Multiplies a matrix by a vector.
    Args:
        a (list[list[float]]): A matrix represented as a list of lists.
        b (list[float]): A vector represented as a list.
    Returns:
        list[float]: The resulting vector after multiplication.
    Raises:
        ValueError: If matrix columns do not match vector size or matrix is empty.
    """
    if not a or not a[0] or not b:
        raise ValueError("Matrix and vector must not be empty")
    cols = len(a[0])
    if any(len(row) != cols for row in a):
        raise ValueError("All rows in matrix must have the same length")
    if cols != len(b):
        raise ValueError("Matrix columns must match vector size")
    
    return [sum(x * y for x, y in zip(row, b)) for row in a]

def mat_mul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """
    Multiplies two matrices.
    Args:
        a (list[list[float]]): First matrix.
        b (list[list[float]]): Second matrix.
    Returns:
        list[list[float]]: Resulting matrix after multiplication.
    Raises:
        ValueError: If matrix dimensions are incompatible or matrices are empty.
    """
    if not a or not a[0] or not b or not b[0]:
        raise ValueError("Matrices must not be empty")
    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])
    if any(len(row) != cols_a for row in a) or any(len(row) != cols_b for row in b):
        raise ValueError("All rows in matrices must have the same length")
    if cols_a != rows_b:
        raise ValueError("Matrix columns must match matrix rows")
    
    return [[sum(a[i][k] * b[k][j] for k in range(cols_a)) for j in range(cols_b)] for i in range(rows_a)]

def mat_mean(matrix: list[list[float]], mode: str) -> list[float]:
    """
    Computes the mean of a matrix along a specified mode.
    Args:
        matrix (list[list[float]]): The input matrix.
        mode (str): 'column' for column-wise mean, 'row' for row-wise mean.
    Returns:
        list[float]: A list containing the mean values.
    """

    if not matrix or not matrix[0]:
        raise ValueError("Matrix must not be empty")
    
    rows, cols = len(matrix), len(matrix[0])
    
    if mode == 'column':
        return [sum(matrix[i][j] for i in range(rows)) / rows for j in range(cols)]
    else:  # assuming mode is 'row'
        return [sum(row) / cols for row in matrix]

def transpose_mat(a: list[list[int|float]]) -> list[list[int|float]]:
    """
    Transposes a given matrix.
    Args:
        a (list[list[int|float]]): The input matrix.
    Returns:
        list[list[int|float]]: The transposed matrix.
    """
    if not a or not a[0]:
        raise ValueError("Matrix must not be empty")
    
    cols = len(a[0])
    if any(len(row) != cols for row in a):
        raise ValueError("All rows in matrix must have the same length")
    return [list(row) for row in zip(*a)]

def inverse_mat(matrix: list[list[float]]) -> list[list[float]]:
    """
    Computes the inverse of a matrix using the Gauss-Jordan elimination method.
    Args:
        matrix (list[list[float]]): The input matrix.
    Returns:
        list[list[float]]: The inverse matrix.
    Raises:
        ValueError: If the matrix is not square, empty, or singular.
    """

    if not matrix or not matrix[0]:
        raise ValueError("Matrix must not be empty")
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("Matrix must be square")
    
    # Create augmented matrix [A|I]
    augmented = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(matrix)]
    
    # Gauss-Jordan elimination
    for i in range(n):
        # Find pivot
        pivot = augmented[i][i]
        if abs(pivot) < 1e-10:  # Check for zero pivot (singular matrix)
            raise ValueError("Matrix is singular and cannot be inverted")
        
        # Scale row to make pivot = 1
        for j in range(2 * n):
            augmented[i][j] /= pivot
        
        # Eliminate column
        for k in range(n):
            if k != i:
                factor = augmented[k][i]
                for j in range(2 * n):
                    augmented[k][j] -= factor * augmented[i][j]
    
    # Extract the inverse (right half of augmented matrix)
    return [[augmented[i][j] for j in range(n, 2 * n)] for i in range(n)]

def reshape_matrix(a: list[list[int|float]], new_shape: tuple[int, int]) -> list[list[int|float]]:
    """    
    Reshapes a matrix to a new shape.
    Args:
        a (list[list[int|float]]): The input matrix.
        new_shape (tuple[int, int]): The desired shape (rows, columns).
    Returns:
        list[list[int|float]]: The reshaped matrix.
    """

    if not a or not a[0]:
        raise ValueError("Matrix must not be empty")
    rows, cols = len(a), len(a[0])
    if any(len(row) != cols for row in a):
        raise ValueError("All rows in matrix must have the same length")
    new_rows, new_cols = new_shape
    if new_rows <= 0 or new_cols <= 0:
        raise ValueError("New shape dimensions must be positive")
    if rows * cols != new_rows * new_cols:
        raise ValueError("New shape must have the same number of elements as the original matrix")
    
    flat = [x for row in a for x in row]
    return [[flat[i * new_cols + j] for j in range(new_cols)] for i in range(new_rows)]
