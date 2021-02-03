import json
import ipaddress
import multiprocessing.dummy
import multiprocessing
import subprocess

from mynetbox import mynetbox

def load_config():
    for location in os.curdir, os.path.expanduser("~/.netbox_importer"), "/etc/netbox_importer":
        try:
            with open(os.path.join(location, "config.yaml")) as source:
                config = yaml.safe_load(source)
        except IOError:
            pass

    missing_config = [ x for x in config["api"] if x not in ['hostname', 'api_token'] ]
    if len(missing_config) > 0:
        print("Missing the following configuration options: {}".format(", ".join(missing_config)))
        sys.exit(1)

    config = (config["api"]["api_token"], config["api"]["hostname"])

    return config

netbox = mynetbox(
        host='https://netbox.apps.aks-adfch-k8s-int-test-02.cloud.adfinis.com',
        token='b1ab94731121a89b7056edd133923d94aa1f7c77'
)


def get_hosts(network):
    ip_network = ipaddress.ip_network(u"{}".format(network))
    return list(ip_network.hosts())

def ping(ip):
    if ip.version == 4:
        ping_cmd = "ping"
    elif ip.version == 6:
        ping_cmd = "ping"
        #ping_cmd = "ping6"

    result=subprocess.Popen([ping_cmd, "-q", "-c", "2", "-n", "-W", "3",
        str(ip)], stdout=subprocess.PIPE).wait()
    if not result:
        #print(ip, "active, checking netbox")
        netbox.active_ip(f"{ip}/32")
    if result:
        #print(ip, "inactive, checking netbox")
        netbox.inactive_ip(f"{ip}/32")


def ping_network(network):
    num_threads = 4 * multiprocessing.cpu_count()
    p = multiprocessing.dummy.Pool(num_threads)
    p.map(ping, get_hosts(network))

def main():

    prefixes = [prefix['prefix'] for prefix in netbox.get_scan_prefixes()]

    for prefix in prefixes:
        print(f"Starting to ping {prefix}")
        ping_network(prefix)


if __name__ == "__main__":
    main()

