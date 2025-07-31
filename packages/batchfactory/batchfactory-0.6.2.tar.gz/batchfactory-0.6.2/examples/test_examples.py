from pathlib import Path
import os
import pytest

examples_dir = Path(__file__).resolve().parent
example_files = list(examples_dir.glob('*.py'))
self_path = Path(__file__).resolve()
example_files = [p for p in examples_dir.glob('*.py') if p != self_path]

@pytest.mark.parametrize("example_path", example_files, ids=lambda p: p.name)
def test_example_script(example_path):
    original_cwd = os.getcwd()
    os.chdir(examples_dir)  # Change working dir to examples/
    try:
        print(f"Running example: {example_path.name}")
        exec(example_path.read_text(encoding='utf-8'), {'__name__': '__main__'})
        print(f"Example {example_path.name} executed successfully.")
    finally:
        os.chdir(original_cwd)