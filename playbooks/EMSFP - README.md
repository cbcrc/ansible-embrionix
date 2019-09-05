# embrionix - playbooks emsfp

La série de playbooks **sfp-(...)** vise à configurer différents paramètres des modules sfp em22. Les playbooks ayant le préfix **sfp-csv-(...)** utilisent les valeurs provenant d'un csv. Les playbooks débutants seulement par **sfp-(...)** puisent les valeurs directement de l'inventaire.

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

Pour chacun des encapsulateurs sfp, un numéro de licence spécifique au module doit être assigné à la variable frame_sync_licence.
  
### Configuration des paramètres pour frame sync:
* sfp-frame-sync.yml

### Enregistrer la configuration d'un module dans l'inventaire
* emsfp-save-config.yml

## License

GNU General Public License v3.0+ (see the [LICENSE](../LICENSE) file for details)
