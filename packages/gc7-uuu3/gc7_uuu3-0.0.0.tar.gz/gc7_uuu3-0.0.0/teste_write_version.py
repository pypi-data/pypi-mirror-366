import re

with open("gc7/__init__.py", "r+") as f:
    content = f.read()
    content = re.sub(
        r'__version__\s*=\s*["\'].*?["\']', '__version__ = "1.1.0"', content
    )
    f.seek(0)
    f.write(content)
    f.truncate()
