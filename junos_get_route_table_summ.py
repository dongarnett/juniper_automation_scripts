import os
import paramiko
import re
import sys
import time
from pprint import pprint
import argparse


'''Create device class to handle connectivity'''
class Device:
    #def __init__(self, hostname, username, password, session_timeout):
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        #self.session_timeout = session_timeout

'''Create device handle instance'''
def create_handle(self):
    # Connection Parameters
    print(f'Connecting to host {self.hostname}')
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=self.hostname, username=self.username, password=self.password)
    #client.load_system_host_keys(filename="/home/don/.ssh/id_rsa")
    #self.key_file = "/home/don/.ssh/id_rsa"
    #self.key = paramiko.RSAKey.from_private_key_file(key_file)
    #client.connect(hostname=switch_a, username=username, password=password)
    return client


'''Get routes from routing table'''
def get_route_summ(dut_host, route_table):
    '''Command sets for device configuration'''
    command_set_1 = [f'show route summary table {route_table}']
    '''Create handle'''
    dut_host_session = create_handle(dut_host)
    dut_host_terminal = dut_host_session.invoke_shell()
    #print(dir(dut_host_session))
    '''Start execution'''
    for command in command_set_1:
        print(f'Sending command: {command}\n')
        try:
            dut_host_terminal.send(f'{command}\n')
            time.sleep(1)
        except:
            print(f"An error occurred.")
        output = dut_host_terminal.recv(1000).decode('utf-8')
        #pprint(output)
    output_recv = output.split("\n")
    #pprint(output_recv)
    return output
    time.sleep(10)


'''Parse output from routing table data retrieved'''
def parse_route_table_prefix_counts(table_name, route_table_values):
    rt_sum_inputs = route_table_values.split("\n")
    route_table_dict = {"table": table_name}
    summary_dict = {}
    direct_dict = {}
    local_dict = {}
    bgp_dict = {}
    ospf_dict = {}
    for line in rt_sum_inputs:
        if "destinations" in line:
            summary_temp_list = line.split()
            #print(temp_list)
            summary_dict['total_routes'] = summary_temp_list[3]
            for items in summary_temp_list:
                if "(" in items:
                    items_temp = items.split("(")
                    fib_routes = items_temp[1]
            summary_dict['active_routes'] = fib_routes
            route_table_dict["sum_routes"] = summary_dict
            #print(summary_dict)
        if "Direct" in line:
            direct_temp_list = line.split()
            direct_dict['total_routes'] = direct_temp_list[1]
            direct_dict['active_routes'] = direct_temp_list[3]
            route_table_dict["direct_routes"] = direct_dict
            #print(direct_dict)
        if "Local" in line:
            local_temp_list = line.split()
            local_dict['total_routes'] = local_temp_list[1]
            local_dict['active_routes'] = local_temp_list[3]
            route_table_dict["local_routes"] = local_dict
            #print(local_dict)
        if "BGP" in line:
            bgp_temp_list = line.split()
            bgp_dict['total_routes'] = bgp_temp_list[1]
            bgp_dict['active_routes'] = bgp_temp_list[3]
            route_table_dict["bgp_routes"] = bgp_dict
            #print(bgp_dict)
        if "OSPF" in line:
            ospf_temp_list = line.split()
            ospf_dict['total_routes'] = ospf_temp_list[1]
            ospf_dict['active_routes'] = ospf_temp_list[3]
            route_table_dict["ospf_routes"] = ospf_dict
            #print(ospf_dict)
    if 'summary_temp_list' in locals():
        print(f"{table_name}: RIB Routes: {route_table_dict['sum_routes']['total_routes']}")
        print(f"{table_name}: FIB Routes: {route_table_dict['sum_routes']['active_routes']}")
    if 'direct_temp_list' in locals():
        print(f"{table_name}: Total Routes - Direct: {route_table_dict['direct_routes']['total_routes']}")
        print(f"{table_name}: Active Routes - Direct: {route_table_dict['direct_routes']['active_routes']}")
    if 'local_temp_list' in locals():
        print(f"{table_name}: Total Routes - Local: {route_table_dict['local_routes']['total_routes']}")
        print(f"{table_name}: Active Routes - Local: {route_table_dict['local_routes']['active_routes']}")
    if 'ospf_temp_list' in locals():
        print(f"{table_name}: Total Routes - OSPF: {route_table_dict['ospf_routes']['total_routes']}")
        print(f"{table_name}: Active Routes - OSPF: {route_table_dict['ospf_routes']['active_routes']}")
    if 'bgp_temp_list' in locals():
        print(f"{table_name}: Total Routes - BGP: {route_table_dict['bgp_routes']['total_routes']}")
        print(f"{table_name}: Active Routes - BGP: {route_table_dict['bgp_routes']['active_routes']}")
    print(route_table_dict)
    return route_table_dict


'''
The following code can be used to iterate through a set of device IPs.
'''
# args = sys.argv[1:]
# route_table = args[0]
# user = 'don'
# passwd = 'desi8g'
# timeout = 30
#
# dut_list = ['10.0.0.31']
# for system in dut_list:
#     host_ip = system
#     dut_host = Device(host_ip, user, passwd)
#     route_values = get_route_summ(dut_host, route_table)
#     route_table_values = route_values
#     try:
#         parse_route_table_prefix_counts(route_table, route_table_values)
#     except IndexError:
#         print(f"Verify that 'chassis network-services enhanced-ip' is configured on {host_ip}.")
#     except:
#         print(f"An error occurred.")


'''The following code can be used to execute this script file on 1 device under test.'''
cli_args = sys.argv[1:]
dut_ip = cli_args[0]
dut_user = cli_args[1]
dut_pass = cli_args[2]
route_table = cli_args[3]


'''DUT Login parameters'''
host_ip = dut_ip
user = dut_user
passwd = dut_pass
timeout = 30

def main():
    #pass
    dut_host = Device(host_ip, user, passwd)
    route_values = get_route_summ(dut_host, route_table)
    route_table_values = route_values
    try:
        parse_route_table_prefix_counts(route_table, route_table_values)
    except IndexError:
        print(f'Verify that "chassis network-services enhanced-ip" is configured on {host_ip}.')
    except:
        print(f'An error occurred.')

if __name__ == '__main__':
    main()
