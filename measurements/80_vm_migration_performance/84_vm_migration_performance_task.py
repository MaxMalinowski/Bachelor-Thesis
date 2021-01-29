#!/usr/bin/python3 -u

import openstack
import json
import time
import sys

from subprocess import call


def print_wait(msg, sec):
    print("--> " + msg + ":  " + str(sec), end="")
    for index in range(sec, 0, -1):
        print("\b", end="")
        print("\b", end="")
        print(index, end="", flush=True)
        time.sleep(1)
    print("")


class Migrator:

    conn = None
    server = None

    def __init__(self, name):
        # init connection to openstack cluster
        self.conn = self.__create_connection()
        servers = self.conn.compute.servers(all_projects=True)
        for item in servers:
            if item.name == name:
                self.server = self.conn.compute.get_server(item.id)

    def __create_connection(self):
        return openstack.connect(
                            region_name="RegionOne",
                            auth=dict(
                                auth_url="http://10.1.1.110/identity",
                                username="admin",
                                password="adminpass",
                                user_domain_name="default",
                                project_domain_name="demo",),
                            identity_interface='internal',)

    def start_server(self):
        # start or restart instance
        if self.server.status != 'SHUTOFF':
            print("--> Shutting instance down")
            self.conn.compute.stop_server(self.server)
            self.conn.compute.wait_for_server(self.server, status='SHUTOFF')
        print("--> Starting instance")
        self.conn.compute.start_server(self.server)
        self.conn.compute.wait_for_server(self.server)

    def migrate_server(self):
        # migrate server to counterpart and measure time until migration finished
        print("--> Migrating instance ...", end='')

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
            self.server = self.conn.compute.wait_for_server(self.server, wait=900)
            stop = time.time()
        
        except Exception as e:
            print("--> Error migrating server -- " + str(e))
            return None, None

        if self.server.hypervisor_hostname != dest_host:
            print("--> Error migrating server -- Server did not change host")
            return None, None
        else:
            print("--> Server migrated successfully")
            return int(start), int(stop)
    
    def get_performance_data(self):
        cmd = "scp -i login-key.pem ubuntu@10.1.1.247:~/migration-performance.txt ."
        call(cmd.split(" "))


def main():

    tests = 4
    
    if len(sys.argv) == 2:
        migrator = Migrator(name=sys.argv[1])
        if migrator.server == None:
            print("Server not found. Please supplie a valid server name!")    
            exit(1)
    else:
        print("Please supplie valid arguments!")
        exit(1)

    print("Starting Virtual Machine ...")
    migrator.start_server()
    print_wait("Waiting for vm to reach idle state", 120)

    res = list()
    for i in range (1, tests + 1):
        # migrate instances
        print("[" + str(i) + "] Migrating...")
        start_server = migrator.server.hypervisor_hostname
        start, stop = migrator.migrate_server()
        dest_server = migrator.server.hypervisor_hostname
        res.append({"iteration": i, "start_server": start_server, "dest_server": dest_server, "start_time": start, "end_time": stop})
        print_wait("Waiting for vm to reach idle state", 120)
    
    migrator.get_performance_data()
    
    with open("vm-migration-performance-" + migrator.server.hypervisor_hostname[:-1]+ ".json", "w") as json_file:
        json.dump(res, json_file, indent = 4)


if __name__ == "__main__":
    main()

