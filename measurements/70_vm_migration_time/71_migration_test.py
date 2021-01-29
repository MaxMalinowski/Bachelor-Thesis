import openstack
import json
import time
import sys


class Migrator:

    conn = None
    server = None
    server_name = None
    server_image = None
    server_flavor = None
    server_network = None

    def __init__(self, name, image, flavor, network):
        # init connection to openstack cluster
        self.conn = self.__create_connection()
        self.server_name = name
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

    def create_server(self):
        # create and start instance
        print("Creating new server started ...")

        try:
            self.server = self.conn.compute.create_server(
                                name=self.server_name, 
                                image_id=self.conn.compute.find_image(self.server_image).id, 
                                flavor_id=self.conn.compute.find_flavor(self.server_flavor).id, 
                                networks=[{"uuid": self.conn.network.find_network(self.server_network).id}])
            self.server = self.conn.compute.wait_for_server(self.server)
            print("--> Server Created successfully!")
            return 0
        
        except Exception as e:
            print("--> Error creating server! --  " + str(e))
            return 1

    def migrate_server(self):
        # migrate server to counterpart and measure time until migration finished
        print("--> Migrating new server started ... ", end='')

        # get current and destination host
        if self.server.hypervisor_hostname == "kontron1":
            dest_host = "kontron2"
        elif self.server.hypervisor_hostname == "kontron2":
            dest_host = "kontron1"
        elif self.server.hypervisor_hostname == "rcar1":
            dest_host = "rcar2"
        elif self.server.hypervisor_hostname == "rcar2":
            dest_host = "rcar1"
        else:
            print("somthing is wrong: current host is invalid")
            exit(1)
        print("Destination: " + dest_host)

        try:
            # start migration
            self.conn.compute.live_migrate_server(self.server, host=dest_host, block_migration=True)
            self.server = self.conn.compute.wait_for_server(self.server, status='MIGRATING')
            start = time.time()
            self.server = self.conn.compute.wait_for_server(self.server)
            stop = time.time()
        
        except Exception as e:
            print("--> Error migrating server -- " + str(e))

        if self.server.hypervisor_hostname == dest_host:
            print("--> Server migrated successfully!")
            return float(stop) - float(start)
        else:
            print("--> Server migrated but did not change host!")
            return None
    
    def delete_server(self):
        # delete instance
        print("--> Deleting server ... ", end='')
        self.conn.compute.delete_server(self.server)
        try:
            self.conn.compute.wait_for_server(self.server, status='DELETED')
        
        except openstack.exceptions.ResourceNotFound:
            print("Done")
        
        except Exception:
            print("Probably done, but somthing didn't went as planned.")
        
        print("Done")
            

def main():

    tests = 20

    results = dict()
    results["values"] = list()
    results["average"] = int()

    if len(sys.argv) == 2:
        if sys.argv[1].startswith("rcar"):
            migrator = Migrator(name="migration-test-vm", image="Ubuntu-18.04-arm", flavor=sys.argv[1], network="private")
        elif sys.argv[1].startswith("xeon"):
            migrator = Migrator(name="migration-test-vm", image="Ubuntu-18.04-x86", flavor=sys.argv[1], network="private")
        else:
            print("Please supplie valid arguments!")
            exit(1)
    else:
        print("Please supplie valid arguments!")
        exit(1)

    for i in range(1, tests + 1):
        # start migrations
        duration = None
        print("[" + str(i) + "] ", end='') 
        if not migrator.create_server():    
            duration = migrator.migrate_server()
            print("--> Duration: " + str(duration))
        migrator.delete_server()

        if duration != None:
            results["values"].append(duration)
    
    results["average"] = sum(results["values"]) / len(results["values"])
    print("\n\n----------\n\n==> Average: " + str(results["average"]))

    with open("vm-migration-" + sys.argv[1] + ".json", "w") as json_file:
        json.dump(results, json_file, indent = 4)


if __name__ == "__main__":
    main()

