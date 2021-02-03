import socket
import pynetbox


class mynetbox:
    def __init__(self, host='127.0.0.1', token='1234'):
        self.netbox = pynetbox.api(host, token=token)

    def get_active_prefixes(self):

        return self.netbox.ipam.prefixes.filter(status='active')

    def get_scan_prefixes(self):

        return self.netbox.ipam.prefixes.filter(status='active', tag=['scan'])

    def add_inactive_tag(self, address):
        """
        This function gets executed if the IP address is available in netbox
        but is not reachable anymore.
        """

        item = self.netbox.ipam.ip_addresses.get(address=address)
        tag = self.netbox.extras.tags.get(name="scan-inactive")

        item.tags.append(tag)
        item.save()

    def get_dnsname(self, address):

        try:
            dnsname = socket.gethostbyaddr(address.split('/')[0])[0]
        except socket.herror:
            return False
        except:
            print(f"Unknown error: {address}")
            return False

        return dnsname

    def update_dns_name(self, address):
        dnsname = self.get_dnsname(address)
        item = self.netbox.ipam.ip_addresses.get(address=address)

        if dnsname:
            if item.dns_name != dnsname:
                print(f"Updating DNS of host address:    {address}")
                item.dns_name = dnsname
                item.tags.append(self.netbox.extras.tags.get(name="scan-dnsupdate"))

        if not item.dns_name:
            item.tags.append(self.netbox.extras.tags.get(name="no-reverse-dns"))
        else:
            item.tags = [tag for tag in item.tags if not tag['name'] == 'no-reverse-dns']

        item.save()


    def create_active_ipaddress(self, address):

        hostobj = {
            "address": address,
            "tags": [{
                "name": "scan-active"
            }]
        }

        dnsname = self.get_dnsname(address)

        if dnsname:
            hostobj.update(dns_name=dnsname)

        self.netbox.ipam.ip_addresses.create([hostobj])

    def check_ipaddress(self, address):
        """
        This function is used to check if an ipadress is already added to Netbox.
        Returns true if ip address exists.
        Returns false if ip address doesn't exsist.
        """

        if self.netbox.ipam.ip_addresses.get(address=address):
            return True
        else:
            return False


    def active_ip(self, address):
        """
        Checks if the ip is in netbox, if true, do nothing
        If the IP is not in netdot, create it
        """

        if not self.check_ipaddress(address):
            print(f"Creating new host with address:  {address}")
            self.create_active_ipaddress(address)
        else:
            self.update_dns_name(address)

    def inactive_ip(self, address):
        """Checks if the ip is in Netbox, if true, then add the inactive scan tag"""

        if self.check_ipaddress(address):
            print(f"Tagging the address as inactive: {address}")
            self.add_inactive_tag(address)
