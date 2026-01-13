#!/usr/bin/env python3
"""
Task Validator - Validate task structure and content.

Usage:
    cd contrib
    python validate_task.py <task-name>
    python validate_task.py <task-name> --check-encrypted
    python validate_task.py --all

Checks that all required files exist and have valid content.
"""

import base64
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# ANSI colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_pass(text: str):
    print(f"  {Colors.GREEN}✓{Colors.END} {text}")


def print_warn(text: str):
    print(f"  {Colors.YELLOW}⚠{Colors.END} {text}")


def print_fail(text: str):
    print(f"  {Colors.RED}✗{Colors.END} {text}")


def validate_instruction_md(file_path: Path) -> Tuple[bool, List[str]]:
    """Validate instruction.md content."""
    issues = []
    
    if not file_path.exists():
        return False, ["File does not exist"]
    
    content = file_path.read_text()
    
    # Check for header (should not have one)
    if content.strip().startswith('#'):
        issues.append("Should not start with a header (# ...)")
    
    # Check for output format section
    if '**Output Format:**' not in content and '## Output Format' not in content:
        issues.append("Missing **Output Format:** section")
    
    # Check for answer tags
    if '<answer>' not in content:
        issues.append("Missing <answer> tag example in output format")
    
    # Check for requirements section
    if '**Requirements:**' not in content and '**Task:**' not in content:
        issues.append("Consider adding **Requirements:** or **Task:** sections")
    
    # Check minimum length
    if len(content) < 50:
        issues.append("Content seems too short (< 50 characters)")
    
    return len(issues) == 0, issues


def validate_evaluation_md(file_path: Path) -> Tuple[bool, List[str]]:
    """Validate evaluation.md content."""
    issues = []
    
    if not file_path.exists():
        return False, ["File does not exist"]
    
    content = file_path.read_text()
    
    # Check for required sections
    if '# Evaluation' not in content:
        issues.append("Missing # Evaluation header")
    
    if '## Evaluation Criteria' not in content:
        issues.append("Missing ## Evaluation Criteria section")
    
    if '## Initialization' not in content:
        issues.append("Missing ## Initialization section (use 'None' if not needed)")
    
    # Check for expected answer
    lines = content.split('\n')
    criteria_idx = None
    for i, line in enumerate(lines):
        if '## Evaluation Criteria' in line:
            criteria_idx = i
            break
    
    if criteria_idx is not None:
        # Check if there's content after criteria header
        remaining = '\n'.join(lines[criteria_idx + 1:]).strip()
        if not remaining or remaining.startswith('##'):
            issues.append("Evaluation Criteria section appears empty")
    
    return len(issues) == 0, issues


def validate_solution_md(file_path: Path) -> Tuple[bool, List[str]]:
    """Validate solution.md content."""
    issues = []
    
    if not file_path.exists():
        return False, ["File does not exist"]
    
    content = file_path.read_text()
    
    # Check for header
    if '# Solution' not in content:
        issues.append("Missing # Solution header")
    
    # Check for steps
    if '### Step' not in content and 'Step 1' not in content:
        issues.append("Missing step-by-step breakdown (### Step 1, etc.)")
    
    # Check for final answer
    if 'Final Answer' not in content and 'Answer' not in content:
        issues.append("Consider adding a ### Final Answer section")
    
    # Check minimum length
    if len(content) < 50:
        issues.append("Content seems too short (< 50 characters)")
    
    return len(issues) == 0, issues


def validate_metadata_json(file_path: Path) -> Tuple[bool, List[str]]:
    """Validate metadata.json content."""
    issues = []
    
    if not file_path.exists():
        return False, ["File does not exist"]
    
    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    
    required_fields = ['id', 'name', 'brainstorm_by', 'stage']
    for field in required_fields:
        if field not in data:
            issues.append(f"Missing required field: {field}")
    
    # Validate stage
    valid_stages = ['Brainstorm', 'Approved', 'Deprecated']
    if 'stage' in data and data['stage'] not in valid_stages:
        issues.append(f"Invalid stage: {data['stage']} (must be one of {valid_stages})")
    
    # Check id is integer
    if 'id' in data and not isinstance(data['id'], int):
        issues.append(f"'id' should be an integer, got {type(data['id']).__name__}")
    
    # Check self_checked
    if 'self_checked' in data and data['self_checked'] not in ['yes', 'no']:
        issues.append("'self_checked' should be 'yes' or 'no'")
    
    return len(issues) == 0, issues


