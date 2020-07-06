import subprocess
import requests
import shlex
import yaml
import os
import sys

def getExternalCurrentIP():

    # Get current external IP. Check DNS instead of a web service for reliability. 
    cmd='dig @resolver1.opendns.com ANY -4 myip.opendns.com +short'
    proc=subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE)
    out,err=proc.communicate()
    currentIPv4 = out.decode('UTF-8').strip('\n')
    return currentIPv4

def updateIP(currentExternalIP, api_key, tld, update_domain):
    
    headers = {'Content-Type':'application/json','Authorization': 'Bearer ' + api_key}
    get_url = "https://api.digitalocean.com/v2/domains/{}/records?name={}".format(tld, update_domain)
    try:
        r = requests.get(get_url, headers=headers, timeout=5)
    except TimeoutError as err:
        print("Timed out accessing DigitalOcean")
        print(err)
        sys.exit(1)

    if r.status_code == 200:
        try:
            content = r.json()
            if content['meta']['total'] == 0:
                print("No current DNS entry found. Add a manual A record and then retry")
                sys.exit(1)
            elif content['meta']['total'] > 1:
                print("Returned more than 1 IP for current hostname. Exiting as assume something is wrong.")
                sys.exit(1)
            else:
                record_id = content['domain_records'][0]['id']
                current_DNS_IP = content['domain_records'][0]['data']
                if content['domain_records'][0]['type'] == 'CNAME':
                    print("Current DNS record is set as a CNAME but we cannot change record type.\n\nPlease delete the record and retry.")
                    sys.exit(1)

        except ValueError as err:
            print("Unknown content returned when looking up existing IP")
            print(err)
            sys.exit(1)

    else:
        print("Failed to get current ip: ", r.reason)
        print(r.text)
        sys.exit(1)
        
    if currentExternalIP == current_DNS_IP:
        # Current IP matches DNS IP
        sys.exit(0)

    else:
        put_url = "https://api.digitalocean.com/v2/domains/{}/records/{}".format(tld, record_id)
        payload = {"data": currentExternalIP}
        r = requests.put(put_url, headers=headers, json = payload)
        print(r.text, r.status_code)

def main():

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
        
    if os.getenv("UPDATE_DOMAIN"):
        update_domain = os.environ['UPDATE_DOMAIN']
    else:
        print("UPDATE_DOMAIN environment is not set.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-c",
                        required=False,
                        help="Specify alternate config location",
                        action="store",
                        dest="config",
                        default=None
                        )
    ap_parsed = parser.parse_args()
    
    if ap_parsed.config:
        config_file = ap_parsed.config
    else:
        config_file = "config.yaml"

    currentExternalIP = getExternalCurrentIP()
    updateIP(currentExternalIP, api_key, tld, update_domain)

if __name__ == "__main__":
    main()
