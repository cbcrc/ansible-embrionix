# Playbooks Ansible pour modules Embrionix

La série de playbooks **emsfp-(...)** vise à configurer différents paramètres des modules Embrionix st2110. La série de playbooks **embox-(...)** s'applique comme le préfix l'indique aux embox. Les playbooks contenant **(...)-csv-(...)** utilisent les valeurs provenant d'un csv. Les autres puisent les valeurs directement de l'inventaire Ansible.

## Comment débuter

Il faut d'abord déterminer si les valeurs à configurer proviendront d'un csv ou de l'inventaire. Dans le premier cas, le document **EmbrionixConfigurationCSV.xlsx** a été conçu pour aider à générer les csv de configuration. Il est hébergé sur gdrive avec accès restreint. Pour obtenir un accès, contacter [Alexandre Dugas](mailto:alexandre.dugas@radio-canada.ca).

## Utilisation

Tous les playbooks peuvent être exécutés avec la commande suivante:

`ansible-playbook [nom du playbook] -i inventaire/[chemin du fichier d'inventaire] -l [machine ou groupe cible] --ask-vault-pass`

L'option --ask-vault-pass peut être omise en utilisant un fichier de mot de passe. Voir [Running a Playbook With Vault](https://docs.ansible.com/ansible/latest/user_guide/playbooks_vault.html#running-a-playbook-with-vault).

## Configuration générale

##### Télécharger les configurations d'un module
* emsfp-config-download-v2.yml

##### Configuration des paramètres d'un module à partir des valeurs de l'inventaire
* emsfp-config-upload-v2.yml

##### Redémarrage du module ou réinitialisation des paramètres:
* emsfp-csv-reset-configs.yml
* emsfp-reset-configs.yml
* emsfp-reset-flows.yml

##### Sanity check
* emsfp-nanity-check.yml

## Configuration spécifique

##### Configuration des flows
* emsfp-csv-flows.yml
* emsfp-flows.csv.yml
* embox-csv-flows.yml

##### Configuration des paramètres ipconfig:
* emsfp-csv-ipconfig.yml
* emsfp-ipconfig.yml
* embox-csv-ipconfig.yml
* embox-ipconfig.yml

##### Configuration du mapping des cannaux audio sur les decap:
* emsfp-csv-sdi-audio-output.yml
* emsfp-sdi-audio-output.yml
* embox-csv-sdi-audio-mapping.yml
* embox-sdi-audio-mapping.yml

##### Configuration du ptp
* emsfp-csv-ptp.yml
* emsfp-ptp.yml
* embox-csv-refclk.yml
* embox-refclk.yml

##### "Staging" par smbus les modules st2110
* emsfp-csv-staging.yml
* emsfp-csv-staging-avec-hostname.yml

##### Enregistrement de la licence frame sync pour les encapsulateurs
* emsfp-register-frame_sync-licence.yml

##### Configuration des paramètres pour frame sync:
* emsfp-frame-sync.yml

Pour chacun des encodeurs st2110, un numéro de licence spécifique au module doit être assigné à la variable frame_sync_licence.

## Gestion de l'inventaire Ansible

##### Créer le fichier "last-good-configuration"
* emsfp-save-last-good-config.yml (désuet)
* emsfp-save-last-good-config-v2.yml

##### Mise à jour des fichiers sous host_vars
* emsfp_maj-host_vars.yml
* emsfp-save-config.yml (désuet)
* emsfp-save-downloaded-config-v2.yml (désuet)
* emsfp-saveuploaded-config.yml (désuet)

## Auteurs

* **[Alexandre Cormier](mailto:alexandre.cormier@radio-canada.ca)** - *Initial work* - ISTM - Applications Média
* **[Guillaume Lorrain-Bélanger](mailto:guillaume.lorrain-belanger@radio-canada.ca)** - *Initial work* - ISTM - Applications Média
* **[Emanuel Mateus](mailto:emanuel.mateus@cbc.ca)** - *Initial work* - ISTM - Applications Média

## License

#### Copyright: (c) 2018, Société Radio-Canada>
#### GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)