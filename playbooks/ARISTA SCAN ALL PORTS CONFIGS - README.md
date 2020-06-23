# embrionix - Arista scan all ports configs

Ce playbook sert à faire un scan des ports ethernet d'une switch arista.
Configuration des adresses réseaux des cartes Embrionix par I2C. (Adresse IP, le masque réseau et la passerelle par défault).

Pour ce faire, on établit une connection ssh avec la switch arista dans laquelle se trouvent les devices emsfp d'embrionix via le module ansible eos_command pour ensuite configure la MAC, l'adresse IP, le masque reseau et la passerelle réseau.

Une fois que le tout a été lu, on affiche toutes les configurations associées par port ethernet dans l'ordre.

## Utilisation

Le playbook peut être exécuté avec la commande suivante:

`ansible-playbook [nom du playbook] -i inventaire/[chemin du fichier d'inventaire] -l [machine ou groupe cible] -v`

### Configuration des paramètres du playbook

- arista-scan-all-ports-configs.yml

## Auteurs

* **[Alexandre Cormier](mailto:alexandre.cormier@radio-canada.ca)** - *IDéveloppement ultérieur* - ISTM - ASD
* **[Guillaume Lorrain-Bélanger](mailto:guillaume.lorrain-belanger@radio-canada.ca)** - *Développement ultérieur* - ISTM - ASD

## License

À déterminer.

## Remerciements
