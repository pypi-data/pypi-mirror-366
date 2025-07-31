# README.md
# wt-authlib

Librairie d'authentification pour l'api wt_user. 
Cette librairie permet de sécuriser un projet FastAPI en quelques lignes. une fois l'API sécurisée, seules les personnes aillant un compte WT pourront utiliser l'API protégée.

## Fonctionnalités
- Permet de s'identifier à WT et récupérer un Bearer
- Récupération automatique des clés AWS depuis la base de données (renseignées par `wt_user`)
- Décodage et validation des tokens Bearer pour les endpoints ou routers protégés
- Intégration facile avec FastAPI via `Depends`

## Installation
```bash
uv pip install wt_authlib
```

## Initialisation

Une fois installé, il est essentiel d'initialiser UserApi dans un lifespan FastAPI

```python
from contextlib import asynccontextmanager
from wt_authlib import user_api

@asynccontextmanager
async def lifespan(_: FastAPI):
	user_api.init(
		user_api_url="https://url_api_user.com",
		host="host user db",
		port="port user db",
		username="username user db",
		password="password user db",
	)
	yield

app = FastAPI(lifespan=lifespan)

```

## Sécurisation
il faut ajouter la méthode validate_user comme dépendance (Depends) aux endpoints ou routeur

### exemple ajout router

```python

from wt_authlib import validate_user

routeur = APIRouter()
routeur.include_router(
    document.router,
	dependencies=[Depends(validate_user)]
)
```

### exemple ajout endpoint
```python

from wt_authlib import validate_user

app = FastAPI()

@app.get("/private", dependencies=[Depends(validate_user)])
async def private_route():
    return {"message": "Bienvenue, utilisateur authentifié"}
```


