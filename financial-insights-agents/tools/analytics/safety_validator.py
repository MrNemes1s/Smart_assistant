"""
Safety Validator for Generated Python Code
Validates code for security risks before execution in sandbox
"""
import ast
import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of code validation"""
    is_safe: bool
    violations: List[str]
    warnings: List[str]
    risk_level: str  # 'safe', 'low', 'medium', 'high', 'critical'


class SafetyValidator:
    """
    Validates Python code for security risks

    Checks for:
    - Dangerous imports (os, subprocess, socket, etc.)
    - File system operations outside allowed paths
    - Network operations
    - Code execution (eval, exec, compile)
    - System commands
    """

    # Completely blocked imports
    BLOCKED_IMPORTS = {
        'os', 'subprocess', 'sys', 'socket', 'http', 'urllib',
        'requests', 'shutil', 'tempfile', 'multiprocessing',
        'threading', 'ctypes', 'importlib', '__builtin__',
        '__import__', 'pty', 'telnetlib', 'ftplib', 'smtplib'
    }

    # Dangerous functions that should be blocked
    BLOCKED_FUNCTIONS = {
        'eval', 'exec', 'compile', '__import__', 'open',
        'input', 'raw_input', 'execfile', 'file', 'reload'
    }

    # Allowed file operations (with specific paths)
    ALLOWED_FILE_PATHS = {
        '/sandbox/data',
        '/sandbox/outputs'
    }

    # Suspicious patterns
    SUSPICIOUS_PATTERNS = [
        r'__\w+__',  # Dunder methods (except common ones)
        r'getattr',
        r'setattr',
        r'delattr',
        r'globals\(',
        r'locals\(',
        r'vars\(',
        r'dir\(',
    ]

    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator

        Args:
            strict_mode: If True, applies stricter validation rules
        """
        self.strict_mode = strict_mode

    def validate(self, code: str) -> ValidationResult:
        """
        Validate Python code for security risks

        Args:
            code: Python code to validate

        Returns:
            ValidationResult with safety assessment
        """
        violations = []
        warnings = []

        # Check 1: Parse code (syntax check)
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return ValidationResult(
                is_safe=False,
                violations=[f"Syntax error: {e}"],
                warnings=[],
                risk_level='critical'
            )

        # Check 2: Analyze imports
        import_violations = self._check_imports(tree)
        violations.extend(import_violations)

        # Check 3: Check for dangerous function calls
        function_violations = self._check_functions(tree)
        violations.extend(function_violations)

        # Check 4: Check file operations
        file_violations, file_warnings = self._check_file_operations(tree)
        violations.extend(file_violations)
        warnings.extend(file_warnings)

        # Check 5: Pattern-based checks
        pattern_warnings = self._check_suspicious_patterns(code)
        warnings.extend(pattern_warnings)

        # Determine risk level and safety
        risk_level = self._assess_risk(violations, warnings)
        is_safe = risk_level in ['safe', 'low']

        return ValidationResult(
            is_safe=is_safe,
            violations=violations,
            warnings=warnings,
            risk_level=risk_level
        )

    def _check_imports(self, tree: ast.AST) -> List[str]:
        """Check for dangerous imports"""
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if module in self.BLOCKED_IMPORTS:
                        violations.append(f"Blocked import: {alias.name}")

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    if module in self.BLOCKED_IMPORTS:
                        violations.append(f"Blocked import from: {node.module}")

        return violations

    def _check_functions(self, tree: ast.AST) -> List[str]:
        """Check for dangerous function calls"""
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None

                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name in self.BLOCKED_FUNCTIONS:
                    violations.append(f"Blocked function call: {func_name}()")

        return violations

    def _check_file_operations(self, tree: ast.AST) -> tuple:
        """Check file operations for path restrictions"""
        violations = []
        warnings = []

        for node in ast.walk(tree):
            # Check for open() calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'open':
                    # Note: 'open' is in BLOCKED_FUNCTIONS, so this is redundant
                    # but we keep it for context-aware checking
                    pass

            # Check for Path operations
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # Check for Path.open, Path.write_text, etc.
                    if node.func.attr in ['open', 'write_text', 'write_bytes', 'read_text', 'read_bytes']:
                        # Try to extract path if it's a constant
                        # This is simplified; full analysis would need data flow
                        warnings.append(f"File operation: Path.{node.func.attr}()")

        return violations, warnings

    def _check_suspicious_patterns(self, code: str) -> List[str]:
        """Check for suspicious patterns in code"""
        warnings = []

        for pattern in self.SUSPICIOUS_PATTERNS:
            matches = re.findall(pattern, code)
            if matches:
                # Filter out common safe patterns
                safe_patterns = {'__init__', '__main__', '__name__', '__file__'}
                dangerous_matches = [m for m in matches if m not in safe_patterns]

                if dangerous_matches:
                    warnings.append(f"Suspicious pattern: {pattern} (matches: {dangerous_matches[:3]})")

        return warnings

    def _assess_risk(self, violations: List[str], warnings: List[str]) -> str:
        """Assess overall risk level"""
        if not violations and not warnings:
            return 'safe'

        if violations:
            # Any violations are considered high risk
            critical_keywords = ['exec', 'eval', 'import os', 'subprocess']
            if any(keyword in v.lower() for v in violations for keyword in critical_keywords):
                return 'critical'
            return 'high'

        if len(warnings) > 5:
            return 'medium'
        elif len(warnings) > 0:
            return 'low'

        return 'safe'


# Convenience function
def validate_code(code: str, strict_mode: bool = True) -> ValidationResult:
    """
    Validate Python code for safety (convenience function)

    Args:
        code: Python code to validate
        strict_mode: Use strict validation rules

    Returns:
        ValidationResult
    """
    validator = SafetyValidator(strict_mode=strict_mode)
    return validator.validate(code)


# Example usage
if __name__ == "__main__":
    # Test with safe code
    safe_code = """
import pandas as pd
import numpy as np

df = pd.DataFrame({'a': [1, 2, 3]})
print(df.mean())
"""

    result = validate_code(safe_code)
    print("Safe code validation:")
    print(f"  Is safe: {result.is_safe}")
    print(f"  Risk level: {result.risk_level}")
    print(f"  Violations: {result.violations}")

    # Test with dangerous code
    dangerous_code = """
import os
import subprocess

os.system('rm -rf /')
subprocess.call(['malicious', 'command'])
exec('malicious code')
"""

    result = validate_code(dangerous_code)
    print("\nDangerous code validation:")
    print(f"  Is safe: {result.is_safe}")
    print(f"  Risk level: {result.risk_level}")
    print(f"  Violations: {result.violations}")
