# digitalocean_ddns

![Docker Image CI](https://github.com/bjmd/digitalocean_ddns/workflows/Docker%20Image%20CI/badge.svg)

A DigitalOcean dynamic dns client, inspired by https://github.com/satyamkapoor/homeIPv4DynamicUpdateDNS. 

The above project was the basis for this one, but I expanded on to add the option of a config file and to dockerise the app. 

# Prerequisite

You must have a hostname added to DigitalOcean already. This script will only update, it will not create a new record for you.

The DNS entry you are trying to update needs to be a A record and not a CNAME. 

# How to run

The app runs as a docker container with two options. Either mapping a directory containing a config file or passing environment variables at run time. 

Example with config mapping:

    docker create \
        --name digitalocean_ddns
        -v /path/to/config/:/config/
        bjmd/digitalocean_ddns:latest

Example passing environment variables:

    docker create \
        --name digitalocean_ddns
        -e API_KEY=00000000
        -e DOMAIN=example.com
        -e HOSTNAME=myhost.example.com
        bjmd/digitalocean_ddns:latest


If you map in a directory containing a config file, the file must be named `config.yaml`. 

An example file can be found in the repo.

*Note: environment variables and config file entries are **case sensitive***


This container does not run continuously. To enable periodic updating on Linux you will need to run it as a cronjob. An example cron entry to run every 6 hours:

`0 */6 * * * docker start digitalocean_ddns`

You can then view the logs for the last run with:

`docker logs digitalocean_ddns`

Finally, if you have a need to update to a newer build of the container then assuming the same name was used above you can use the following commands:

    docker pull bjmd/digitalocean_ddns:latest && docker rm digitalocean_ddns

Then re-create using your chosed method above. 