# EMBRIONIX - EMSFP config download

Le playbook sfp config download vise à télécharger les configurations d'un module emsfp dans un fichier yaml .

## Comment débuter

Lancer l'exécution du module sur l'inventaire désiré ou filrer sur un groupe de module d'un inventaire.

## Utilisation

Le playbook peut être exécuté avec la commande suivante:

`ansible-playbook [nom du playbook] -i inventaire/[chemin du fichier d'inventaire] -l [machine ou groupe cible] -v`

### Configuration des paramètres du playbook

* emsfp-config-download.yml

### Configuration des routes de l'api qui sont lu sur les modules emsfp

Liste des routes de configuration régulière :

All device type :

* /emsfp/node/v1/self/ipconfig/
* /emsfp/node/v1/refclk/

Liste des routes de configuration basé sur ID :

Appliquable à tous les types de module :

* /emsfp/node/v1/flows/

Spécifique aux Encapsulateurs :

* /emsfp/node/v1/sdi_input/

Spécifique aux Decapsulateurs :

* /emsfp/node/v1/sdi_audio/
* /emsfp/node/v1/sdi_output/

Liste des routes de configuration basé sur ID dans un parametre spécifique:

* /emsfp/node/v1/refclk/ sous le parametre UUID

### Destination du fichier YAML

Le fichier est créé dans le répertoire ./vars/ et la nomenclature est "value_read_from_module_XXX.XXX.XXX.XXX". Les X réprésentent l'adresse IP du module.

## Auteurs

* **[Alexandre Cormier](mailto:alexandre.cormier@radio-canada.ca)** - *Initial work* - ISTM - ASD
* **[Guillaume Lorrain-Bélanger](mailto:guillaume.lorrain-belanger@radio-canada.ca)** - *Initial work* - ISTM - ASD

## License


#### Copyright: (c) 2018, Société Radio-Canada>
#### GNU General Public License v3.0+

Voir le fichier [LICENSE.md](LICENSE.md) pour les détails.

## Remerciements
