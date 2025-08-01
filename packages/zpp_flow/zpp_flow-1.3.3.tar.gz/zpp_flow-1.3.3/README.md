<p align="center">
  <img src="asset/flow_logo_small.png" alt="logo"/>
</p>

## Informations
Application pour permettre l'exécution de task ou de workflow basé sur des scripts Python.
Un task représente un ensemble de fonction.
Un flow représente un ensemble de fonction où la sortie de la fonction A devient les paramètres de la fonction suivante.


### Prérequis
- Python 3
<br>

## Installation
```console
pip install zpp_flow
```
<br>

## Utilisation

### config

La commande permet de lister les paramètres de configuration. 
Il est possible de les éditer en rajoutant le nom du paramètre et sa valeur à la commande

```console
flow config PARAM_NAME VALUE
```

### run

La commande permet d'exécuter une task ou un flow. Pour cela, il suffit de renseigner le nom de la task.

```console
flow run TASK_NAME
```

En paramètre supplémentaire, il est possible d'utiliser:
<br>
**--task** pour filtrer sur les task
<br>
**--flow** pour filtrer sur les flow
<br>
**--debug** pour afficher la totalité des retour de code
<br>
**--repeat** INT pour répeter les actions à intervalles régulières. Par défaut l'intervalle est en seconde mais il est possible d'utiliser des clés de temps (m: minutes, h: heures, d: jours)
<br>
**--starter** HH:MM:SS pour démarrer la task à un moment précis (les secondes ne sont pas obligatoires)
<br>


### list

La commande permet d'afficher la liste des task et flow disponibles.

```console
flow list
```

### info

La commande permet d'afficher les détails sur une task ou un flow spécifique.

```console
flow info TASK_NAME
```

### details

La commande permet d'afficher les détails pour l'ensemble des task et flow disponibles.

```console
flow details
```

### fabric

La commande permet d'ouvrir le répertoire de script

```console
flow fabric
```

### tree:

La commande permet d'afficher l'arborescence du répertoire de script

```console
flow tree
```

### pull:

La commande permet de récupérer un fichier depuis le répertoire de script

```console
flow pull FILE_NAME
```

Il est possible de rajouter l'option **--output** pour préciser le chemin de sortie

### push:

La commande permet d'envoyer un fichier dans le répertoire de script

```console
flow push FILE_NAME
```

Il est possible de rajouter l'option **--folder** pour préciser le répertoire de destination

### pop:

La commande permet de supprimer un script du répertoire de script

```console
flow pop FILE_NAME
```
<br>

## Création de script

Pour être pris en compte par l'application, les scripts doivent une certaine syntaxe.
Chaque fonction est indépendante de base et doit avoir un décorateur @zpp_flow.task ou @zpp_flow.flow
Le décorateur peut contenir plusieurs paramètres comme **name** pour définir le nom de la task ou **order** pour définir l'ordre d'exécution.

```python
import zpp_flow

@zpp_flow.task
def hello_world():
	print("Bonjour je suis une task")
```

Dans une fonction, il est possible de définir des arguments qui pourront être utilisés dans le reste du flow

```python
from zpp_flow.core.runner import set_persist

set_persist(argument, value)
```