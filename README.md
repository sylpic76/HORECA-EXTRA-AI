# HORECA Extra AI

Prototype d'application web pour la mise en relation entre établissements de l'hôtellerie-restauration et professionnels disponibles pour des missions courtes.

## Fonctionnalités

- Consultation et filtrage des missions par ville et plage de dates.
- Assistant côté candidat pour vérifier instantanément la compatibilité d'une mission avec son profil.
- Assistant côté employeur pour analyser un talent ciblé et recevoir des suggestions pertinentes.
- Démonstration basée sur des données d'exemple en mémoire.

## Prérequis

- Python 3.10+

## Installation & exécution

```bash
python -m venv .venv
source .venv/bin/activate  # sous Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
flask --app app.server run --debug
```

L'application est accessible sur http://127.0.0.1:5000/.

## Tests rapides

Le projet ne contient pas encore de suite de tests automatisés. Vous pouvez néanmoins vérifier que le code Python est valide en exécutant :

```bash
python -m compileall app
```
