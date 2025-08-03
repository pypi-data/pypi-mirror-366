"""
Enhanced Error Handling for NovaLang
Provides better error messages and debugging information.
"""

class NovaLangError(Exception):
    """Base class for NovaLang errors."""
    def __init__(self, message: str, line: int = None, column: int = None, filename: str = None):
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename
        super().__init__(self.format_error())
    
    def format_error(self) -> str:
        """Format the error message with location information."""
        if self.line and self.column and self.filename:
            return f"{self.filename}:{self.line}:{self.column}: {self.message}"
        elif self.line and self.column:
            return f"Line {self.line}, Column {self.column}: {self.message}"
        elif self.line:
            return f"Line {self.line}: {self.message}"
        else:
            return self.message


class SyntaxError(NovaLangError):
    """Syntax errors during parsing."""
    pass


class RuntimeError(NovaLangError):
    """Runtime errors during execution."""
    pass


class TypeError(NovaLangError):
    """Type errors."""
    pass


class NameError(NovaLangError):
    """Name resolution errors."""
    pass


def format_stack_trace(error: Exception, filename: str = None) -> str:
    """Format a stack trace for NovaLang errors."""
    import traceback
    
    if isinstance(error, NovaLangError):
        return str(error)
    
    # For other Python exceptions, provide a cleaner format
    tb_lines = traceback.format_exception(type(error), error, error.__traceback__)
    
    # Filter out internal Python frames
    filtered_lines = []
    for line in tb_lines:
        if any(skip in line for skip in ['site-packages', 'python3', 'lib/python']):
            continue
        filtered_lines.append(line)
    
    return ''.join(filtered_lines)
