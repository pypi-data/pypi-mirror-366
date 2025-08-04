from typing import Any, Callable, Optional

class Placeholder:
    """
    A placeholder object that creates callable expressions for an elegant pipeline syntax.
    This class is now a pure "recipe builder". The Pipeline class is responsible
    for "unwrapping" the recipe into an executable function.
    """
    def __init__(self, func: Optional[Callable[[Any], Any]] = None, op_func: Optional[Callable[[Any, Any], Any]] = None, other_operand: Optional[Any] = None, is_reverse: bool = False):
        # _func stores the function that has been built up by the expression.
        self._func: Callable[[Any], Any] = func if func is not None else (lambda x: x)
        # For binary operations, these store the details
        self._op_func: Optional[Callable[[Any, Any], Any]] = op_func
        self._other_operand: Optional[Any] = other_operand
        self._is_reverse: bool = is_reverse

    def __call__(self, *args: Any, **kwargs: Any) -> 'Placeholder':
        """
        This method is used to build expressions like _.method(*args, **kwargs).
        It returns a NEW placeholder with the method call added to the function chain.
        It does NOT execute the function. The Pipeline's _unwrap handles execution.
        """
        return Placeholder(func=lambda x: self._func(x)(*args, **kwargs))

    def __getattr__(self, name: str) -> 'Placeholder':
        """Builds a new placeholder for attribute access like _.name"""
        return Placeholder(func=lambda x: getattr(self._func(x), name))

    def __getitem__(self, key: Any) -> 'Placeholder':
        """Builds a new placeholder for item access like _['key']"""
        return Placeholder(func=lambda x: self._func(x)[key])

    def __repr__(self) -> str:
        if self._op_func:
            op_name = self._op_func.__name__ if hasattr(self._op_func, '__name__') else 'binary_op'
            return f"Placeholder(op={op_name}, other={self._other_operand}, reverse={self._is_reverse})"
        return f"Placeholder({self._func.__name__ if hasattr(self._func, '__name__') else 'lambda'})"

    # --- Operator overloads build a new placeholder with the composed function ---
    def _binary_op(self, other: Any, op_func: Callable[[Any, Any], Any], is_reverse: bool = False) -> 'Placeholder':
        # The func for the new placeholder will apply the binary operation
        if isinstance(other, Placeholder):
            new_func = lambda x: op_func(self._func(x), other._func(x))
        else:
            new_func = lambda x: op_func(self._func(x), other)
        return Placeholder(func=new_func, op_func=op_func, other_operand=other, is_reverse=is_reverse)

    # Comparison operators
    def __lt__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a < b)
    def __le__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a <= b)
    def __eq__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a == b) # type: ignore
    def __ne__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a != b) # type: ignore
    def __gt__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a > b)
    def __ge__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a >= b)

    # Arithmetic operators
    def __add__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a + b)
    def __sub__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a - b)
    def __mul__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a * b)
    def __truediv__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a / b)
    def __floordiv__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a // b)
    def __mod__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a % b)
    def __pow__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a ** b)

    # Reverse arithmetic operators
    def __radd__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a + b, True)
    def __rsub__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a - b, True)
    def __rmul__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a * b, True)
    def __rtruediv__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a / b, True)
    def __rfloordiv__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a // b, True)
    def __rmod__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a % b, True)
    def __rpow__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a ** b, True)

    # Bitwise operators
    def __and__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a & b)
    def __or__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a | b)
    def __xor__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a ^ b)
    def __lshift__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a << b)
    def __rshift__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a >> b)

    # Reverse bitwise operators
    def __rand__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a & b, True)
    def __ror__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a | b, True)
    def __rxor__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a ^ b, True)
    def __rlshift__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a << b, True)
    def __rrshift__(self, other: Any) -> 'Placeholder': return self._binary_op(other, lambda a, b: a >> b, True)

    # Unary operators
    def __neg__(self) -> 'Placeholder': return Placeholder(func=lambda x: -self._func(x))
    def __pos__(self) -> 'Placeholder': return Placeholder(func=lambda x: +self._func(x))
    def __invert__(self) -> 'Placeholder': return Placeholder(func=lambda x: ~self._func(x))
    def __abs__(self) -> 'Placeholder': return Placeholder(func=lambda x: abs(self._func(x)))

    # Container operators
    def __contains__(self, item: Any) -> 'Placeholder':
        return Placeholder(func=lambda x: item in self._func(x))

    # Special methods that should not be used directly on Placeholder
    def __len__(self) -> Any:
        raise TypeError("len() of Placeholder is not supported. Use _.len() or len(pipeline.get())")

    def __bool__(self) -> Any:
        raise TypeError("bool() of Placeholder is not supported. Use _.is_true() or similar.")

    def as_reducer(self) -> Callable[[Any, Any], Any]:
        """Returns a two-argument function suitable for reduce operations."""
        if self._op_func is None:
            raise TypeError("This placeholder does not represent a binary operation for reduce.")

        op_func = self._op_func
        other_operand = self._other_operand
        is_reverse = self._is_reverse

        if isinstance(other_operand, Placeholder):
            # If the other operand is also a placeholder, it means the operation is like _ + _
            # In this case, both 'a' and 'b' come from the reduce operation itself.
            return lambda a, b: op_func(a, b)
        else:
            # If the other operand is a concrete value, it's fixed.
            if is_reverse:
                return lambda a, b: op_func(other_operand, b) # other_operand is left, b is right
            else:
                return lambda a, b: op_func(a, other_operand) # a is left, other_operand is right

    # Function composition operators
    def __rshift__(self, other: 'Placeholder') -> 'Placeholder':
        """Function composition: f >> g means g(f(x))"""
        if isinstance(other, Placeholder):
            return Placeholder(func=lambda x: other._func(self._func(x)))
        else:
            return Placeholder(func=lambda x: other(self._func(x)))

    def __lshift__(self, other: 'Placeholder') -> 'Placeholder':
        """Function composition: f << g means f(g(x))"""
        if isinstance(other, Placeholder):
            return Placeholder(func=lambda x: self._func(other._func(x)))
        else:
            return Placeholder(func=lambda x: self._func(other(x)))




