#!/usr/bin/env python3
"""
Utility script to list and filter tasks in the benchmark dataset.

Usage:
    cd contrib
    python list_tasks.py
    python list_tasks.py --stage Approved
    python list_tasks.py --stats
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


def load_task_metadata(task_folder: Path) -> Dict:
    """Load metadata for a single task."""
    metadata_file = task_folder / 'metadata.json'
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return {}


def list_all_tasks(tasks_dir: Path) -> List[Dict]:
    """List all tasks with their metadata."""
    tasks = []
    if not tasks_dir.exists():
        return tasks
    for task_folder in sorted(tasks_dir.iterdir()):
        if task_folder.is_dir():
            metadata = load_task_metadata(task_folder)
            metadata['folder'] = task_folder.name
            tasks.append(metadata)
    return tasks


def filter_tasks(tasks: List[Dict], stage: Optional[str] = None) -> List[Dict]:
    """Filter tasks by stage."""
    if stage:
        return [t for t in tasks if t.get('stage') == stage]
    return tasks


def print_task_summary(tasks: List[Dict]):
    """Print a formatted summary of tasks."""
    print(f"\n{'ID':<5} {'Name':<40} {'Stage':<12} {'Author':<10}")
    print("-" * 75)
    for task in tasks:
        task_id = task.get('id', '?')
        task_name = task.get('name', task.get('folder', '?'))
        stage = task.get('stage', 'Unknown')
        author = task.get('brainstorm_by', 'Unknown')
        print(f"{task_id:<5} {task_name:<40} {stage:<12} {author:<10}")
    print(f"\nTotal: {len(tasks)} tasks")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='List and filter benchmark tasks')
    parser.add_argument('--stage', choices=['Approved', 'Brainstorm', 'Deprecated'],
                       help='Filter by task stage')
    parser.add_argument('--stats', action='store_true',
                       help='Show statistics')
    args = parser.parse_args()

    # Scripts are in contrib/, contributed tasks are in parent/cocoabench-head/
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent
    tasks_dir = project_root / 'cocoabench-head'
    
    all_tasks = list_all_tasks(tasks_dir)
    filtered_tasks = filter_tasks(all_tasks, args.stage)

    print_task_summary(filtered_tasks)

    if args.stats:
        print("\n=== Statistics ===")
        stages = {}
        authors = {}
        for task in all_tasks:
            stage = task.get('stage', 'Unknown')
            author = task.get('brainstorm_by', 'Unknown')
            stages[stage] = stages.get(stage, 0) + 1
            authors[author] = authors.get(author, 0) + 1

        print("\nBy Stage:")
        for stage, count in sorted(stages.items()):
            print(f"  {stage}: {count}")

        print("\nBy Author:")
        for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True):
            print(f"  {author}: {count}")


if __name__ == '__main__':
    main()

