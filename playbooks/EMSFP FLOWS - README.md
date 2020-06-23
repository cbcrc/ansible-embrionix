# embrionix - emsfp flows

Le playbook emsfp put flow vise à pousser les configurations de flows des modules emsfp. Le playbook utilise les valeurs provenant d'un csv.

Ce playbook est légerement différent des playbook **sfp-(...)** en quelques points :

- Il y a une validation de trois champs mandatoires, soit "Target" (Adresse IP du module emsfp), "Flow" (Flow ID du flow) et "FlowType" (enc_video, enc_audio, enc_ancillary, dec_video, dec_audio, dec_ancillary).

- Il s'adresse aux modules de type Encapsulateur et Decapsulateur. Pour ces deux types de modules, les valeurs assignées au flow dans le csv doivent correspondre soit à un flow video, audio ou ancilliary.

- Une adresse MAC est générée à partir de l'adresse IP "dst_ip_addr" selon un script fourni par emsfp. Cette valeur est assignée au champs dst_mac du payload envoyé au module.

## Comment débuter

Il faut d'abord déterminer si les valeurs à configurer proviendront d'un csv ou de l'inventaire. Dans le premier cas, le document **emsfpConfigurationCSV.xlsx** a été conçu pour aider à générer les csv de configuration. Il est hébergé sur gdrive avec accès restreint. Pour obtenir un accès, contacter [Alexandre Dugars](mailto:alexandre.dugas@radio-canada.ca).

## Utilisation

Le playbook peut être exécuté avec la commande suivante:

`ansible-playbook [nom du playbook] -i inventaire/[chemin du fichier d'inventaire] -l [machine ou groupe cible] -v`

### Configuration des paramètres du playbook

- emsfp-csv-flows.yml (Si un csv est utilisé pour fournir les informations d'entrée.)
- emsfp-flow.yml (Si un yaml est utilisé pour fournir les informations d'entrée.)

## Auteurs

- **[Alexandre Cormier](mailto:alexandre.cormier@radio-canada.ca)** - *Initial work* - ISTM - ASD
- **[Guillaume Lorrain-Bélanger](mailto:guillaume.lorrain-belanger@radio-canada.ca)** - *Initial work* - ISTM - ASD

## License

À déterminer - see the [LICENSE.md](LICENSE.md) file for details

## Remerciements
