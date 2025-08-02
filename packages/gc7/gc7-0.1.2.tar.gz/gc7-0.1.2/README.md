# PyMoX - GC7

Trousse à outils utiles pour devs en PyMoX

---

## Rapide mémo

```bash
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

py -m build
twine check dist/*  --verbose
twine upload dist/* --verbose

Remove-Item -Recurse -Force dist, gc7.egg-info
```