def validate_task_yaml(file_path: Path) -> Tuple[bool, List[str]]:
    """Validate task.yaml content."""
    issues = []
    
    if not file_path.exists():
        return False, ["File does not exist"]
    
    content = file_path.read_text()
    
    # Check for instruction field
    if 'instruction:' not in content:
        issues.append("Missing 'instruction:' field")
    
    # Check for output format
    if '<answer>' not in content:
        issues.append("Missing <answer> tag example in instruction")
    
    # Check minimum length
    if len(content) < 50:
        issues.append("Content seems too short (< 50 characters)")
    
    return len(issues) == 0, issues


def validate_test_py(file_path: Path) -> Tuple[bool, List[str]]:
    """Validate test.py content."""
    issues = []
    
    if not file_path.exists():
        return False, ["File does not exist"]
    
    content = file_path.read_text()
    
    # Check for test function
    if 'def test(' not in content:
        issues.append("Missing 'def test(result: dict)' function")
        
    # Check for return statement with passed
    if "'passed'" not in content and '"passed"' not in content:
        issues.append("Test function should return dict with 'passed' key")
    
    return len(issues) == 0, issues


def validate_encryption(task_path: Path) -> Tuple[int, int, int]:
    """Validate that task files are properly encrypted. Returns (passes, warnings, failures)."""
    print(f"\n{Colors.BOLD}Checking encryption: {task_path.name}{Colors.END}")
    
    passes = 0
    warnings = 0
    failures = 0
    
    canary_file = task_path / "canary.txt"
    
    # Required encrypted files
    instruction_enc = task_path / "instruction.md.enc"
    evaluation_enc = task_path / "evaluation.md.enc"
    
    # Check that encrypted files exist
    if instruction_enc.exists():
        print_pass("instruction.md.enc exists")
        passes += 1
        
        # Validate it's valid base64
        try:
            content = instruction_enc.read_text()
            base64.b64decode(content)
            print_pass("instruction.md.enc is valid base64")
            passes += 1
        except Exception as e:
            print_fail(f"instruction.md.enc is not valid base64: {e}")
            failures += 1
    else:
        print_fail("instruction.md.enc - MISSING (required for encrypted tasks)")
        failures += 1
    
    if evaluation_enc.exists():
        print_pass("evaluation.md.enc exists")
        passes += 1
        
        # Validate it's valid base64
        try:
            content = evaluation_enc.read_text()
            base64.b64decode(content)
            print_pass("evaluation.md.enc is valid base64")
            passes += 1
        except Exception as e:
            print_fail(f"evaluation.md.enc is not valid base64: {e}")
            failures += 1
    else:
        print_fail("evaluation.md.enc - MISSING (required for encrypted tasks)")
        failures += 1
    
    if canary_file.exists():
        print_pass("canary.txt exists")
        passes += 1
        
        # Validate canary format (should be 16 hex chars)
        canary = canary_file.read_text().strip()
        if len(canary) == 16 and all(c in '0123456789abcdef' for c in canary):
            print_pass("canary.txt has valid format")
            passes += 1
            
            # Verify canary matches expected value for task name
            task_name = task_path.name
            hasher = hashlib.sha256()
            hasher.update(task_name.encode())
            expected_canary = hasher.hexdigest()[:16]
            if canary == expected_canary:
                print_pass("canary.txt matches task name hash")
                passes += 1
            else:
                print_fail(f"canary.txt does not match expected value for task '{task_name}'")
                failures += 1
        else:
            print_fail("canary.txt has invalid format (expected 16 hex characters)")
            failures += 1
    else:
        print_fail("canary.txt - MISSING (required for encrypted tasks)")
        failures += 1
    
    # Check optional encrypted files
    metadata_enc = task_path / "metadata.json.enc"
    solution_enc = task_path / "solution.md.enc"
    
    if metadata_enc.exists():
        try:
            content = metadata_enc.read_text()
            base64.b64decode(content)
            print_pass("metadata.json.enc exists and is valid base64")
            passes += 1
        except Exception:
            print_fail("metadata.json.enc is not valid base64")
            failures += 1
    
    if solution_enc.exists():
        try:
            content = solution_enc.read_text()
            base64.b64decode(content)
            print_pass("solution.md.enc exists and is valid base64")
            passes += 1
        except Exception:
            print_fail("solution.md.enc is not valid base64")
            failures += 1
    
    # Check that original files are removed
    instruction_md = task_path / "instruction.md"
    evaluation_md = task_path / "evaluation.md"
    metadata_json = task_path / "metadata.json"
    solution_md = task_path / "solution.md"
    
    if instruction_md.exists():
        print_warn("instruction.md still exists (should be removed after encryption)")
        warnings += 1
    else:
        print_pass("instruction.md removed (as expected)")
        passes += 1
    
    if evaluation_md.exists():
        print_warn("evaluation.md still exists (should be removed after encryption)")
        warnings += 1
    else:
        print_pass("evaluation.md removed (as expected)")
        passes += 1
    
    if metadata_json.exists():
        print_warn("metadata.json still exists (should be removed after encryption)")
        warnings += 1
    
    if solution_md.exists():
        print_warn("solution.md still exists (should be removed after encryption)")
        warnings += 1
    
    return passes, warnings, failures


