# README

**pyarcscripts** est un paquetage Python pour gérer les configurations, l'internationalisation et les routes dans les applications FastAPI.

## Builder le projet

### Installations préalables

* **windows** : python -m pip install sdist bdist_wheel
* **linux** : sudo -H pip3 install sdist bdist_wheel

### Builder le projet

* **windows** : python setup.py sdist bdist_wheel
* **linux** : sudo py setup.py sdist bdist_wheel

### Deployer le projet sur pip

* **windows** : python -m twine upload dist/*
* **linux** : sudo twine upload dist/*

## Git

### Cloner le projet

git init && git remote add origin https://[username]@bitbucket.org/[username]/pypyarc.git && git config user.email [email] && git checkout -b [branche] && git pull origin [branche]

### Pousser le projet

git checkout [branche] && git add -A && git fetch && git merge [branche] && git commit -am "[le message commit]" && git push -u origin [branche]

## Tests

* **windows** : cls && python test.py
* **linux** : clear && python test.py

## Docstring

### Installations préalables

* **windows** : python -m pip install pdoc3
* **linux** : sudo -H pip3 install pdoc3

### Au préalable

Documenter aux préalables son code.

### Generer une documentation

* **windows** : python -m pdoc [projet]
* **linux** : sudo pdoc [projet]

### Exemple d'utilisation

```python 
from fastapi import FastAPI
from pyarcscripts import init_app, t, cfg, register_routes

app = FastAPI()
init_app()

# Use translations
print(t("hello.world"))  # Returns translation for "hello.world"

# Use configurations
print(cfg("database.url"))  # Returns configuration value for "database.url"

# Register routes
router = APIRouter()
register_routes(router, "path/to/routes")
app.include_router(router)
```

### Structure recommandée pour l'application utilisant ce package

```
arc_project/
├── config.xml
├── locales/
│   └── fr.json
├── modules/
│   └── votre_module/
│       ├── config.xml
│       └── locales/
│           └── fr.json
└── routes/
    └── vos_routes/
        └── *.py
```