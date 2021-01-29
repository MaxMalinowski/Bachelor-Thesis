import os
import re

import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np

rc('text', usetex=True)

prompt = """Which platform do you want plotted?\n\
    1. Renesas RCAR as compute node\n\
    2. Intel Xeon as compute node\n\
    3. Intel Xeon as control node\n\
    4. NXP LX2 as control node\n\
Please enter your choice: """


def get_file(choice=None):
    
    if choice is None:
        choice = input(prompt)

    master_path = os.path.dirname(os.path.realpath(__file__))
    if choice == "1":
        file_host = master_path  + "/rcar_cluster/startup-host.txt"
        file_vm = master_path  + "/rcar_cluster/startup-vm.txt"
        name = "use-case-usage-rcar.pdf"
    elif choice == "2":
        file_host = master_path  + "/xeon_cluster/startup-host.txt"
        file_vm = master_path  + "/xeon_cluster/startup-vm.txt"
        name = "use-case-usage-xeon.pdf"
    else:
        print("Invalid choice!")
        exit(1)

    return file_host, file_vm, name


def load_file_data(file_path):
    file_data = list()
    start_mem = None
    start_time = None
    with open(file_path) as text_file: 
        lines = text_file.readlines()
        start_mem = lines[0][re.search(r"\d", lines[0]).start():len(lines[0])-3]
        start_time = lines[4]
        lines = lines[4:]
        
        for line in lines:
            if line.strip():
                file_data.append(line.strip())

    cnt = 0
    results = {"time": list(), "cpu": list(), "mem": list()}
    for line in file_data:
        if cnt == 0:
            timestamp = int(line) - int(start_time)
            results["time"].append(timestamp)
            cnt += 1
        elif cnt == 1:
            memory = (int(start_mem) - int(line[re.search(r"\d", line).start():len(line)-3])) / 1000 / 1000
            results['mem'].append(float("{:.2f}".format(memory)))
            cnt += 1
        else:
            results['cpu'].append(float("{:.2f}".format(100 - float(line))))
            cnt = 0
    
    return results, start_time


