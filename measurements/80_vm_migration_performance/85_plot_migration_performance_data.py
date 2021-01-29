import json
import os

import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np

rc('text', usetex=True)


prompt = """Which platform do you want plotted?\n\
    1. Renesas Cluster\n\
    2. Intel Cluster\n\
Please enter your choice: """


def get_file(choice=None):
    
    if choice is None:
        choice = input(prompt)

    master_path = os.path.dirname(os.path.realpath(__file__))
    if choice == "1":
        data_file = master_path + "/rcar_cluster/migration-performance.txt"
        data_meta = master_path + "/rcar_cluster/vm-migration-performance-rcar.json"
        name = "rcar_cluster_migration_performance.pdf"
    elif choice == "2":
        data_file = master_path + "/xeon_cluster/migration-performance.txt"
        data_meta = master_path + "/xeon_cluster/vm-migration-performance-kontron.json"
        name = "xeon_cluster_migration_performance.pdf"
    else:
        print("Invalid choice!")
        exit(1)

    return data_file, data_meta, name


def load_file_data(file_path):
    data = dict()
    tests = list()
    units = list()
    
    with open(file_path) as txt_file:
        lines = txt_file.readlines()
        data["eps"] = list()
        data["lat"] = list()
        data["time"] = list()

        start_time = lines[0].split('-')[1].strip()
        lines = lines[2:]

        for index in range(0, len(lines), 6):
            data["time"].append(float(lines[index].strip()) - float(start_time))
            data["eps"].append(float(lines[index+1].strip().split(':')[1].strip()))
            data["lat"].append(float(lines[index+2].strip().split(':')[1].strip()))
            
    return [np.array(data[key]) for key in data.keys()], tests, units, start_time

def load_meta_file(file_path):
    meta = list()
    hosts = list()

    with open(file_path) as json_file:
        results = json.load(json_file)
        for item in results:
            meta.append([item["start_time"], item["end_time"]])
            hosts.append(item["start_server"])

    return meta, hosts

