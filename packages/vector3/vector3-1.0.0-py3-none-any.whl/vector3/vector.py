class Vector:
    """
    A flexible 3D vector class that also supports 2D, 1D, and 0D behavior
    by treating unused components as zero. Supports arithmetic operations,
    dot and cross products, projections, angle calculations, and more.

    Vectors are internally stored in 3D, but lower-dimensional behavior
    is automatically handled when components are zero.

    Example:
        v1 = Vector(1, 2, 3)
        v2 = Vector(4, 0, 0)
        print(v1 + v2)
        print(abs(v1))
        print(v1.angle_degrees(v2))
    """

    def __init__(self, x: int | float = 0, y: int | float = 0, z: int | float = 0):
        """Initialize a vector with x, y, and z components (defaults to 0)."""
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other: 'Vector') -> 'Vector':
        """Returns the sum of two vectors."""
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vector') -> 'Vector':
        """Returns the difference between two vectors."""
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float | int) -> 'Vector':
        """Returns the vector scaled by a scalar."""
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def __neg__(self) -> 'Vector':
        """Returns the negated vector: -v."""
        return Vector(-self.x, -self.y, -self.z)

    def __truediv__(self, scalar: float | int) -> 'Vector':
        """Returns the vector divided by a scalar."""
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return Vector(self.x / scalar, self.y / scalar, self.z / scalar)

    def dimension(self) -> int:
        """Returns the number of non-zero components (1D, 2D, 3D, or 0D)."""
        return sum(1 for val in (self.x, self.y, self.z) if val != 0)

    def __eq__(self, other: 'Vector') -> bool:
        """Checks if two vectors are equal (component-wise)."""
        return self.x == other.x and self.y == other.y and self.z == other.z

    def modulus(self) -> float:
        """Returns the magnitude (length) of the vector."""
        return (self.x**2 + self.y**2 + self.z**2)**0.5

    def unit(self) -> 'Vector':
        """Returns the unit (normalized) vector."""
        mag = self.modulus()
        if mag == 0:
            raise ValueError("Cannot normalize a zero vector")
        return Vector(self.x / mag, self.y / mag, self.z / mag)

    def dot_product(self, other: 'Vector') -> float:
        """Returns the dot product of this vector with another."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross_product(self, other: 'Vector') -> 'Vector':
        """Returns the cross product of this vector with another."""
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x
        return Vector(x, y, z)

    def cos_angle(self, other: 'Vector') -> float:
        """Returns the cosine of the angle between two vectors."""
        dot = self.dot_product(other)
        mod_product = self.modulus() * other.modulus()
        if mod_product == 0:
            raise ValueError("Cannot compute angle with a zero vector")
        return dot / mod_product

    def sin_angle(self, other: 'Vector') -> float:
        """Returns the sine of the angle between two vectors."""
        cos = self.cos_angle(other)
        return (1 - cos**2)**0.5

    def is_zero(self) -> bool:
        """Checks if the vector is a zero vector (0, 0, 0)."""
        return self.x == 0 and self.y == 0 and self.z == 0

    def copy(self) -> 'Vector':
        """Returns a copy of the vector."""
        return Vector(self.x, self.y, self.z)

    def angle_degrees(self, other: 'Vector') -> float:
        """Returns the angle between two vectors in degrees."""
        import math
        cos_theta = self.cos_angle(other)
        cos_theta = max(-1.0, min(1.0, cos_theta))
        angle_rad = math.acos(cos_theta)
        return math.degrees(angle_rad)

    def __iter__(self):
        """Allows unpacking of the vector: x, y, z = vector."""
        yield from (self.x, self.y, self.z)

    def to_tuple(self) -> tuple:
        """Returns the vector as a tuple (x, y, z)."""
        return (self.x, self.y, self.z)

    def __rmul__(self, scalar: float | int) -> 'Vector':
        """Enables scalar * vector (left-hand scalar multiplication)."""
        if not isinstance(scalar, (int, float)):
            raise TypeError("Multiplication is only supported with scalars (int or float).")
        return self * scalar

    def __abs__(self):
        """Returns the magnitude using abs(vector)."""
        return self.modulus()

    def __getitem__(self, index: int) -> float:
        """Access vector components by index: 0=x, 1=y, 2=z."""
        return (self.x, self.y, self.z)[index]

    def __str__(self) -> str:
        """Returns a clean string representation: (x, y, z)."""
        return f"({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        """Returns a formal representation: Vector(x, y, z)."""
        return f"Vector({self.x}, {self.y}, {self.z})"

    def project_onto(self, other: 'Vector') -> 'Vector':
        """Returns the projection of this vector onto another."""
        scalar = self.dot_product(other) / other.modulus()**2
        return other * scalar

    def scalar_triple_product(self, v2: 'Vector', v3: 'Vector') -> float:
        """Returns the scalar triple product: self · (v2 × v3)."""
        return self.dot_product(v2.cross_product(v3))

    def vector_triple_product(self, v2: 'Vector', v3: 'Vector') -> 'Vector':
        """
        Returns the vector triple product: self × (v2 × v3).
        The result lies in the plane of v2 and v3.
        """
        return self.cross_product(v2.cross_product(v3))

    def volume_with(self, v2: 'Vector', v3: 'Vector') -> float:
        """Returns the volume of the parallelepiped formed by self, v2, and v3."""
        return abs(self.scalar_triple_product(v2, v3))
