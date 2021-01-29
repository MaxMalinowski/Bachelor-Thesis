import openstack
import json
import sys


class Distributor:

    conn = None
    servers = list()
    server_name = None
    server_image = None
    server_flavor = None
    server_network = None

    def __init__(self, image, flavor, network):
        # init connection to openstack cluster
        self.conn = self.__create_connection()
        self.server_image = image
        self.server_flavor = flavor
        self.server_network = network

    def __create_connection(self):
        return openstack.connect(
                            region_name="RegionOne",
                            auth=dict(
                                auth_url="http://10.1.1.110/identity",
                                username="admin",
                                password="adminpass",
                                user_domain_name="default",
                                project_domain_name="default",),
                            identity_interface='internal',)

    def create_server(self, name):
        # create and start instance
        print("Creating new server started ...")

        try:
            server = self.conn.compute.create_server(
                                name=name, 
                                image_id=self.conn.compute.find_image(self.server_image).id, 
                                flavor_id=self.conn.compute.find_flavor(self.server_flavor).id, 
                                networks=[{"uuid": self.conn.network.find_network(self.server_network).id}])
            
            res = list()
            host = None
            flag = True
            
            # check for instance reschedules
            while (flag):
                print("--> Checking host... ", end='')
                flag, res, host = self.check_host(server, name, host, res)
                print(host)

            server = self.conn.compute.wait_for_server(server)
            print("--> Server Created successfully!")
            res.append({"index": name[name.find('-')+1:], "host": server.hypervisor_hostname, "error": False})
        
        except Exception as e:
            msg = {"index": name[name.find('-')+1:], "host": host, "error": True}
            if msg not in res:
                res.append(msg)
            print("--> Error creating server! --  " + str(e))
        
        finally:
            self.servers.append(server)
            return res
    
    def check_host(self, server, name, host, res):
        try:
            self.conn.compute.wait_for_server(server, failures=['ERROR'], wait=1)

        except openstack.exceptions.ResourceFailure:
            return False, res, host
        
        except openstack.exceptions.ResourceTimeout:
            tmp_host = server.hypervisor_hostname
            if (host is not None) and (tmp_host != host):
                msg = {"index": name[name.find('-')+1:], "host": host, "error": True}
                if msg not in res:
                    res.append(msg)
            if tmp_host is not None:
                host = tmp_host
            return True, res, host
        
        return False, res, host
    
    def delete_servers(self):
        # delete server
        print("Deleting servers ...")
        for server in self.servers:
            self.conn.compute.delete_server(server)


def main():

    tests = 16

    results = list()

    if len(sys.argv) == 2:
        flavors = ["rcar_01_256_06", "xeon_06_21504_106"]
        if sys.argv[1] == "rcar":
            distributor = Distributor(image="Ubuntu-18.04-arm", flavor=flavors[0], network="private")
        elif sys.argv[1] == "xeon":

            distributor = Distributor(image="Ubuntu-18.04-x86", flavor=flavors[1], network="private")
        else:
            print("Please supplie valid arguments!")
            exit(1)  
    else:
        print("Please supplie valid arguments!")
        exit(1)  

    for index in range(1, tests + 1):
        # start distributions
        res = distributor.create_server("test-" + str(index))
        results.append(res)
        print(res)
    
    distributor.delete_servers()
        
    with open("vm-distribution-" + sys.argv[1] + ".json", "w") as json_file:
        json.dump(results, json_file, indent = 4)


if __name__ == "__main__":
    main()

