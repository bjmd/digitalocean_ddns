import subprocess
import requests
import shlex
import yaml
import os
import sys
import socket
from datetime import datetime
import dns.resolver

def configParse(config_file):

    api_key = None
    tld = None
    update_domain = None
    
    with open(config_file, 'r') as file:
        config = yaml.full_load(file)

    for key,value in config.items():
        if key == "API_KEY":
            api_key = value
        if key == "DOMAIN":
            tld = value
        if key == "FQDN":
            update_domain = value
    # Validate that we find an API key, tld and domain name
    if api_key is None or tld is None or update_domain is None:
        log("Config invalid. Correct the config or pass options as variables.")
        sys.exit(1)

    return(api_key, tld, update_domain)

def log(message):
    print("{} {}".format(datetime.now(), message))

def getExternalCurrentIP():

    domain = 'myip.opendns.com'

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['208.67.222.222', '208.67.220.220'] # opendns nameservers
    answer = resolver.query(domain)

    current_ip = str(answer[0])

    try:
        # Validate IP with builtin 
        socket.inet_aton(current_ip)
    except OSError:
        log("Unable to lookup current external IP. Answer returned {}".format(current_ip))
        sys.exit(1)

    return current_ip

def updateIP(currentExternalIP, api_key, tld, update_domain):
    
    headers = {'Content-Type':'application/json','Authorization': 'Bearer ' + api_key}
    get_url = "https://api.digitalocean.com/v2/domains/{}/records?name={}".format(tld, update_domain)
    try:
        r = requests.get(get_url, headers=headers, timeout=5)
    except TimeoutError as err:
        log("Timed out accessing DigitalOcean")
        print(err)
        sys.exit(1)

    if r.status_code == 200:
        try:
            content = r.json()
            if content['meta']['total'] == 0:
                log("No current DNS entry found for {}. Add a manual A record and then retry".format(update_domain))
                sys.exit(1)
            elif content['meta']['total'] > 1:
                log("Returned more than 1 IP for current hostname. Exiting as assume something is wrong.")
                sys.exit(1)
            else:
                record_id = content['domain_records'][0]['id']
                current_DNS_IP = content['domain_records'][0]['data']
                if content['domain_records'][0]['type'] == 'CNAME':
                    log("\nCurrent DNS record is set as a CNAME but we cannot change record type.\n\nPlease delete the record and retry.")
                    sys.exit(1)

        except ValueError as err:
            log("Unknown content returned when looking up existing IP")
            print(err)
            sys.exit(1)

    else:
        log("Failed to get current ip: {}".format(r.reason))
        print(r.text)
        sys.exit(1)
        
    if currentExternalIP == current_DNS_IP:
        # Current IP matches DNS IP
        log("No change in IP found.")
        sys.exit(0)

    else:
        put_url = "https://api.digitalocean.com/v2/domains/{}/records/{}".format(tld, record_id)
        payload = {"data": currentExternalIP}
        r = requests.put(put_url, headers=headers, json = payload)
        log("{} {}".format(r.text, r.status_code))

def main():

    config_file='/config/config.yaml'
    
    if not os.path.exists(config_file):

        if os.getenv("API_KEY"):
            api_key = os.environ['API_KEY']
        else:
            print("API_KEY environment is not set.")
            sys.exit(1)
            
        if os.getenv("DOMAIN"):
            tld = os.environ['DOMAIN']
        else:
            print("DOMAIN environment is not set.")
            sys.exit(1)
            
        if os.getenv("FQDN"):
            update_domain = os.environ['FQDN']
        else:
            print("FQDN environment is not set.")
            sys.exit(1)

    else:
        api_key, tld, update_domain = configParse(config_file)

    currentExternalIP = getExternalCurrentIP()
    updateIP(currentExternalIP, api_key, tld, update_domain)

if __name__ == "__main__":
    main()
