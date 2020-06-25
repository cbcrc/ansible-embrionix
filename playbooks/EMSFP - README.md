# Ansible Playbooks for Embrionix Devices

The **emsfp-(...)** playbooks is used to configure Embrionix st2110 modules. The **embox-(...)** playbooks as their name implies are used to configure Embrionix embox devices. Playbooks containing **(...)-csv-(...)** use values provided by a csv. Other playbooks use values from the Ansible inventory.

## How to begin

1. Determine if the configuration values will be provided by a csv or from the Ansible inventory.
2. If from a csv, the document **EmbrionixConfigurationCSV.xlsx** was created to generate configuration csv. It's hosted on a gdrive with restricted access. Contact [Alexandre Dugas](mailto:alexandre.dugas@radio-canada.ca) for more information.
3. The playbooks listed here can then be used to configure de devices.

## Usage

All the playbooks can be executed with this command in cli:

`ansible-playbook [playbook name] -i inventory/[path to hosts file] -l [device name or device group] --ask-vault-pass`

--ask-vault-pass option can be ommited if a password file is used. See Ansible docummentation: [Running a Playbook With Vault](https://docs.ansible.com/ansible/latest/user_guide/playbooks_vault.html#running-a-playbook-with-vault).

## Playbooks

### General configuration

##### Download device configuration
* emsfp-config-download-v2.yml

##### Configure device with Ansible inventory values
* emsfp-config-upload-v2.yml

##### Reboot device or reset to factory default
* emsfp-csv-reset-configs.yml
* emsfp-reset-configs.yml
* emsfp-reset-flows.yml

##### Sanity check
* emsfp-nanity-check.yml

### Specific Configuration

##### flows configuration
* emsfp-csv-flows.yml
* emsfp-flows.csv.yml
* embox-csv-flows.yml

##### ip parameters configuration
* emsfp-csv-ipconfig.yml
* emsfp-ipconfig.yml
* embox-csv-ipconfig.yml
* embox-ipconfig.yml

##### Audio mapping configuration
* emsfp-csv-sdi-audio-output.yml
* emsfp-sdi-audio-output.yml
* embox-csv-sdi-audio-mapping.yml
* embox-sdi-audio-mapping.yml

##### ptp configuration
* emsfp-csv-ptp.yml
* emsfp-ptp.yml
* embox-csv-refclk.yml
* embox-refclk.yml

##### st2110 devices smbus staging
* emsfp-csv-staging.yml
* emsfp-csv-staging-avec-hostname.yml

##### st2110 encap devices framesync licence registering
* emsfp-register-frame_sync-licence.yml

##### Framesync parameters configuration
* emsfp-frame-sync.yml

### Ansible Inventory Management

##### "last-good-configuration" file creation
* emsfp-save-last-good-config.yml (désuet)
* emsfp-save-last-good-config-v2.yml

##### host_vars file update
* emsfp_maj-host_vars.yml
* emsfp-save-config.yml (désuet)
* emsfp-save-downloaded-config-v2.yml (désuet)
* emsfp-saveuploaded-config.yml (désuet)

## Authors

* **[Alexandre Cormier](mailto:alexandre.cormier@radio-canada.ca)** - *Initial work* - ISTM - Applications Média
* **[Guillaume Lorrain-Bélanger](mailto:guillaume.lorrain-belanger@radio-canada.ca)** - *Initial work* - ISTM - Applications Média
* **[Emanuel Mateus](mailto:emanuel.mateus@cbc.ca)** - *Initial work* - ISTM - Applications Média

## License

#### Copyright: (c) 2018, Société Radio-Canada>
#### GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)