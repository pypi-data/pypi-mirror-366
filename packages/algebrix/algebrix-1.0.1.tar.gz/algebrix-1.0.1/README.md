# Algebrix
--- 

**Algebrix** is a simple and powerful library for working with vectors and matrices. Supports basic linear algebra operations, including:

* Addition, subtraction, scalar and matrix multiplication

* Normalization of vectors, calculation of angle, projections

* Transpose, inverse matrix, reshape

* And much more

## Installing
```bash
pip install algebrix
```

## Usage examples
```python
from algebrix import Matrix, Vector

# Векторы
v1 = Vector([1, 2, 3])
v2 = Vector([4, 5, 6])

print(v1 + v2)             # Vector([5, 7, 9])
print(v1.dot(v2))          # 32
print(v1.norm())           # 3.741...
print(v1.project_onto(v2)) # Проекция v1 на v2

# Матрицы
m1 = Matrix([[1, 2], [3, 4]])
m2 = Matrix([[5, 6], [7, 8]])

print(m1 + m2)             # Matrix([[6, 8], [10, 12]])
print(m1 * m2)             # Matrix([[19, 22], [43, 50]])
print(m1.T())              # Matrix([[1, 3], [2, 4]])
print(m1.inverse())        # Matrix([[-2.0, 1.0], [1.5, -0.5]])

```

## 🧠 Features
### 🟦 Vector Class
Implements:

* __add__, __sub__, __mul__, __rmul__

* dot(other): dot product

* norm(): Euclidean norm

* normalize(): unit vector

* project_onto(other): vector projection

* angle_with(other): angle between vectors (in radians)

### 🟩 Matrix Class
Implements:

* __add__, __sub__, __mul__, __rmul__

* T(): transpose

* inverse(): matrix inverse

* shape(): returns (rows, cols)

* reshape((new_rows, new_cols)): reshapes the matrix

🛠️ Requirements
* Python 3.10+

* Only depends on the built-in math module (no third-party dependencies)