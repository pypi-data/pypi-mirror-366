import socket
import logging
log = logging.getLogger()

def add_host_alias(app, host, domain, hosts_file='/etc/hosts'):
    ip = socket.gethostbyname(host)
    with open(hosts_file, "a") as hosts:
        log.info("adding hosts: {0} {1}".format(ip, domain))
        hosts.write("{0} {1}\n".format(ip, domain))
        log.info("adding hosts: {0} {1}.{2}".format(ip, app, domain))
        hosts.write("{0} {1}.{2}\n".format(ip, app, domain))
        log.info("adding hosts: {0} auth.{1}".format(ip, domain))
        hosts.write("{0} auth.{1}\n".format(ip, domain))
