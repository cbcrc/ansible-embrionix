# embrionix - EMSFP-STAGING

Configuration des adresses réseaux des cartes Embrionix par I2C. (adresse IP, le masque réseau et la passerelle par défault).

Pour ce faire, on établit une connection ssh avec la switch arista dans laquelle se trouvent les devices emsfp d'embrionix via le module ansible eos_command pour ensuite configurer le module via I2c sur le smbus corresondant.

Dependamment de ce qui est fourni dans le csv, la configuration peut être envoyée au port Ethernet spécifié ou au module emsfp d'embrionix qui possède la mac adresse spécifié et ce peut importe le port ethernet dans lequel le module ce trouve.

## Comment débuter

Un fichier csv doit être constitué de la façon suivante pour programmer les modules:

Contenue du csv pour la procédure par MAC_Address:

`port_number, mac_address, ip_addr, gateway, Subnet_mask`

Contenue du csv pour la procédure par Port Ethernet:

`port_number, , ip_addr, gateway, Subnet_mask`

Dans le premier cas, la mac adresse inscrite dans la deuxième position de la ligne sera recherché parmis les modules qui se trouve dans la switch.

Dans le dernier cas, le playbook trouvera les modules selon le numéro de port au lieu de l'adresse MAC. Il laisser un emplacement vide pour l'adresse mac.
Le fichier ne doit pas comporter plus d'entrées que le nombre de module pouvant être programmé à la fois sur la switch.

## Utilisation

Le playbook peut être exécuté avec la commande suivante:

`ansible-playbook [nom du playbook] -i inventaire/[chemin du fichier d'inventaire] -l [machine ou groupe cible] -v`

### Configuration des paramètres du playbook

- emsfp-csv-staging.yml
- emsfp-csv-staging-avec-hostname.yml (Appel du playbook emsfp-csv-staging ensuite configuration du hostname par l'API du module emsfp d'embrionix.)

## Auteurs

* **[Emanuel Mateus](mailto:emanuel.mateus@cbc.ca)** - *Initial work* - ISTM - ASD
* **[Alexandre Cormier](mailto:alexandre.cormier@radio-canada.ca)** - *IDéveloppement ultérieur* - ISTM - ASD
* **[Guillaume Lorrain-Bélanger](mailto:guillaume.lorrain-belanger@radio-canada.ca)** - *Développement ultérieur* - ISTM - ASD
  
## License

À déterminer - see the [LICENSE.md](LICENSE.md) file for details

## Remerciements
