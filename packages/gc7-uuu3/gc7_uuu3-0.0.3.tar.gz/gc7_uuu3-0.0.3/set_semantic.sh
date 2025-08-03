mkdir test-semantic
cd test-semantic
python -m venv .venv
.venv\Scripts\activate  # ou source .venv/bin/activate sur Unix
pip install python-semantic-release build

mkdir testpkg
echo '__version__ = "0.1.0"' > testpkg/__init__.py

echo '''
[tool.semantic_release]
version_variable = "testpkg/__init__.py:__version__"
build_command = "python -m build"
upload_to_pypi = false
log_level = "DEBUG"
''' > pyproject.toml

git init
git add .
git commit -m "feat: initial commit"
