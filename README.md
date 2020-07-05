# digitalocean_ddns

![Docker Image CI](https://github.com/bjmd/digitalocean_ddns/workflows/Docker%20Image%20CI/badge.svg)

A DigitalOcean ddns client, inspired by https://github.com/satyamkapoor/homeIPv4DynamicUpdateDNS. 

The above project was the basis for this one, but expanded on to add use of a config file add some additional functionality. 

# Prerequisite

You must have a hostname added to DigitalOcean already. This script will only update, it will not create a new record for you.

The DNS entry you are trying to update needs to be a A record and not a CNAME. 

# How to run

You can run the file 'app.py' using Python 3. On first run it will prompt for your Digital Ocean API key, the domin you wish to update and the hostname within the domain.

If you wish to store the config file in a seperate location, you can run:

 `python3 app.py -c [Config Location]`
