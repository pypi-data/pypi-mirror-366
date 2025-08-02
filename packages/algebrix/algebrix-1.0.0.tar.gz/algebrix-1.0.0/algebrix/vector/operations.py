import math

def vector_add(vec1: list[float], vec2: list[float]) -> list[float]:
    """Adds two vectors element-wise.
    Args:
        vec1 (list[float]): First vector.
        vec2 (list[float]): Second vector.
    Returns:
        list[float]: Resulting vector after addition."""
    
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must be of the same length")
    return [a + b for a, b in zip(vec1, vec2)]

def vector_sub(vec1: list[float], vec2: list[float]) -> list[float]:
    """Subtracts two vectors element-wise.
    Args:
        vec1 (list[float]): First vector.
        vec2 (list[float]): Second vector.
    Returns:
        list[float]: Resulting vector after subtraction."""
    
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must be of the same length")
    return [a - b for a, b in zip(vec1, vec2)]

def vector_dot(vec1: list[float], vec2: list[float]) -> float:
    """Calculates the dot product of two vectors.
    Args:
        vec1 (list[float]): First vector.
        vec2 (list[float]): Second vector.
    Returns:
        float: The dot product of the two vectors."""
    
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must be of the same length")
    return sum(a * b for a, b in zip(vec1, vec2))

def vector_norm(v: list[float]) -> float:
    """Calculates the Euclidean norm (magnitude) of a vector.
    Args:
        v (list[float]): The vector.
    Returns:
        float: The norm of the vector."""
    
    return math.sqrt(vector_dot(v, v))

def vector_scalar_mul(v: list[float], scalar: float) -> list[float]:
    """Multiplies a vector by a scalar.
    Args:
        v (list[float]): The vector.
        scalar (float): The scalar value.  
    Returns:
        list[float]: The resulting vector after multiplication."""
    
    return [scalar * x for x in v]

def vector_normalize(v: list[float]) -> list[float]:
    """Normalizes a vector to unit length.
    Args:  
        v (list[float]): The vector to normalize.
    Returns:    
        list[float]: The normalized vector.
    """

    n = vector_norm(v)
    if n == 0:
        raise ValueError("Cannot normalize zero vector")
    return [x / n for x in v]

def vector_projection(v: list[float], onto: list[float]) -> list[float]:
    """Projects vector v onto vector onto.
    Args:
        v (list[float]): The vector to project.
        onto (list[float]): The vector to project onto.
    Returns:
        list[float]: The projection of v onto onto.
    """

    dot = vector_dot(v, onto)
    onto_norm_sq = vector_dot(onto, onto)
    if onto_norm_sq == 0:
        raise ValueError("Cannot project onto zero vector")
    scalar = dot / onto_norm_sq
    return vector_scalar_mul(onto, scalar)

def angle_between(vec1: list[float], vec2: list[float]) -> float:
    """Calculates the angle in radians between two vectors.
    Args:
        vec1 (list[float]): First vector.
        vec2 (list[float]): Second vector.
    Returns:
        float: The angle in radians between the two vectors.
    """
    dot = vector_dot(vec1, vec2)
    norms = vector_norm(vec1) * vector_norm(vec2)
    if norms == 0:
        raise ValueError("Cannot compute angle with zero vector")
    return math.acos(dot / norms)