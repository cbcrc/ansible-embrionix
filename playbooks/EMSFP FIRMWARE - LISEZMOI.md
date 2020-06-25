# embrionix - emsfp firmware

Le playbook emsfp firmware vise à copier les configurations du module emsfp, uploader un firmware vers un module emsfp dans une slot disponible, le rendre actif, le configurer en mode défaut, faire un reset config au niveau application et ensuite repousser les configurations du module emsfp.

## Comment débuter

Configurer la slot vers laquelle le playbook va téléverser le firmware désiré. Mettre le firmware sous "./embrionix/firmwares/". Mettre le chemin du firmware dans la variable "module_enc_firmware_filepath" ou "module_dec_firmware_filepath" dépendamment du type de module auquel s'adresse le firmware. À noter que le nom du fichier de firmware doit contenir les lettres "ENC" ou "DEC" afin d'identifier à quel type de module il s'adresse. Lancer l'exécution du module sur l'inventaire désiré ou filtrer sur un groupe de module d'un inventaire.

## Utilisation

Le playbook peut être exécuté avec la commande suivante:

`ansible-playbook [nom du playbook] -i inventaire/[chemin du fichier d'inventaire] -l [machine ou groupe cible] -v`

### Configuration des paramètres du playbook

* emsfp-firmware-upload.yml

### Configuration des variables

Les variables utilisées par le firmware sont puisées sois de ./common_vars/ ou soit de l'inventaire (group_vars ou hosts_vars) si l'on désirer tester un nouveau firmware sans le rendre disponible pour l'ensemble des modules.

* module_firmware_slot
* module_enc_firmware_filepath
* module_dec_firmware_filepath

## Auteurs

* **[Alexandre Cormier](mailto:alexandre.cormier@radio-canada.ca)** - *Initial work* - ISTM - ASD
* **[Guillaume Lorrain-Bélanger](mailto:guillaume.lorrain-belanger@radio-canada.ca)** - *Initial work* - ISTM - ASD

## License

À déterminer - see the [LICENSE.md](LICENSE.md) file for details

## Remerciements
