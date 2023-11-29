########################################################################################################################
# IMPORTS ##############################################################################################################
########################################################################################################################
import configparser     # python config parser module
import requests         # human friendly http requests
import logging          # logger class

########################################################################################################################
# DEFINITIONS ##########################################################################################################
########################################################################################################################
restURL = 'https://api.gandi.net/v5/livedns/'           # the URL to the REST API of Gandi
configFileStructure = {'GANDI': ['key'],                # the expected structure for the gandiDynDNS.conf file
                       'DNS': ['domain', 'records']}

########################################################################################################################
# LOGGER ###############################################################################################################
########################################################################################################################
# create base logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create file handler
fh = logging.FileHandler('gandiDynDNS.log', mode='w')
fh.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# add formatter to fh
fh.setFormatter(formatter)

# add fh to logger
logger.addHandler(fh)

########################################################################################################################
# METHODS ##############################################################################################################
########################################################################################################################
def getPublicIP(ipv4 = True):
    try:
        # function to get an IPv4 or IPv6 address
        ipType = '' if ipv4 else '64'
        strIPType = 'v4' if ipv4 else 'v6'

        # get the ip from ipify as json
        ip = requests.get(f'https://api{ipType}.ipify.org?format=json')
        ip.raise_for_status()

        if not ip.status_code == 200:
            # unable to retrieve the ip, exit with an error message
            logger.error('Critical Error: Unable to get public IP!')
            logger.error(f'Status Code: {ip.status_code}')
            exit(1)

        # log message and return ip
        ip = ip.json()['ip']
        logger.info(f'Public IP{strIPType}: {ip}')
        return ip

    except Exception as e:
        logger.error(f'Critical Error: Unable to get public IP{strIPType} address')
        logger.error(f'Error Message: {e}')
        exit(1)

def getPublicIPs():
    try:
        # function retrieve the public IPv4 addresses of the server from the ipify API
        ip4 = getPublicIP(ipv4=True)
        ip6 = getPublicIP(ipv4=False)

        # return the IP addresses
        return ip4, ip6

    except Exception as e:
        logger.error('Critical Error: Unable to get public IP addresses')
        logger.error(f'Error Message: {e}')
        exit(1)

def getGandiRecord(domain, name, dnsType, header):
    try:
        # function to get the domain record of the specified type and name
        result = requests.get(restURL + f'domains/{domain}/records/{name}/{dnsType}', headers=header)
        result.raise_for_status()

        if not result.status_code == 200:
            # the domain records could not be retrieved from the server, exit with an error message
            logger.error(f'Critical Error: Unable to retrieve the {dnsType} record for {name}@{domain} from Gandi!')
            logger.error(f'Status Code: {result.status_code}')
            exit(1)

        return result.json()['rrset_values']

    except Exception as e:
        logger.error('Critical Error: Unable to get the domain records from Gandi!')
        logger.error(f'Error Message: {e}')
        exit(1)

def updateGandiRecord(domain, name, dnsType, newIP, header):
    # function to update a DNS record
    try:
        # create payload and set PUT request
        payload = {'rrset_ttl': 1800, 'rrset_values': [newIP]}
        result = requests.put(restURL + f'domains/{domain}/records/{name}/{dnsType}', json=payload, headers=header)
        changed = True

        # raise for status
        if not result.status_code == 201:
            changed = False
            logger.warning(f'{dnsType} -> {name}@{domain}: {result.status_code}')

        return changed

    except Exception as e:
        logger.error(f'Critical Error: Unable to update {dnsType} record of {name}.{domain}!')
        logger.error(f'Error Message: {e}')
        exit(1)

########################################################################################################################
# SCRIPT ###############################################################################################################
########################################################################################################################
def main():
    # main script
    try:
        # READ AND PARSE THE CONFIG FILE ###############################################################################
        config = configparser.ConfigParser()
        config.read('.gandi.conf')

        # check for a valid file
        for section, parameters in configFileStructure.items():
            # for each section, parameters pair
            if section not in config.sections():
                # if the section is not found in the supplied configuration file -> exit with an error message
                logger.error(f'Invalid Configuration File! Please provide a [{section}] section!')
                exit(1)

            # the section exists -> check if the desired parameters are set
            for parameter in parameters:
                if parameter not in config[section].keys():
                    # if the parameter was not set, exit with an error message
                    logger.error(f'Invalid Configuration File! Please provide a {parameter} parameter!')
                    exit(1)

        # the configuration file is valid, get the API key, as well as the desired domain and subdomains
        key = config['GANDI']['key']
        domain = config['DNS']['domain']
        records = config['DNS']['records'].split('\n')

        # print starting message
        logger.info(f'Updating the records of {domain} ...')

        # HTTPS AUTHORIZATION ##########################################################################################
        header = {'Authorization': f'Apikey {key}'}

        # GET PUBLIC IP ADDRESS ########################################################################################
        ipv4, ipv6 = getPublicIPs()

        # UPDATE A and AAAA RECORDS ####################################################################################
        nChanged = 0
        for i, record in enumerate(records):
            # for each record that should be updated
            logger.info(f'\tUpdating the entries of {record}@{domain} ...')
            gandiIPv4 = getGandiRecord(domain=domain, name=record, dnsType='A', header=header)
            gandiIPv6 = getGandiRecord(domain=domain, name=record, dnsType='AAAA', header=header)

            if len(gandiIPv6) == 0 and len(gandiIPv4) == 0:
                # if the record does not exist in the domain, print a warning and continue
                logger.warning(f'Warning! The record {record} does not exist, and can thus not be updated!')
                continue

            # check for IP change and update if necessary
            if ipv4 != gandiIPv4[0]:
                if updateGandiRecord(domain=domain, name=record, dnsType='A', newIP=ipv4, header=header):
                    nChanged += 1
            if ipv6 != gandiIPv6[0]:
                if updateGandiRecord(domain=domain, name=record, dnsType='AAAA', newIP=ipv6, header=header):
                    nChanged += 1

        # exit with success
        logger.info(f'Success! {nChanged} DNS records were changed.')
        exit(0)

    except Exception as e:
        # on any exception, print an error message and exit
        logger.error(f'Critical Error: {e}')
        exit(1)

# run main
if __name__ == '__main__':
    main()