def validate_task(task_path: Path, check_encrypted: bool = False) -> Tuple[int, int, int]:
    """Validate a single task. Returns (passes, warnings, failures)."""
    print(f"\n{Colors.BOLD}Validating: {task_path.name}{Colors.END}")
    
    passes = 0
    warnings = 0
    failures = 0
    
    # Check if encrypted
    if check_encrypted:
        return validate_encryption(task_path)
    
    # Validate unencrypted task
    required_files = [
        ('instruction.md', validate_instruction_md),
        ('evaluation.md', validate_evaluation_md),
        ('solution.md', validate_solution_md),
        ('metadata.json', validate_metadata_json),
    ]
    
    for filename, validator in required_files:
        file_path = task_path / filename
        valid, issues = validator(file_path)
        
        if valid:
            print_pass(filename)
            passes += 1
        else:
            if not file_path.exists():
                print_fail(f"{filename} - MISSING (required)")
                failures += 1
            else:
                print_fail(filename)
                for issue in issues:
                    print(f"      └─ {issue}")
                failures += 1
    
    return passes, warnings, failures


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Validate benchmark task structure')
    parser.add_argument('task_name', nargs='?', help='Task name to validate')
    parser.add_argument('--all', action='store_true', help='Validate all tasks')
    parser.add_argument('--check-encrypted', action='store_true', 
                       help='Check that task files are properly encrypted')
    args = parser.parse_args()
    
    # Scripts are in contrib/, contributed tasks are in parent/cocoabench-head/
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent
    tasks_dir = project_root / 'cocoabench-head'
    
    if args.all:
        # Validate all tasks
        total_passes = 0
        total_warnings = 0
        total_failures = 0
        task_count = 0
        
        if not tasks_dir.exists():
            print_fail(f"Tasks directory not found: {tasks_dir}")
            sys.exit(1)
        
        for task_folder in sorted(tasks_dir.iterdir()):
            if task_folder.is_dir():
                p, w, f = validate_task(task_folder, args.check_encrypted)
                total_passes += p
                total_warnings += w
                total_failures += f
                task_count += 1
        
        print(f"\n{'=' * 50}")
        print(f"{Colors.BOLD}Summary: {task_count} tasks validated{Colors.END}")
        print(f"  {Colors.GREEN}Passed: {total_passes}{Colors.END}")
        print(f"  {Colors.YELLOW}Warnings: {total_warnings}{Colors.END}")
        print(f"  {Colors.RED}Failed: {total_failures}{Colors.END}")
        
        sys.exit(0 if total_failures == 0 else 1)
    
    elif args.task_name:
        # Validate single task
        if not tasks_dir.exists():
            print_fail(f"Tasks directory not found: {tasks_dir}")
            sys.exit(1)
        
        task_path = tasks_dir / args.task_name
        if not task_path.exists():
            print_fail(f"Task not found: {args.task_name}")
            print(f"Available tasks in {tasks_dir}:")
            for t in sorted(tasks_dir.iterdir()):
                if t.is_dir():
                    print(f"  • {t.name}")
            sys.exit(1)
        
        p, w, f = validate_task(task_path, args.check_encrypted)
        print(f"\n{'=' * 50}")
        print(f"{Colors.GREEN}Passed: {p}{Colors.END}  {Colors.YELLOW}Warnings: {w}{Colors.END}  {Colors.RED}Failed: {f}{Colors.END}")
        sys.exit(0 if f == 0 else 1)
    
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python validate_task.py neurips-citation-analysis")
        print("  python validate_task.py neurips-citation-analysis --check-encrypted")
        print("  python validate_task.py --all")
        sys.exit(1)


if __name__ == '__main__':
    main()

