from .operations import *

class Vector:
    def __init__(self, values: list[float]):
        if not values:
            raise ValueError("Vector cannot be empty")
        self.values = values

    def __repr__(self):
        return f"Vector({self.values})"

    def __len__(self):
        return len(self.values)

    def __getitem__(self, idx: int) -> float:
        return self.values[idx]

    def __add__(self, other: 'Vector') -> 'Vector':
        return Vector(vector_add(self.values, other.values))

    def __sub__(self, other: 'Vector') -> 'Vector':
        return Vector(vector_sub(self.values, other.values))

    def __mul__(self, scalar: float) -> 'Vector':
        return Vector(vector_scalar_mul(self.values, scalar))
    
    def __rmul__(self, scalar: float) -> 'Vector':
        return self * scalar
    
    def __eq__(self, other: 'Vector') -> bool:
        return self.values == other.values

    def __neg__(self) -> 'Vector':
        return Vector([-x for x in self.values])

    def dot(self, other: 'Vector') -> float:
        return vector_dot(self.values, other.values)

    def norm(self) -> float:
        return vector_norm(self.values)

    def normalize(self) -> 'Vector':
        return Vector(vector_normalize(self.values))

    def project_onto(self, other: 'Vector') -> 'Vector':
        return Vector(vector_projection(self.values, other.values))

    def angle_with(self, other: 'Vector') -> float:
        return angle_between(self.values, other.values)