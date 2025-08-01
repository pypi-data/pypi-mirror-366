import os
import sys
import ast
import subprocess
from pathlib import Path

try:
    from importlib.metadata import distributions
except ImportError:
    from importlib_metadata import distributions  # type: ignore
try:
    import stdlib_list
    STDLIB_MODULES = set(stdlib_list.stdlib_list())
except ImportError:
    STDLIB_MODULES = set(sys.builtin_module_names)


def _get_installed_packages():
    pkgs = set()
    for dist in distributions():
        name = dist.metadata['Name']
        if name:
            pkgs.add(name.lower())
    return pkgs


def _parse_imports_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        node = ast.parse(f.read(), filename=file_path)
    imports = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Import):
            for alias in n.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(n, ast.ImportFrom):
            if n.module:
                imports.add(n.module.split('.')[0])
    return imports


def _scan_python_files(root_dir):
    all_imports = set()
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith('.py'):
                fpath = os.path.join(dirpath, fname)
                try:
                    all_imports |= _parse_imports_from_file(fpath)
                except Exception:
                    pass
    return all_imports


def _install_with_pip(package):
    print(f"Installing {package}...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=False)


def _install_requirements(requirements_path):
    print(f"Installing dependencies from {requirements_path}...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_path], check=False)


def install():
    cwd = os.getcwd()
    requirements = Path(cwd) / 'requirements.txt'
    if requirements.exists():
        _install_requirements(str(requirements))
    
    print("Scanning Python files for additional dependencies...")
    imports = _scan_python_files(cwd)
    installed = _get_installed_packages()
    missing = set()
    for imp in imports:
        if imp in STDLIB_MODULES or imp in installed:
            continue
        if (Path(cwd) / (imp + '.py')).exists():
            continue
        missing.add(imp)
    for pkg in sorted(missing):
        _install_with_pip(pkg)
    print("Dependency installation complete!")
