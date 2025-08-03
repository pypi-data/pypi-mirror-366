"""
NovaLang Standard Library
Built-in functions and utilities for NovaLang programs.
"""

import json
import math
import os
import re
import time
from typing import Any, List, Dict


class StandardLibrary:
    """Contains all built-in functions for NovaLang."""
    
    @staticmethod
    def setup_builtins() -> Dict[str, Any]:
        """Return a dictionary of all built-in functions."""
        from interpreter import BuiltinFunction
        
        builtins = {}
        
        # Math functions
        builtins['abs'] = BuiltinFunction(abs)
        builtins['max'] = BuiltinFunction(max)
        builtins['min'] = BuiltinFunction(min)
        builtins['round'] = BuiltinFunction(round)
        builtins['floor'] = BuiltinFunction(math.floor)
        builtins['ceil'] = BuiltinFunction(math.ceil)
        builtins['sqrt'] = BuiltinFunction(math.sqrt)
        builtins['pow'] = BuiltinFunction(pow)
        
        # String functions
        builtins['len'] = BuiltinFunction(len)
        builtins['upper'] = BuiltinFunction(lambda s: str(s).upper())
        builtins['lower'] = BuiltinFunction(lambda s: str(s).lower())
        builtins['trim'] = BuiltinFunction(lambda s: str(s).strip())
        builtins['split'] = BuiltinFunction(lambda s, sep=' ': str(s).split(sep))
        builtins['join'] = BuiltinFunction(lambda sep, arr: sep.join(map(str, arr)))
        builtins['replace'] = BuiltinFunction(lambda s, old, new: str(s).replace(old, new))
        
        # Type checking
        builtins['type'] = BuiltinFunction(lambda x: type(x).__name__)
        builtins['isNumber'] = BuiltinFunction(lambda x: isinstance(x, (int, float)))
        builtins['isString'] = BuiltinFunction(lambda x: isinstance(x, str))
        builtins['isArray'] = BuiltinFunction(lambda x: isinstance(x, list))
        builtins['isObject'] = BuiltinFunction(lambda x: isinstance(x, dict))
        builtins['isFunction'] = BuiltinFunction(lambda x: callable(x))
        
        # Array functions
        builtins['push'] = BuiltinFunction(StandardLibrary._array_push)
        builtins['pop'] = BuiltinFunction(StandardLibrary._array_pop)
        builtins['slice'] = BuiltinFunction(StandardLibrary._array_slice)
        builtins['indexOf'] = BuiltinFunction(StandardLibrary._array_index_of)
        builtins['includes'] = BuiltinFunction(StandardLibrary._array_includes)
        builtins['filter'] = BuiltinFunction(StandardLibrary._array_filter)
        builtins['map'] = BuiltinFunction(StandardLibrary._array_map)
        builtins['reduce'] = BuiltinFunction(StandardLibrary._array_reduce)
        
        # Object functions
        builtins['keys'] = BuiltinFunction(lambda obj: list(obj.keys()) if isinstance(obj, dict) else [])
        builtins['values'] = BuiltinFunction(lambda obj: list(obj.values()) if isinstance(obj, dict) else [])
        builtins['hasKey'] = BuiltinFunction(lambda obj, key: key in obj if isinstance(obj, dict) else False)
        
        # I/O functions
        builtins['readFile'] = BuiltinFunction(StandardLibrary._read_file)
        builtins['writeFile'] = BuiltinFunction(StandardLibrary._write_file)
        builtins['input'] = BuiltinFunction(input)
        
        # JSON functions
        builtins['parseJSON'] = BuiltinFunction(StandardLibrary._parse_json)
        builtins['stringifyJSON'] = BuiltinFunction(StandardLibrary._stringify_json)
        
        # Time functions
        builtins['now'] = BuiltinFunction(time.time)
        builtins['sleep'] = BuiltinFunction(time.sleep)
        
        # Utility functions
        builtins['range'] = BuiltinFunction(lambda *args: list(range(*args)))
        builtins['random'] = BuiltinFunction(StandardLibrary._random)
        builtins['assert'] = BuiltinFunction(StandardLibrary._assert)
        
        return builtins
    
    @staticmethod
    def _array_push(arr: List, *items) -> int:
        """Push items to array and return new length."""
        if not isinstance(arr, list):
            raise RuntimeError("push() can only be called on arrays")
        arr.extend(items)
        return len(arr)
    
    @staticmethod
    def _array_pop(arr: List) -> Any:
        """Pop and return last item from array."""
        if not isinstance(arr, list):
            raise RuntimeError("pop() can only be called on arrays")
        if not arr:
            return None
        return arr.pop()
    
    @staticmethod
    def _array_slice(arr: List, start: int = 0, end: int = None) -> List:
        """Return a slice of the array."""
        if not isinstance(arr, list):
            raise RuntimeError("slice() can only be called on arrays")
        return arr[start:end]
    
    @staticmethod
    def _array_index_of(arr: List, item: Any) -> int:
        """Return the index of item in array, or -1 if not found."""
        if not isinstance(arr, list):
            raise RuntimeError("indexOf() can only be called on arrays")
        try:
            return arr.index(item)
        except ValueError:
            return -1
    
    @staticmethod
    def _array_includes(arr: List, item: Any) -> bool:
        """Check if array includes the item."""
        if not isinstance(arr, list):
            raise RuntimeError("includes() can only be called on arrays")
        return item in arr
    
    @staticmethod
    def _array_filter(arr: List, predicate) -> List:
        """Filter array with predicate function."""
        if not isinstance(arr, list):
            raise RuntimeError("filter() can only be called on arrays")
        if not callable(predicate):
            raise RuntimeError("filter() requires a function as second argument")
        return [item for item in arr if predicate(item)]
    
    @staticmethod
    def _array_map(arr: List, mapper) -> List:
        """Map array with mapper function."""
        if not isinstance(arr, list):
            raise RuntimeError("map() can only be called on arrays")
        
        # Check if mapper is callable (function or NovaFunction)
        from interpreter import NovaFunction, BuiltinFunction
        if not (callable(mapper) or isinstance(mapper, (NovaFunction, BuiltinFunction))):
            raise RuntimeError("map() requires a function as second argument")
        
        result = []
        for item in arr:
            if isinstance(mapper, NovaFunction):
                # For NovaLang functions, we need the interpreter context
                # This is a limitation - we'll handle it differently
                result.append(mapper.call(None, [item]))  # Temporary solution
            elif isinstance(mapper, BuiltinFunction):
                result.append(mapper.call([item]))
            else:
                result.append(mapper(item))
        
        return result
    
    @staticmethod
    def _array_reduce(arr: List, reducer, initial=None) -> Any:
        """Reduce array with reducer function."""
        if not isinstance(arr, list):
            raise RuntimeError("reduce() can only be called on arrays")
        if not callable(reducer):
            raise RuntimeError("reduce() requires a function as second argument")
        
        if initial is not None:
            result = initial
            start = 0
        else:
            if not arr:
                raise RuntimeError("reduce() of empty array with no initial value")
            result = arr[0]
            start = 1
        
        for i in range(start, len(arr)):
            result = reducer(result, arr[i], i, arr)
        
        return result
    
    @staticmethod
    def _read_file(path: str) -> str:
        """Read file and return contents as string."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read file '{path}': {e}")
    
    @staticmethod
    def _write_file(path: str, content: str) -> bool:
        """Write content to file."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(str(content))
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to write file '{path}': {e}")
    
    @staticmethod
    def _parse_json(text: str) -> Any:
        """Parse JSON string."""
        try:
            return json.loads(text)
        except Exception as e:
            raise RuntimeError(f"Failed to parse JSON: {e}")
    
    @staticmethod
    def _stringify_json(obj: Any) -> str:
        """Convert object to JSON string."""
        try:
            return json.dumps(obj, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to stringify JSON: {e}")
    
    @staticmethod
    def _random(*args) -> float:
        """Generate random number."""
        import random
        if len(args) == 0:
            return random.random()
        elif len(args) == 1:
            return random.randint(0, args[0])
        elif len(args) == 2:
            return random.randint(args[0], args[1])
        else:
            raise RuntimeError("random() accepts 0-2 arguments")
    
    @staticmethod
    def _assert(condition: bool, message: str = "Assertion failed") -> bool:
        """Assert that condition is true."""
        if not condition:
            raise AssertionError(message)
        return True