def main_rcar():

    # setup plot env
    fig, ax = plt.subplots(2, 1, figsize=(10, 5))
    handles = list()
    labels  = list()

    # get data
    file_host, file_vm, name = get_file("1")
    data_host, start_host = load_file_data(file_host)
    data_vm, start_vm = load_file_data(file_vm)

    # process data
    offset_time = int(start_vm) - int(start_host) 
    data_vm["time"] = [t + offset_time for t in data_vm["time"]]
    data_vm["cpu"] = [x * 0.5 for x in data_vm["cpu"]]
    data_vm["mem"] = [x + data_host["mem"][0] for x in data_vm["mem"]]
 
    data_vm["time"] = data_vm["time"][:data_vm["time"].index(data_host["time"][-1])+1]
    data_vm["cpu"] = data_vm["cpu"][:data_vm["time"].index(data_host["time"][-1])+1]
    data_vm["mem"] = data_vm["mem"][:data_vm["time"].index(data_host["time"][-1])+1]

    # plot data
    ax[0].plot(data_host["time"], data_host["cpu"], color='#005a9b', label="Host Usage")
    ax[0].plot(data_vm["time"], data_vm["cpu"], color='#da1a30', label="OpenStack VM Usage")
    ax[1].plot(data_host["time"], data_host["mem"], color='#005a9b', label="Host Usage")
    ax[1].plot(data_vm["time"], data_vm["mem"], color='#da1a30', label="OpenStack VM Usage")

    # plot timepoints
    ax[0].annotate('VM Start', ha='right', xy=(196, 0), xytext=(196, -13), arrowprops = dict(arrowstyle='->', relpos=(1, 0)))
    ax[0].annotate('VM OS Start', ha='right',xy=(data_vm["time"][0], 30), xytext=(data_vm["time"][0], -13),arrowprops = dict(arrowstyle='->', relpos=(1, 0)))
    ax[0].annotate('VNC Server Start', ha='left', xy=(310, 0), xytext=(310, -13), arrowprops = dict(arrowstyle='->', relpos=(0, 0)))
    ax[0].annotate('Application Start', ha='left', xy=(410, 0), xytext=(410, -13), arrowprops = dict(arrowstyle='->', relpos=(0, 0)))

    ax[1].annotate('VM Start', ha='right', xy=(196, 1.9), xytext=(196, 1.6), arrowprops = dict(arrowstyle='->', relpos=(1, 0)))
    ax[1].annotate('VM OS Start', ha='right', xy=(data_vm["time"][0], 2.1), xytext=(data_vm["time"][0], 1.6), arrowprops = dict(arrowstyle='->', relpos=(1, 0)))
    ax[1].annotate('VNC Server Start', ha='left', xy=(310, 2.1), xytext=(310, 1.6), arrowprops = dict(arrowstyle='->', relpos=(0, 0)))
    ax[1].annotate('Application Start', ha='left', xy=(410, 2.5), xytext=(410, 1.6), arrowprops = dict(arrowstyle='->', relpos=(0, 0)))

    # fill overhead
    tmp_cpu = data_host['cpu'][len(data_host['cpu'])-len(data_vm['cpu']):]
    ax[0].fill_between(data_vm["time"], data_vm["cpu"], tmp_cpu, facecolor='#005a9b', alpha=0.2, label='OpenStack Overhead') 
    tmp_mem = data_host['mem'][len(data_host['mem'])-len(data_vm['mem']):]
    ax[1].fill_between(data_vm["time"], data_vm["mem"], tmp_mem, facecolor='#005a9b', alpha=0.2, label='OpenStack Overhead') 

    # general layout
    for i in range(2):
        ax[i].set_axisbelow(True)
        ax[i].grid(True, linestyle=':')
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['left'].set_linewidth(1.5)
        ax[i].spines['bottom'].set_linewidth(1.5)
        ax[i].xaxis.set_label_coords(1.02,0.035)
        ax[i].set_xlabel('sec', rotation='horizontal')
        ax[i].set_xlim([0, max(data_host["time"])])
        ax[i].plot((max(data_host["time"])), (0), ls="", marker=">", ms=5, color="k", transform=ax[i].get_xaxis_transform(), clip_on=False)
        for h in ax[i].get_legend_handles_labels()[0]:
            handles.append(h)
        for l in ax[i].get_legend_handles_labels()[1]:
            labels.append(l)

    ax[0].set_ylim([-20, max(data_host["cpu"] + data_vm["cpu"])*1.1])
    ax[1].set_ylim([1.4, max(data_host["mem"] + data_vm["mem"])*1.1])
    ax[0].plot((0), (max(data_host["cpu"] + data_vm["cpu"])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[0].get_yaxis_transform(), clip_on=False)
    ax[1].plot((0), (max(data_host["mem"] + data_vm["mem"])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[1].get_yaxis_transform(), clip_on=False)

    # plot titles
    ax[0].title.set_text('VM Application on R-Car Host\n' + r'\small{CPU Usage in \%}')
    ax[1].title.set_text('VM Application on R-Car Host\n' + r'\small{Memory Usage in GB}')

    fig.tight_layout(pad=3.0)
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='lower center', bbox_to_anchor=(0.5, 0), ncol=3)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/109_migration_usecase_test/' + name, transparent=True)

def main_xeon():

    # setup plot env
    fig, ax = plt.subplots(2, 1, figsize=(10, 5))
    handles = list()
    labels  = list()

    # get data
    file_host, file_vm, name = get_file("2")
    data_host, start_host = load_file_data(file_host)
    data_vm, start_vm = load_file_data(file_vm)

    # process data
    offset_time = int(start_vm) - int(start_host) 
    data_vm["time"] = [t + offset_time for t in data_vm["time"]]
    data_vm["cpu"] = [x * 0.5 for x in data_vm["cpu"]]
    data_vm["mem"] = [x + data_host["mem"][0] for x in data_vm["mem"]]
 
    data_vm["time"] = data_vm["time"][:data_vm["time"].index(data_host["time"][-1])+1]
    data_vm["cpu"] = data_vm["cpu"][:data_vm["time"].index(data_host["time"][-1])+1]
    data_vm["mem"] = data_vm["mem"][:data_vm["time"].index(data_host["time"][-1])+1]

    # plot data
    ax[0].plot(data_host["time"], data_host["cpu"], color='#005a9b', label="Host Usage")
    ax[0].plot(data_vm["time"], data_vm["cpu"], color='#da1a30', label="OpenStack VM Usage")
    ax[1].plot(data_host["time"], data_host["mem"], color='#005a9b', label="Host Usage")
    ax[1].plot(data_vm["time"], data_vm["mem"], color='#da1a30', label="OpenStack VM Usage")

    # plot timepoints
    ax[0].annotate('VM Start', ha='right', xy=(196, 0), xytext=(196, -1.5), arrowprops = dict(arrowstyle='->', relpos=(1, 0)))
    ax[0].annotate('VM OS Start', ha='left',xy=(data_vm["time"][0], 0.8), xytext=(data_vm["time"][0], -1.5),arrowprops = dict(arrowstyle='->', relpos=(0, 0)))
    ax[0].annotate('VNC Server Start', ha='left', xy=(298, 0), xytext=(298, -1.5), arrowprops = dict(arrowstyle='->', relpos=(0, 0)))
    ax[0].annotate('Application Start', ha='left', xy=(399, 0), xytext=(399, -1.5), arrowprops = dict(arrowstyle='->', relpos=(0, 0)))

    ax[1].annotate('VM Start', ha='right', xy=(196, 9.9), xytext=(196, 8.5), arrowprops = dict(arrowstyle='->', relpos=(1, 0)))
    ax[1].annotate('VM OS Start', ha='left', xy=(data_vm["time"][0], 10.4), xytext=(data_vm["time"][0], 8.5), arrowprops = dict(arrowstyle='->', relpos=(0, 0)))
    ax[1].annotate('VNC Server Start', ha='left', xy=(298, 10.4), xytext=(298, 8.5), arrowprops = dict(arrowstyle='->', relpos=(0, 0)))
    ax[1].annotate('Application Start', ha='left', xy=(399, 10.7), xytext=(399, 8.5), arrowprops = dict(arrowstyle='->', relpos=(0, 0)))

    # fill overhead
    tmp_cpu = data_host['cpu'][len(data_host['cpu'])-len(data_vm['cpu']):]
    ax[0].fill_between(data_vm["time"], data_vm["cpu"], tmp_cpu, facecolor='#005a9b', alpha=0.2, label='OpenStack Overhead') 
    tmp_mem = data_host['mem'][len(data_host['mem'])-len(data_vm['mem']):]
    ax[1].fill_between(data_vm["time"], data_vm["mem"], tmp_mem, facecolor='#005a9b', alpha=0.2, label='OpenStack Overhead') 

    # general layout
    for i in range(2):
        ax[i].set_axisbelow(True)
        ax[i].grid(True, linestyle=':')
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['left'].set_linewidth(1.5)
        ax[i].spines['bottom'].set_linewidth(1.5)
        ax[i].xaxis.set_label_coords(1.02,0.035)
        ax[i].set_xlabel('sec', rotation='horizontal')
        ax[i].set_xlim([0, max(data_host["time"])])
        ax[i].plot((max(data_host["time"])), (0), ls="", marker=">", ms=5, color="k", transform=ax[i].get_xaxis_transform(), clip_on=False)
        for h in ax[i].get_legend_handles_labels()[0]:
            handles.append(h)
        for l in ax[i].get_legend_handles_labels()[1]:
            labels.append(l)

    ax[0].set_ylim([-2, max(data_host["cpu"] + data_vm["cpu"])*1.1])
    ax[1].set_ylim([8, max(data_host["mem"] + data_vm["mem"])*1.1])
    ax[0].plot((0), (max(data_host["cpu"] + data_vm["cpu"])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[0].get_yaxis_transform(), clip_on=False)
    ax[1].plot((0), (max(data_host["mem"] + data_vm["mem"])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[1].get_yaxis_transform(), clip_on=False)

    # plot titles
    ax[0].title.set_text('VM Application on Xeon Host\n' + r'\small{CPU Usage in \%}')
    ax[1].title.set_text('VM Application on Xeon Host\n' + r'\small{Memory Usage in GB}')

    fig.tight_layout(pad=3.0)
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='lower center', bbox_to_anchor=(0.5, 0), ncol=3)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/109_migration_usecase_test/' + name, transparent=True)


if __name__ == "__main__":
    main_rcar()
    main_xeon()
