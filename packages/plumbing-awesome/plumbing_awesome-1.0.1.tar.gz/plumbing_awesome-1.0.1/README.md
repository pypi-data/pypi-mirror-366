# Plumbing
Pipes!
----------------------
Install:
```sh
pip install plumbing-awesome
```

Use:
```python
from plumbing import Plumber

Plumber(10).pipe(lambda x: x * 10).pipe(str).value # "10"
```
