# EMBRIONIX - EMSFP UPLOAD CONFIG

Le playbook sfp config upload vise à téléverser les configurations d'un module emsfp qui sont dans un fichier yaml vers le module correspondant. Seule les configurations qui sont différentes seront envoyé à l'API du module pour modification.

## Comment débuter

Lancer l'exécution du module sur l'inventaire désiré ou filrer sur un groupe de module d'un inventaire.

## Utilisation

Le playbook peut être exécuté avec la commande suivante:

`ansible-playbook [nom du playbook] -i inventaire/[chemin du fichier d'inventaire] -l [machine ou groupe cible] -v`

### Configuration des paramètres du playbook

* emsfp-config-upload.yml

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

### Source du fichier YAML

Le fichier est pris dans le répertoire ./vars/ et la nomenclature recherchée est  "value_read_from_module_XXX.XXX.XXX.XXX". Les X réprésentent l'adresse IP du module.

## Auteurs

* **[Alexandre Cormier](mailto:alexandre.cormier@radio-canada.ca)** - *Initial work* - ISTM - ASD
* **[Guillaume Lorrain-Bélanger](mailto:guillaume.lorrain-belanger@radio-canada.ca)** - *Initial work* - ISTM - ASD

## License

À déterminer - see the [LICENSE.md](LICENSE.md) file for details

## Remerciements
