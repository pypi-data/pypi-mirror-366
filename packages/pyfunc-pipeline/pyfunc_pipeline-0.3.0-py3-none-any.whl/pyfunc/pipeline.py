from collections.abc import Iterable, Callable, Generator
import copy
from functools import reduce, partial
import itertools
from typing import TypeVar, Generic, Any, Optional, cast, Union

from .errors import PipelineError
from .placeholder import Placeholder

# Define a TypeVar for the value in the Pipeline
T = TypeVar('T')
U = TypeVar('U')

# ======================================================================
# The Complete and Corrected Pipeline Class
# ======================================================================

class Pipeline(Generic[T]):
    """
    A chainable functional pipeline for transforming values or iterables.
    Supports chaining, conditional application, operator overloading, and more.
    """ 
    _custom_type_handlers: dict[type, dict[str, Callable[[Any], Any]]] = {}

    @classmethod
    def register_custom_type(cls, custom_type: type, handlers: dict[str, Callable[[Any], Any]]) -> None:
        """Register custom type handlers for specific operations."""
        cls._custom_type_handlers[custom_type] = handlers

    @classmethod
    def extend(cls, name: str, func: Callable[..., Any]) -> None:
        """Extend the Pipeline class with a new method."""
        setattr(cls, name, func)

    @classmethod
    def from_iterable(cls, iterable: Iterable[T]) -> 'Pipeline[Generator[T, None, None]]':
        """Create a Pipeline from any iterable (tuple, set, generator, etc)."""
        return cast('Pipeline[Generator[T, None, None]]', cls(initial_value=iter(iterable)))

    def __init__(self, initial_value: Any = None, _pipeline_func: Optional[Callable[[Any], Any]] = None):
        # _initial_value is the starting value for the pipeline when .get() is called
        self._initial_value = initial_value
        # _pipeline_func is the accumulated function representing all chained operations
        self._pipeline_func: Callable[[Any], Any] = _pipeline_func if _pipeline_func is not None else (lambda x: x)

    def __repr__(self) -> str:
        """Representation for easier debugging."""
        return f"Pipeline(initial_value={repr(self._initial_value)}, func={self._pipeline_func.__name__ if hasattr(self._pipeline_func, '__name__') else 'lambda'})"

    def get(self) -> Any:
        """Get the current value from the pipeline by applying all accumulated functions."""
        return self._pipeline_func(self._initial_value)

    def clone(self) -> 'Pipeline[T]':
        """Return a new Pipeline with the same initial value and accumulated function."""
        return Pipeline(copy.deepcopy(self._initial_value), self._pipeline_func)

    # --- Core Methods ---

    def apply(self, func: Callable[[Any], U]) -> 'Pipeline[U]':
        """Apply func to the value (or map over iterable). Chainable."""
        executable = self._unwrap(func)
        new_pipeline_func = lambda x: executable(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def then(self, func: Callable[[Any], U]) -> 'Pipeline[U]':
        """Alias for apply method for chaining operations."""
        return self.apply(func)

    def map(self, func: Callable[[Any], U]) -> 'Pipeline[Generator[U, None, None]]':
        """Alias for apply method to map a function over elements."""
        executable = self._unwrap(func)
        def _map_func(val: Any) -> Generator[U, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from (executable(v) for v in val)
            else:
                yield executable(val)
        new_pipeline_func = lambda x: _map_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def pipe(self, *funcs: Callable[[Any], Any]) -> 'Pipeline[Any]':
        """Applies a sequence of functions to the current value in order."""
        def chained_func(x: Any) -> Any:
            result = x
            for f in funcs:
                executable = self._unwrap(f)
                result = executable(result)
            return result
        new_pipeline_func = lambda x: chained_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def compose(self, *funcs: Callable[[Any], Any]) -> 'Pipeline[Any]':
        """Compose multiple functions and apply them as a single transformation."""
        composed = reduce(lambda f, g: lambda x: self._unwrap(f)(self._unwrap(g)(x)), reversed(funcs))
        new_pipeline_func = lambda x: composed(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def reduce(self, func: Callable[[Any, Any], U], initializer: Optional[Any] = None) -> 'Pipeline[U]':
        """Apply a function of two arguments cumulatively to the items of an iterable, from left to right, to reduce the iterable to a single value."""
        executable: Callable[[Any, Any], Any]
        if isinstance(func, Placeholder):
            executable = func.as_reducer()
        else:
            executable = func # If not a Placeholder, assume it's a regular 2-arg function

        def _reduce_func(val: Any) -> U:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                if initializer is None:
                    return reduce(executable, val)
                else:
                    return reduce(executable, val, initializer)
            else:
                raise PipelineError("reduce() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _reduce_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def reduce_right(self, func: Callable[[Any, Any], U], initializer: Optional[Any] = None) -> 'Pipeline[U]':
        """Apply a function of two arguments cumulatively to the items of an iterable, from right to left, to reduce the iterable to a single value."""
        executable: Callable[[Any, Any], Any]
        if isinstance(func, Placeholder):
            executable = func.as_reducer()
        else:
            executable = func # If not a Placeholder, assume it's a regular 2-arg function

        def _reduce_right_func(val: Any) -> U:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                # Convert to list to allow reverse iteration and indexing
                val_list = list(val)
                if initializer is None:
                    # If no initializer, start with the last element
                    if not val_list:
                        raise TypeError("reduce_right() of empty sequence with no initial value")
                    acc = val_list[-1]
                    items: Iterable[Any] = val_list[-2::-1] # Iterate from second to last to first
                else:
                    acc = initializer
                    items = reversed(val_list) # Iterate from last to first

                for item in items:
                    acc = executable(item, acc) # Note: item, acc for right-to-left
                return acc
            else:
                raise PipelineError("reduce_right() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _reduce_right_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    # --- Conditional Application ---

    def apply_if(self, condition: Callable[[Any], bool], func: Callable[[Any], Any]) -> 'Pipeline[Any]':
        """Apply func to the entire value if condition is True (or condition(self.value) is True if callable)."""
        executable_condition = self._unwrap(condition)
        executable_func = self._unwrap(func)
        def _apply_if_func(val: Any) -> Any:
            processed_val = list(val) if isinstance(val, Iterable) and not isinstance(val, (str, bytes)) else val
            if executable_condition(processed_val):
                return executable_func(processed_val)
            return processed_val
        new_pipeline_func = lambda x: _apply_if_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def when(self, pred: Callable[[Any], bool], func: Callable[[Any], Any]) -> 'Pipeline[Any]':
        """Apply `func` only if `pred(value)` is True."""
        executable_pred = self._unwrap(pred)
        executable_func = self._unwrap(func)
        def _when_func(val: Any) -> Any:
            processed_val = list(val) if isinstance(val, Iterable) and not isinstance(val, (str, bytes)) else val
            if executable_pred(processed_val):
                return executable_func(processed_val)
            return processed_val
        new_pipeline_func = lambda x: _when_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def unless(self, pred: Callable[[Any], bool], func: Callable[[Any], Any]) -> 'Pipeline[Any]':
        """Apply `func` only if `pred(value)` is False."""
        executable_pred = self._unwrap(pred)
        executable_func = self._unwrap(func)
        def _unless_func(val: Any) -> Any:
            processed_val = list(val) if isinstance(val, Iterable) and not isinstance(val, (str, bytes)) else val
            if not executable_pred(processed_val):
                return executable_func(processed_val)
            return processed_val
        new_pipeline_func = lambda x: _unless_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def if_else(self, pred: Callable[[Any], bool], then_fn: Callable[[Any], Any], else_fn: Callable[[Any], Any]) -> 'Pipeline[Any]':
        """Apply `then_fn` if `pred(value)` is True, otherwise apply `else_fn`."""
        executable_pred = self._unwrap(pred)
        executable_then_fn = self._unwrap(then_fn)
        executable_else_fn = self._unwrap(else_fn)
        def _if_else_func(val: Any) -> Any:
            processed_val = list(val) if isinstance(val, Iterable) and not isinstance(val, (str, bytes)) else val
            if executable_pred(processed_val):
                return executable_then_fn(processed_val)
            else:
                return executable_else_fn(processed_val)
        new_pipeline_func = lambda x: _if_else_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    # --- Operator Overloads ---

    def __or__(self, func: Callable[[Any], U]) -> 'Pipeline[U]':
        """Allow using | operator for chaining: Pipeline(42) | square | half"""
        return self.apply(func)

    def __rshift__(self, func: Callable[[Any], U]) -> 'Pipeline[U]':
        """Allow using >> operator for chaining: Pipeline(42) >> square >> half"""
        return self.apply(func)

    # --- Iterable Manipulation ---
    
    def pairwise(self) -> 'Pipeline[Generator[tuple[Any, Any], None, None]]':
        """Group elements of a list into pairs as tuples."""
        def _pairwise_func(val: Any) -> Generator[tuple[Any, Any], None, None]:
            if isinstance(val, list):
                for i in range(0, len(val) - 1, 2):
                    yield (val[i], val[i + 1])
            else:
                raise PipelineError("pairwise() can only be used on lists.")
        new_pipeline_func = lambda x: _pairwise_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)
        
    def filter(self, predicate: Callable[[Any], bool]) -> 'Pipeline[Generator[T, None, None]]':
        """Filter elements of an iterable based on a predicate."""
        executable = self._unwrap(predicate)
        def _filter_func(val: Any) -> Generator[T, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                for v in val:
                    if executable(v):
                        yield v
            else:
                raise PipelineError("filter() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _filter_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def flatten(self) -> 'Pipeline[Generator[Any, None, None]]':
        """Flatten one level of nested iterables."""
        def _flatten_func(val: Any) -> Generator[Any, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                for item in val:
                    if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                        yield from item
                    else:
                        yield item
            else:
                raise PipelineError("flatten() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _flatten_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def flatten_deep(self) -> 'Pipeline[Generator[Any, None, None]]':
        """Recursively flatten nested iterables."""
        def _flatten_deep_func(val: Any) -> Generator[Any, None, None]:
            def _flatten(v: Any) -> Generator[Any, None, None]:
                for i in v:
                    if isinstance(i, Iterable) and not isinstance(i, (str, bytes)):
                        yield from _flatten(i)
                    else:
                        yield i
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from _flatten(val)
            else:
                raise PipelineError("flatten_deep() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _flatten_deep_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def chunk(self, size: int) -> 'Pipeline[Generator[list[T], None, None]]':
        """Break a sequence into chunks of the given size."""
        def _chunk_func(val: Any) -> Generator[list[T], None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                val = list(val) # Convert to list to allow slicing
                for i in range(0, len(val), size):
                    yield val[i:i + size]
            else:
                raise PipelineError("chunk() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _chunk_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def window(self, size: int, step: int = 1) -> 'Pipeline[Generator[list[T], None, None]]':
        """Create a sliding window view over a sequence."""
        def _window_func(val: Any) -> Generator[list[T], None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                val = list(val) # Convert to list to allow slicing
                for i in range(0, len(val) - size + 1, step):
                    yield val[i:i + size]
            else:
                raise PipelineError("window() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _window_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def sliding_reduce(self, func: Callable[[Any], U], size: int) -> 'Pipeline[Generator[U, None, None]]':
        """Create sliding windows and apply a function to each."""
        executable_func = self._unwrap(func)
        def _sliding_reduce_func(val: Any) -> Generator[U, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                val = list(val) # Convert to list to allow slicing
                for i in range(len(val) - size + 1):
                    yield executable_func(val[i:i + size])
            else:
                raise PipelineError("sliding_reduce() can only be used on iterables.")
        new_pipeline_func = lambda x: _sliding_reduce_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def sliding_pairs(self) -> 'Pipeline[Generator[list[T], None, None]]':
        """Create a sliding window of pairs over a sequence."""
        return self.window(2, 1)

    def sort(self, key: Optional[Callable[[Any], Any]] = None, reverse: bool = False) -> 'Pipeline[list[T]]':
        """Sort the iterable."""
        executable_key = self._unwrap(key) if key else None
        def _sort_func(val: Any) -> list[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                return sorted(val, key=executable_key, reverse=reverse)
            else:
                raise PipelineError("sort() can only be used on iterables.")
        new_pipeline_func = lambda x: _sort_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def unique(self) -> 'Pipeline[Generator[T, None, None]]':
        """Remove duplicates from the iterable while preserving order."""
        def _unique_func(val: Any) -> Generator[T, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                seen = set()
                for x in val:
                    if x not in seen:
                        seen.add(x)
                        yield x
            else:
                raise PipelineError("unique() can only be used on iterables.")
        new_pipeline_func = lambda x: _unique_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def starmap(self, func: Callable[..., U]) -> 'Pipeline[Generator[U, None, None]]':
        """Apply a function to each tuple in a list of tuples."""
        executable = self._unwrap(func)
        def _starmap_func(val: Any) -> Generator[U, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                for i in val:
                    if isinstance(i, tuple):
                        yield executable(*i)
                    else:
                        raise PipelineError("starmap() can only be used on iterables of tuples.")
            else:
                raise PipelineError("starmap() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _starmap_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def first(self) -> 'Pipeline[Optional[T]]':
        """Get the first element of an iterable."""
        def _first_func(val: Any) -> Optional[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                return next(iter(val), None)
            else:
                raise PipelineError("first() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _first_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def last(self) -> 'Pipeline[Optional[T]]':
        """Get the last element of an iterable."""
        def _last_func(val: Any) -> Optional[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                try:
                    if isinstance(val, list): # Optimize for lists
                        return val[-1]
                    # For other iterables, consume to get the last element
                    last_item = None
                    for item in val:
                        last_item = item
                    return last_item
                except IndexError:
                    return None
            else:
                raise PipelineError("last() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _last_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def nth(self, n: int) -> 'Pipeline[Optional[T]]':
        """Get the nth element of an iterable (0-indexed)."""
        def _nth_func(val: Any) -> Optional[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                try:
                    if isinstance(val, list):
                        return val[n]
                    # For other iterables, iterate to the nth element
                    for i, item in enumerate(val):
                        if i == n:
                            return item
                    return None # n is out of bounds
                except IndexError:
                    return None
            else:
                raise PipelineError("nth() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _nth_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def is_empty(self) -> 'Pipeline[bool]':
        """Check if the iterable is empty."""
        def _is_empty_func(val: Any) -> bool:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                return not bool(list(val)) # Convert to list to check emptiness
            else:
                raise PipelineError("is_empty() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _is_empty_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def count(self) -> 'Pipeline[int]':
        """Count the number of elements in an iterable."""
        def _count_func(val: Any) -> int:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                return sum(1 for _ in val)
            else:
                raise PipelineError("count() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _count_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def sum(self) -> 'Pipeline[Union[int, float]]':
        """Calculate the sum of elements in an iterable."""
        def _sum_func(val: Any) -> Union[int, float]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                return sum(val)
            else:
                raise PipelineError("sum() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _sum_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def min(self) -> 'Pipeline[Optional[T]]':
        """Get the minimum element in an iterable."""
        def _min_func(val: Any) -> Optional[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                try:
                    return min(val)
                except ValueError:
                    return None # Empty sequence
            else:
                raise PipelineError("min() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _min_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def max(self) -> 'Pipeline[Optional[T]]':
        """Get the maximum element in an iterable."""
        def _max_func(val: Any) -> Optional[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                try:
                    return max(val)
                except ValueError:
                    return None # Empty sequence
            else:
                raise PipelineError("max() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _max_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def reverse(self) -> 'Pipeline[list[T]]':
        """Reverse the order of elements in an iterable."""
        def _reverse_func(val: Any) -> list[T]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                return list(reversed(val))
            else:
                raise PipelineError("reverse() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _reverse_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def take(self, n: int) -> 'Pipeline[Generator[T, None, None]]':
        """Take the first n elements from the iterable."""
        def _take_func(val: Any) -> Generator[T, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                for i, item in enumerate(val):
                    if i < n:
                        yield item
                    else:
                        break
            else:
                raise PipelineError("take() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _take_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def take_while(self, predicate: Callable[[Any], bool]) -> 'Pipeline[Generator[T, None, None]]':
        """Take elements from the iterable as long as the predicate is true."""
        executable_predicate = self._unwrap(predicate)
        def _take_while_func(val: Any) -> Generator[T, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                for item in val:
                    if executable_predicate(item):
                        yield item
                    else:
                        break
            else:
                raise PipelineError("take_while() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _take_while_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def skip(self, n: int) -> 'Pipeline[Generator[T, None, None]]':
        """Skip the first n elements from the iterable."""
        def _skip_func(val: Any) -> Generator[T, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                for i, item in enumerate(val):
                    if i >= n:
                        yield item
            else:
                raise PipelineError("skip() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _skip_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def skip_while(self, predicate: Callable[[Any], bool]) -> 'Pipeline[Generator[T, None, None]]':
        """Skip elements from the iterable as long as the predicate is true."""
        executable_predicate = self._unwrap(predicate)
        def _skip_while_func(val: Any) -> Generator[T, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                skipping = True
                for item in val:
                    if skipping and executable_predicate(item):
                        continue
                    else:
                        skipping = False
                        yield item
            else:
                raise PipelineError("skip_while() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _skip_while_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def chain(self, *others: Iterable[Any]) -> 'Pipeline[Generator[Any, None, None]]':
        """Concatenate multiple sequences."""
        def _chain_func(val: Any) -> Generator[Any, None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from val
                for other_val in others:
                    if isinstance(other_val, Iterable) and not isinstance(other_val, (str, bytes)):
                        yield from other_val
                    else:
                        raise PipelineError("chain() can only concatenate iterables (excluding str/bytes).")
            else:
                raise PipelineError("chain() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _chain_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def zip_with(self, other: Iterable[Any]) -> 'Pipeline[Generator[tuple[Any, Any], None, None]]':
        """Zip the current iterable with another iterable."""
        def _zip_with_func(val: Any) -> Generator[tuple[Any, Any], None, None]:
            if isinstance(val, Iterable) and isinstance(other, Iterable):
                yield from zip(val, other)
            else:
                raise PipelineError("zip_with() requires two iterables.")
        new_pipeline_func = lambda x: _zip_with_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def product(self, *iterables: Iterable[Any]) -> 'Pipeline[Generator[tuple[Any, ...], None, None]]':
        """Cartesian product of input iterables."""
        def _product_func(val: Any) -> Generator[tuple[Any, ...], None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from itertools.product(val, *iterables)
            else:
                raise PipelineError("product() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _product_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def combinations(self, r: int) -> 'Pipeline[Generator[tuple[Any, ...], None, None]]':
        """Return r-length subsequences of elements from the input iterable."""
        def _combinations_func(val: Any) -> Generator[tuple[Any, ...], None, None]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                yield from itertools.combinations(val, r)
            else:
                raise PipelineError("combinations() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _combinations_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def group_by(self, key: Callable[[Any], Any]) -> 'Pipeline[dict[Any, list[T]]]':
        """Group elements of an iterable based on a key function."""
        executable_key = self._unwrap(key)
        def _group_by_func(val: Any) -> dict[Any, list[T]]:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                groups: dict[Any, list[T]] = {}
                for item in val:
                    group_key = executable_key(item)
                    if group_key not in groups:
                        groups[group_key] = []
                    groups[group_key].append(item)
                return groups
            else:
                raise PipelineError("group_by() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _group_by_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    # --- Conversion Methods ---

    def to_list(self) -> list[Any]:
        """Convert the pipeline result to a list."""
        result = self.get()
        if isinstance(result, Iterable) and not isinstance(result, (str, bytes)):
            return list(result)
        else:
            return [result]

    # --- String Methods ---

    def explode(self, delimiter: Optional[str] = None) -> 'Pipeline[Generator[str, None, None]]':
        """Split a string into characters or words."""
        def _explode_func(val: Any) -> Generator[str, None, None]:
            if isinstance(val, str):
                if delimiter is None:
                    # Split into characters
                    yield from val
                else:
                    # Split by delimiter
                    yield from val.split(delimiter)
            else:
                raise PipelineError("explode() can only be used on strings.")
        new_pipeline_func = lambda x: _explode_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def implode(self, separator: str = "") -> 'Pipeline[str]':
        """Join an iterable of strings into a single string."""
        def _implode_func(val: Any) -> str:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                return separator.join(str(item) for item in val)
            else:
                raise PipelineError("implode() can only be used on iterables (excluding str/bytes).")
        new_pipeline_func = lambda x: _implode_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def surround(self, prefix: str, suffix: str) -> 'Pipeline[str]':
        """Surround a string with prefix and suffix."""
        def _surround_func(val: Any) -> str:
            if isinstance(val, str):
                return f"{prefix}{val}{suffix}"
            else:
                raise PipelineError("surround() can only be used on strings.")
        new_pipeline_func = lambda x: _surround_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def template_fill(self, values: dict[str, Any]) -> 'Pipeline[str]':
        """Fill a template string with values using format()."""
        def _template_fill_func(val: Any) -> str:
            if isinstance(val, str):
                return val.format(**values)
            else:
                raise PipelineError("template_fill() can only be used on strings.")
        new_pipeline_func = lambda x: _template_fill_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    # --- Dictionary Methods ---

    def with_items(self) -> 'Pipeline[Generator[tuple[Any, Any], None, None]]':
        """Convert a dictionary to an iterable of (key, value) pairs."""
        def _with_items_func(val: Any) -> Generator[tuple[Any, Any], None, None]:
            if isinstance(val, dict):
                yield from val.items()
            else:
                raise PipelineError("with_items() can only be used on dictionaries.")
        new_pipeline_func = lambda x: _with_items_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def map_keys(self, func: Callable[[Any], Any]) -> 'Pipeline[dict[Any, Any]]':
        """Apply a function to all keys in a dictionary."""
        executable = self._unwrap(func)
        def _map_keys_func(val: Any) -> dict[Any, Any]:
            if isinstance(val, dict):
                return {executable(k): v for k, v in val.items()}
            else:
                raise PipelineError("map_keys() can only be used on dictionaries.")
        new_pipeline_func = lambda x: _map_keys_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def map_values(self, func: Callable[[Any], Any]) -> 'Pipeline[dict[Any, Any]]':
        """Apply a function to all values in a dictionary."""
        executable = self._unwrap(func)
        def _map_values_func(val: Any) -> dict[Any, Any]:
            if isinstance(val, dict):
                return {k: executable(v) for k, v in val.items()}
            else:
                raise PipelineError("map_values() can only be used on dictionaries.")
        new_pipeline_func = lambda x: _map_values_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    # --- Side Effect Methods ---

    def do(self, func: Callable[[Any], Any]) -> 'Pipeline[T]':
        """Apply a side-effect function without changing the value."""
        executable = self._unwrap(func)
        def _do_func(val: Any) -> Any:
            executable(val)
            return val
        new_pipeline_func = lambda x: _do_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def tap(self, func: Callable[[Any], Any]) -> 'Pipeline[T]':
        """Alias for do() - apply a side-effect function without changing the value."""
        return self.do(func)

    def debug(self, label: str = "DEBUG") -> 'Pipeline[T]':
        """Print the current value for debugging purposes."""
        def _debug_func(val: Any) -> Any:
            print(f"{label}: {val}")
            return val
        new_pipeline_func = lambda x: _debug_func(self._pipeline_func(x))
        return Pipeline(self._initial_value, new_pipeline_func)

    def trace(self, label: str) -> 'Pipeline[T]':
        """Print the current value with a custom label for tracing."""
        return self.debug(label)

    def _unwrap(self, func: Any) -> Callable[[Any], Any]:
        """Unwraps a function or placeholder into an executable callable."""
        if isinstance(func, Placeholder):
            return func._func  # Access the single-argument callable from the placeholder
        elif callable(func):
            return func
        elif isinstance(func, dict):
            # Handle dictionary templates with placeholders
            return self._create_dict_mapper(func)
        elif isinstance(func, str) and '{' in func:
            # Handle f-string-like templates
            return self._create_string_formatter(func)
        else:
            raise PipelineError("Provided object is not callable or a valid placeholder.")
    
    def _create_dict_mapper(self, template: dict[str, Any]) -> Callable[[Any], dict[str, Any]]:
        """Create a function that maps an item to a dictionary using placeholder templates."""
        def dict_mapper(item: Any) -> dict[str, Any]:
            result = {}
            for key, value_template in template.items():
                if isinstance(value_template, Placeholder):
                    result[key] = value_template._func(item)
                elif callable(value_template):
                    result[key] = value_template(item)
                else:
                    result[key] = value_template
            return result
        return dict_mapper
    
    def _create_string_formatter(self, template: str) -> Callable[[Any], str]:
        """Create a function that formats a string template using item data."""
        def string_formatter(item: Any) -> str:
            # Handle f-string-like syntax by evaluating placeholders
            import re
            
            def replace_placeholder(match):
                expr = match.group(1)
                try:
                    # Create a safe evaluation context with the item
                    if isinstance(item, dict):
                        # For dict items, allow direct key access
                        context = {'_': item, **item}
                    else:
                        context = {'_': item}
                    
                    # Handle formatting specifiers
                    if ':' in expr:
                        expr_part, format_spec = expr.rsplit(':', 1)
                        result = eval(expr_part, {"__builtins__": {}}, context)
                        return f"{result:{format_spec}}"
                    else:
                        # Evaluate the expression
                        result = eval(expr, {"__builtins__": {}}, context)
                        return str(result)
                        
                except Exception as e:
                    # If evaluation fails, try simple key lookup for dict items
                    if isinstance(item, dict) and expr in item:
                        return str(item[expr])
                    return match.group(0)  # Return original if evaluation fails
            
            # Replace {expression} patterns
            formatted = re.sub(r'\{([^}]+)\}', replace_placeholder, template)
            return formatted
        
        return string_formatter

    def __call__(self, value: T) -> Any:
        """Make the pipeline callable with an input value."""
        # When called, the pipeline applies its accumulated function to the provided value
        return self._pipeline_func(value)

    def add(self, number: Any) -> 'Pipeline[Any]':
        """Add a number to the current value."""
        return self.apply(lambda x: (x or 0) + number)

    def subtract(self, number: Any) -> 'Pipeline[Any]':
        """Subtract a number from the current value."""
        return self.apply(lambda x: (x or 0) - number)

# Decorator for creating a pipeline from a function
def pipeline(func: Callable[['Pipeline[Any]'], 'Pipeline[Any]']) -> Callable[[Any], 'Pipeline[Any]']:
    """Decorator to create a pipeline from a function."""
    def wrapper(initial_value: Any) -> 'Pipeline[Any]':
        p: Pipeline[Any] = Pipeline(initial_value=initial_value)
        return func(p)
    return wrapper

def pipe(value: T) -> 'Pipeline[T]':
    """Creates a new Pipeline instance with the given initial value."""
    return Pipeline(initial_value=value)
