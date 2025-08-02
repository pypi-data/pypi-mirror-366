from ..vector.vector import Vector
from .operations import *

class Matrix:
    def __init__(self, values: list[list[float]]):
        if not values or not values[0]:
            raise ValueError("Matrix cannot be empty")
        self.values = values
        self.rows = len(values)
        self.cols = len(values[0])
        if any(len(row) != self.cols for row in values):
            raise ValueError("All rows must have the same number of columns")

    def __repr__(self):
        return f"Matrix({self.values})"

    def __getitem__(self, idx: int) -> list[float]:
        return self.values[idx]

    def __add__(self, other: 'Matrix') -> 'Matrix':
        """
        Adds two matrices using the + operator.
        Args:
            other (Matrix): The matrix to add.
        Returns:
            Matrix: The resulting matrix.
        Raises:
            TypeError: If other is not a Matrix.
            ValueError: If matrices have incompatible shapes.
        """
        if not isinstance(other, Matrix):
            raise TypeError("Can only add Matrix to Matrix")
        try:
            result = add_mat(self.values, other.values)
            return Matrix(result)
        except ValueError as e:
            raise ValueError(str(e)) from e
    
    def __sub__(self, other: 'Matrix') -> 'Matrix':
        """
        Subtracts another matrix using the - operator.
        Args:
            other (Matrix): The matrix to subtract.
        Returns:
            Matrix: The resulting matrix.
        Raises:
            TypeError: If other is not a Matrix.
            ValueError: If matrices have incompatible shapes.
        """
        if not isinstance(other, Matrix):
            raise TypeError("Can only subtract Matrix from Matrix")
        try:
            result = sub_mat(self.values, other.values)
            return Matrix(result)
        except ValueError as e:
            raise ValueError(str(e)) from e
    
    def __mul__(self, other) -> 'Matrix | Vector':
        """
        Multiplies the matrix by another matrix, vector, or scalar using the * operator.
        Args:
            other: The matrix, vector, or scalar to multiply by.
        Returns:
            Matrix or Vector: The resulting matrix or vector.
        Raises:
            TypeError: If other is not a Matrix, Vector, or scalar (int/float).
            ValueError: If dimensions are incompatible.
        """
        if isinstance(other, Matrix):
            try:
                result = mat_mul(self.values, other.values)
                return Matrix(result)
            except ValueError as e:
                raise ValueError("Incompatible matrix shapes for multiplication") from e
        elif isinstance(other, Vector):
            try:
                result = mat_vec_mul(self.values, other.values)
                return Vector(result)
            except ValueError as e:
                raise ValueError("Matrix columns must match vector size") from e
        elif isinstance(other, (int, float)):
            try:
                result = scalar_mul_mat(other, self.values)
                return Matrix(result)
            except ValueError as e:
                raise ValueError(str(e)) from e
        else:
            raise TypeError("Matrix can only be multiplied by Matrix, Vector, or scalar")
    
    def __rmul__(self, other) -> 'Matrix':
        """
        Handles scalar * Matrix multiplication.
        Args:
            other: The scalar (int/float).
        Returns:
            Matrix: The resulting matrix.
        Raises:
            TypeError: If other is not a scalar (int/float).
            ValueError: If the matrix is empty.
        """
        if isinstance(other, (int, float)):
            try:
                result = scalar_mul_mat(other, self.values)
                return Matrix(result)
            except ValueError as e:
                raise ValueError(str(e)) from e
        else:
            raise TypeError("Matrix can only be multiplied by a scalar on the left")
        
    def T(self) -> 'Matrix':
        try:
            result = transpose_mat(self.values)
            return Matrix(result)
        except ValueError as e:
            raise ValueError("Matrix must not be empty") from e

    def inverse(self) -> 'Matrix':
        """
        Computes the inverse of the matrix using the Gauss-Jordan elimination method.
        Returns:
            Matrix: The inverse matrix.
        Raises:
            ValueError: If the matrix is not square, empty, or singular.
        """
        try:
            result = inverse_mat(self.values)
            return Matrix(result)
        except ValueError as e:
            raise ValueError(str(e)) from e

    def shape(self) -> tuple[int, int]:
        return (self.rows, self.cols)
    
    def reshape(self, new_shape: tuple[int, int]) -> 'Matrix':
        try:
            result = reshape_matrix(self.values, new_shape)
            return Matrix(result)
        except ValueError as e:
            raise ValueError(str(e)) from e