def plot_rcar():

    # setup plot env
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))
    handles = list()
    labels  = list()

    # get data
    data_file, meta_file, name = get_file("1")
    data, tests, units, start = load_file_data(data_file)
    meta, hosts = load_meta_file(meta_file)

    # add offset to data
    offset = float(meta[0][0]) - float(start)
    test = 120 - offset
    for j, item in enumerate(meta):
        meta[j][0] = float(item[0]) + test
        meta[j][1] = float(item[1]) + test

    # plot data
    ax[0].plot(data[2], data[0], color='#da1a30')
    ax[1].plot(data[2], data[1], color='#da1a30')

    # fill space
    colors = {0: ['R-Car 1', '#da1a30', '/'], 1: ['R-Car 2', '#da1a30', '\\']}
    for i, item in enumerate(meta):
        
        if "1" in hosts[i]:
            c1 = 0
            c2 = 1
        else:
            c1 = 1
            c2 = 0
        
        ax[0].fill_between(data[2], 0, data[0], where= data[2] > item[0] - float(start) , facecolor='white', alpha=1)
        ax[0].fill_between(data[2], 0, data[0], where= data[2] > item[0] - float(start), facecolor='#005a9b', alpha=0.2, label='Migrating')
        ax[0].fill_between(data[2], 0, data[0], where= data[2] > item[1] - float(start), facecolor='white', alpha=1)
        ax[1].fill_between(data[2], data[1], max(data[1]), where= data[2] >= item[0] - float(start), facecolor='white', alpha=1)
        ax[1].fill_between(data[2], data[1], max(data[1]), where= data[2] > item[0] - float(start), facecolor='#005a9b', alpha=0.2, label='Migrating')
        ax[1].fill_between(data[2], data[1], max(data[1]), where= data[2] > item[1] - float(start), facecolor='white', alpha=1)

        # annotations
        if i == 0:
            x = 0.5 * (item[0] - float(start))
            ax[0].annotate(colors[c1][0], xy=(0, 700), xytext=(x, 700), color='pink', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[0].annotate(colors[c1][0], xy=(item[0]-float(start), 700), xytext=(x, 700), color='black',va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[1].annotate(colors[c1][0], xy=(0, 1.25), xytext=(x, 1.25), color='pink', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[1].annotate(colors[c1][0], xy=(item[0]-float(start), 1.25), xytext=(x, 1.25), color='black',va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
        else:
            x = 0.5 * (item[0] - float(start) - tmp) + tmp
            ax[0].annotate(colors[c1][0], xy=(tmp, 700), xytext=(x, 700), color='pink', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[0].annotate(colors[c1][0], xy=(item[0]-float(start), 700), xytext=(x, 700), color='black',va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[1].annotate(colors[c1][0], xy=(tmp, 1.25), xytext=(x, 1.25), color='pink', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[1].annotate(colors[c1][0], xy=(item[0]-float(start), 1.25), xytext=(x, 1.25), color='black',va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))

        tmp = item[1] - float(start)

        if i == len(meta) - 1:
            x = 0.5 * (data[2][-1] - (item[1] - float(start))) + item[1] - float(start)
            ax[0].annotate(colors[c2][0], xy=(item[1]-float(start), 700), xytext=(x, 700), color='pink', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[0].annotate(colors[c2][0], xy=(data[2][-1], 700), xytext=(x, 700), color='black', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[1].annotate(colors[c2][0], xy=(item[1]-float(start), 1.25), xytext=(x, 1.25), color='pink', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[1].annotate(colors[c2][0], xy=(data[2][-1], 1.25), xytext=(x, 1.25), color='black', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))

    # general layout
    ax[0].set_ylim([min(data[0])*0.9, max(data[0])*1.1])
    ax[0].plot((max(data[2])*1.025), (0), ls="", marker=">", ms=5, color="k", transform=ax[0].get_xaxis_transform(), clip_on=False)
    ax[0].plot((0), (max(data[0])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[0].get_yaxis_transform(), clip_on=False)
    ax[1].set_ylim([min(data[1])*0.9, max(data[1])*1.1])
    ax[1].plot((max(data[2])*1.025), (0), ls="", marker=">", ms=5, color="k", transform=ax[1].get_xaxis_transform(), clip_on=False)
    ax[1].plot((0), (max(data[1])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[1].get_yaxis_transform(), clip_on=False)

    for i in range(2):
        ax[i].grid(True, linestyle=':')
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['left'].set_linewidth(1.5)
        ax[i].spines['bottom'].set_linewidth(1.5)
        ax[i].xaxis.set_label_coords(1.02,0.035)
        ax[i].set_xlim([0, max(data[2])*1.025])
        ax[i].set_xlabel('sec', rotation='horizontal')
        
        for h in ax[i].get_legend_handles_labels()[0]:
            handles.append(h)
        for l in ax[i].get_legend_handles_labels()[1]:
            labels.append(l)

    # plot titles
    ax[0].title.set_text('R-Car Nodes\n' + r'\small{Events per Second During Migration}')
    ax[1].title.set_text('R-Car Nodes\n' + r'\small{Latency During Migration in ms}')

    fig.tight_layout(pad=3.0)
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='lower center', bbox_to_anchor=(0.5, 0), ncol=3)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/108_migration_performance_test/' + name, transparent=True)


def plot_xeon():

    # setup plot env
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))
    handles = list()
    labels  = list()

    # get data
    data_file, meta_file, name = get_file("2")
    data, tests, units, start = load_file_data(data_file)
    meta, hosts = load_meta_file(meta_file)

    # plot data
    ax[0].plot(data[2], data[0], color='#da1a30')
    ax[1].plot(data[2], data[1], color='#da1a30')

    # fill space
    colors = {0: ['Xeon 1', '#da1a30', '/'], 1: ['Xeon 2', '#da1a30', '\\']}
    tmp = None
    for i, item in enumerate(meta):
        
        if "1" in hosts[i]:
            c1 = 0
            c2 = 1
        else:
            c1 = 1
            c2 = 0

        ax[0].fill_between(data[2], 0, data[0], where= data[2] > item[0] - float(start) , facecolor='white', alpha=1)
        ax[0].fill_between(data[2], 0, data[0], where= data[2] > item[0] - float(start), facecolor='#005a9b', alpha=0.2, label='Migrating')
        ax[0].fill_between(data[2], 0, data[0], where= data[2] > item[1] - float(start), facecolor='white', alpha=1)
        ax[1].fill_between(data[2], data[1], max(data[1]), where= data[2] >= item[0] - float(start), facecolor='white', alpha=1)
        ax[1].fill_between(data[2], data[1], max(data[1]), where= data[2] > item[0] - float(start), facecolor='#005a9b', alpha=0.2, label='Migrating')
        ax[1].fill_between(data[2], data[1], max(data[1]), where= data[2] > item[1] - float(start), facecolor='white', alpha=1)

        # annotations
        if i == 0:
            x = 0.5 * (item[0] - float(start))
            ax[0].annotate(colors[c1][0], xy=(0, 6500), xytext=(x, 6500), color='pink', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[0].annotate(colors[c1][0], xy=(item[0]-float(start), 6500), xytext=(x, 6500), color='black',va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[1].annotate(colors[c1][0], xy=(0, 0.8875), xytext=(x, 0.8875), color='pink', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[1].annotate(colors[c1][0], xy=(item[0]-float(start), 0.8875), xytext=(x, 0.8875), color='black',va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
        else:
            x = 0.5 * (item[0] - float(start) - tmp) + tmp
            ax[0].annotate(colors[c1][0], xy=(tmp, 6500), xytext=(x, 6500), color='pink', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[0].annotate(colors[c1][0], xy=(item[0]-float(start), 6500), xytext=(x, 6500), color='black',va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[1].annotate(colors[c1][0], xy=(tmp, 0.8875), xytext=(x, 0.8875), color='pink', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[1].annotate(colors[c1][0], xy=(item[0]-float(start), 0.8875), xytext=(x, 0.8875), color='black',va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))

        tmp = item[1] - float(start)

        if i == len(meta) - 1:
            x = 0.5 * (data[2][-1] - (item[1] - float(start))) + item[1] - float(start)
            ax[0].annotate(colors[c2][0], xy=(item[1]-float(start), 6500), xytext=(x, 6500), color='pink', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[0].annotate(colors[c2][0], xy=(data[2][-1], 6500), xytext=(x, 6500), color='black', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[1].annotate(colors[c2][0], xy=(item[1]-float(start), 0.8875), xytext=(x, 0.8875), color='pink', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))
            ax[1].annotate(colors[c2][0], xy=(data[2][-1], 0.8875), xytext=(x, 0.8875), color='black', va='center', ha='center', arrowprops = dict(arrowstyle='->', relpos=(1, 0.5)))


    # general layout
    ax[0].set_ylim([min(data[0])*0.99, max(data[0])*1.01])
    ax[0].plot((max(data[2])*1.025), (0), ls="", marker=">", ms=5, color="k", transform=ax[0].get_xaxis_transform(), clip_on=False)
    ax[0].plot((0), (max(data[0])*1.01), ls="", marker="^", ms=5, color="k", transform=ax[0].get_yaxis_transform(), clip_on=False)
    ax[1].set_ylim([min(data[1])*0.99, max(data[1])*1.01])
    ax[1].plot((max(data[2])*1.025), (0), ls="", marker=">", ms=5, color="k", transform=ax[1].get_xaxis_transform(), clip_on=False)
    ax[1].plot((0), (max(data[1])*1.01), ls="", marker="^", ms=5, color="k", transform=ax[1].get_yaxis_transform(), clip_on=False)

    for i in range(2):
        ax[i].grid(True, linestyle=':')
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['left'].set_linewidth(1.5)
        ax[i].spines['bottom'].set_linewidth(1.5)
        ax[i].xaxis.set_label_coords(1.02,0.035)
        ax[i].set_xlim([0, max(data[2])*1.025])
        ax[i].set_xlabel('sec', rotation='horizontal')
        
        for h in ax[i].get_legend_handles_labels()[0]:
            handles.append(h)
        for l in ax[i].get_legend_handles_labels()[1]:
            labels.append(l)

    # plot titles
    ax[0].title.set_text('Xeon Nodes\n' + r'\small{Events per Second During Migration}')
    ax[1].title.set_text('Xeon Nodes\n' + r'\small{Latency During Migration in ms}')

    fig.tight_layout(pad=3.0)
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='lower center', bbox_to_anchor=(0.5, 0), ncol=3)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/108_migration_performance_test/' + name, transparent=True)


if __name__ == "__main__":
    plot_rcar()
    plot_xeon()