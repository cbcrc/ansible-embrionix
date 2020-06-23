# embrionix - playbooks emsfp

La série de playbooks **sfp-(...)** vise à configurer différents paramètres des modules sfp em22. Les playbooks ayant le préfix **sfp-csv-(...)** utilisent les valeurs provenant d'un csv. Les playbooks débutant seulement par **sfp-(...)** puisent les valeurs directement de l'inventaire.

## Comment débuter

Il faut d'abord déterminer si les valeurs à configurer proviendront d'un csv ou de l'inventaire. Dans le premier cas, le document **EmbrionixConfigurationCSV.xlsx** a été conçu pour aider à générer les csv de configuration. Il est hébergé sur gdrive avec accès restreint. Pour obtenir un accès, contacter [Alexandre Dugas](mailto:alexandre.dugas@radio-canada.ca).

## Utilisation

Tous les playbooks peuvent être exécutés avec la commande suivante:

`ansible-playbook [nom du playbook] -i inventaire/[chemin du fichier d'inventaire] -l [machine ou groupe cible]`

### Configuration des paramètres ipconfig:
* sfp-csv-ipconfig.yml
* sfp-ipconfig.yml

### Configuration du mapping des cannaux audio sur les decap:
* sfp-csv-sdi-audio-output.yml
* sfp-sdi-audio-output.yml

### Configuration du ptp
* sfp-ptp.yml

### Redémarrage du module ou réinitialisation des paramètres:
* sfp-csv-reset-configs.yml
* sfp-reset-configs.yml

### Enregistrement de la licence frame sync pour les encapsulateurs
* emsfp-register-frame_sync-licence.yml

Pour chacun des encodeurs sfp, un numéro de licence spécifique au module doit être assigné à la variable frame_sync_licence.

### Configuration des paramètres pour frame sync:
* sfp-frame-sync.yml

## Auteurs

* **[Alexandre Cormier](mailto:alexandre.cormier@radio-canada.ca)** - *Initial work* - ISTM - ASD
* **[Guillaume Lorrain-Bélanger](mailto:guillaume.lorrain-belanger@radio-canada.ca)** - *Initial work* - ISTM - ASD

## License

À déterminer.

## Remerciements
