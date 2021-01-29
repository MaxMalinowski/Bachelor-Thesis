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
        file_host1 = master_path  + "/rcar_cluster_migration/migration-rcar1.txt"
        file_host2 = master_path  + "/rcar_cluster_migration/migration-rcar2.txt"
        file_vm = master_path  + "/rcar_cluster_migration/migration-vm.txt"
        name = "use-case-migration-rcar.pdf"
    elif choice == "2":
        file_host1 = master_path  + "/xeon_cluster_migration/migration-xeon1.txt"
        file_host2 = master_path  + "/xeon_cluster_migration/migration-xeon2.txt"
        file_vm = master_path  + "/xeon_cluster_migration/migration-vm.txt"
        name = "use-case-migration-xeon.pdf"
    else:
        print("Invalid choice!")
        exit(1)

    return file_host1, file_host2, file_vm, name


def load_file_data(file_list):
    data_list = list()
    time_list = list()
    mem_list = list()
    for file_path in file_list:
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
        data_list.append(file_data)
        time_list.append(start_time)
        mem_list.append(start_mem)
    
    results_list = list()
    for i, file_data in enumerate(data_list):
        cnt = 0
        results = {"time": list(), "cpu": list(), "mem": list()}
        for line in file_data:
            if cnt == 0:
                timestamp = int(line)
                results["time"].append(timestamp)
                cnt += 1
            elif cnt == 1:
                memory = (int(mem_list[i]) - int(line[re.search(r"\d", line).start():len(line)-3])) / 1000 / 1000
                results['mem'].append(float("{:.2f}".format(memory)))
                cnt += 1
            else:
                results['cpu'].append(float("{:.2f}".format(100 - float(line))))
                cnt = 0
        results_list.append(results)

    last_time = max(time_list)
    for item in results_list:
        for i, time in enumerate(item["time"]):
            if time >= int(last_time):
                for key in item.keys():
                    item[key] = item[key][i:]
                break
    
    for item in results_list:
        for i, time in enumerate(item["time"]):
            item["time"][i] = time - int(last_time)
    
    len_list = list()
    for item in results_list:
        for key in item.keys():
            len_list.append(len(item[key]))

    for item in results_list:
        for key in item.keys():
            item[key] = item[key][:min(len_list)]

    return results_list[0], results_list[1], results_list[2], last_time


def main_rcar():

     # setup plot env
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))
    handles = list()
    labels  = list()
    
    # get data
    file_host1, file_host2, file_vm, name = get_file("1")
    data_host1, data_host2, data_vm, start_time = load_file_data([file_host1, file_host2, file_vm])
    begin = 1610375976 - int(start_time)
    end = 1610377850 - int(start_time)

    # plot data
    ax[0].plot(data_host2["time"], data_host2["cpu"], color='purple', label='R-Car 1')
    ax[0].plot(data_host1["time"], data_host1["cpu"], color='green', label='R-Car 2')
    ax[1].plot(data_host2["time"], data_host2["mem"], color='purple', label='R-Car 1')
    ax[1].plot(data_host1["time"], data_host1["mem"], color='green', label='R-Car 2')

    # plot zoomed box
    axins = ax[1].inset_axes([0.82, 0.25, 0.2, 0.5])
    axins.plot(data_host1["time"], data_host1["mem"], color='green')
    axins.plot(data_host2["time"], data_host2["mem"], color='purple')

    # fill 
    fill_array_migrating = list()
    fill_array_finished = list()
    for item in data_host1["time"]:
        if item < begin:
            fill_array_migrating.append(False)
        else:
            fill_array_migrating.append(True)
        if item < end:
            fill_array_finished.append(False)
        else:
            fill_array_finished.append(True)
    
    ax[0].fill_between(data_host2["time"], 0, data_host2["cpu"], where=fill_array_migrating, facecolor='#005a9b', alpha=0.2, label='Migrating')
    ax[0].fill_between(data_host2["time"], 0, data_host2["cpu"], where=fill_array_finished, facecolor='white', alpha=1)
    ax[1].fill_between(data_host2["time"], 0, data_host2["mem"], where=fill_array_migrating, facecolor='#005a9b', alpha=0.2, label='Migrating')
    ax[1].fill_between(data_host2["time"], 0, data_host2["mem"], where=fill_array_finished, facecolor='white', alpha=1)

    # general layout
    for i in range(2):
        ax[i].grid(True, linestyle=':')
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['left'].set_linewidth(1.5)
        ax[i].spines['bottom'].set_linewidth(1.5)
        ax[i].xaxis.set_label_coords(1.02,0.035)
        ax[i].set_xlabel('sec', rotation='horizontal')
        ax[i].set_xlim([0, max(data_host1["time"] + data_host2["time"])])
        ax[i].plot((max(data_host1["time"] + data_host2["time"])), (0), ls="", marker=">", ms=5, color="k", transform=ax[i].get_xaxis_transform(), clip_on=False)
        for h in ax[i].get_legend_handles_labels()[0]:
            handles.append(h)
        for l in ax[i].get_legend_handles_labels()[1]:
            labels.append(l)

    ax[0].set_ylim([0-min(data_host1["cpu"] + data_host2["cpu"])*0.8, max(data_host1["cpu"] + data_host2["cpu"])*1.1])
    ax[1].set_ylim([min(data_host1["mem"] + data_host2["mem"])*0.8, max(data_host1["mem"] + data_host2["mem"])*1.1])
    ax[0].plot((0), (max(data_host1["cpu"] + data_host2["cpu"])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[0].get_yaxis_transform(), clip_on=False)
    ax[1].plot((0), (max(data_host1["mem"] + data_host2["mem"])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[1].get_yaxis_transform(), clip_on=False)

    # layout of zoomed box
    axins.set_xlim(2463, 2490)
    axins.set_ylim(1.65, 3.7)
    axins.set_xticks([])
    axins.set_yticks([])
    ax[1].indicate_inset_zoom(axins)

    # plot titles
    ax[0].title.set_text('Resource Usage R-Car Cluster\n' + r'\small{CPU Usage in \%}')
    ax[1].title.set_text('Resource Usage R-Car Cluster\n' + r'\small{Memory Usage in GB}')

    fig.tight_layout(pad=3.0)
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='lower center', bbox_to_anchor=(0.5, 0), ncol=3)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/109_migration_usecase_test/' + name, transparent=True)
    

def main_xeon():

     # setup plot env
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))
    handles = list()
    labels  = list()
    
    # get data
    file_host1, file_host2, file_vm, name = get_file("2")
    data_host1, data_host2, data_vm, start_time = load_file_data([file_host1, file_host2, file_vm])
    begin = 1610366675 - int(start_time)
    end = 1610366710 - int(start_time)

    # plot data
    ax[0].plot(data_host1["time"], data_host1["cpu"], color='green', label='Xeon 1')
    ax[0].plot(data_host2["time"], data_host2["cpu"], color='purple', label='Xeon 2')
    ax[1].plot(data_host1["time"], data_host1["mem"], color='green', label='Xeon 1')
    ax[1].plot(data_host2["time"], data_host2["mem"], color='purple', label='Xeon 2')

    # fill
    fill_array_migrating = list()
    fill_array_finished = list()
    for item in data_host1["time"]:
        if item < begin:
            fill_array_migrating.append(False)
        else:
            fill_array_migrating.append(True)
        if item < end:
            fill_array_finished.append(False)
        else:
            fill_array_finished.append(True)
    
    ax[0].fill_between(data_host1["time"], 0, data_host1["cpu"], where=fill_array_migrating, facecolor='#005a9b', alpha=0.2, label='Migrating')
    ax[0].fill_between(data_host1["time"], 0, data_host1["cpu"], where=fill_array_finished, facecolor='white', alpha=1)
    ax[1].fill_between(data_host1["time"], 0, data_host1["mem"], where=fill_array_migrating, facecolor='#005a9b', alpha=0.2, label='Migrating')
    ax[1].fill_between(data_host1["time"], 0, data_host1["mem"], where=fill_array_finished, facecolor='white', alpha=1)

    # general layout
    for i in range(2):
        ax[i].grid(True, linestyle=':')
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['left'].set_linewidth(1.5)
        ax[i].spines['bottom'].set_linewidth(1.5)
        ax[i].xaxis.set_label_coords(1.02,0.035)
        ax[i].set_xlabel('sec', rotation='horizontal')
        ax[i].set_xlim([0, max(data_host1["time"] + data_host2["time"])])
        ax[i].plot((max(data_host1["time"] + data_host2["time"])), (0), ls="", marker=">", ms=5, color="k", transform=ax[i].get_xaxis_transform(), clip_on=False)
        for h in ax[i].get_legend_handles_labels()[0]:
            handles.append(h)
        for l in ax[i].get_legend_handles_labels()[1]:
            labels.append(l)

    ax[0].set_ylim([0-min(data_host1["cpu"] + data_host2["cpu"])*0.8, max(data_host1["cpu"] + data_host2["cpu"])*1.1])
    ax[1].set_ylim([min(data_host1["mem"] + data_host2["mem"])*0.8, max(data_host1["mem"] + data_host2["mem"])*1.1])
    ax[0].plot((0), (max(data_host1["cpu"] + data_host2["cpu"])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[0].get_yaxis_transform(), clip_on=False)
    ax[1].plot((0), (max(data_host1["mem"] + data_host2["mem"])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[1].get_yaxis_transform(), clip_on=False)

    # plot titles
    ax[0].title.set_text('Resource Usage Xeon Cluster\n' + r'\small{CPU Usage in \%}')
    ax[1].title.set_text('Resource Usage Xeon Cluster\n' + r'\small{Memory Usage in GB}')

    fig.tight_layout(pad=3.0)
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='lower center', bbox_to_anchor=(0.5, 0), ncol=3)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/109_migration_usecase_test/' + name, transparent=True)

def main_vm():

     # setup plot env
    fig, ax = plt.subplots(2, 2, figsize=(10, 5))

    for j in range(2):
    
        # get data
        file_host1, file_host2, file_vm, name = get_file(str(j+1))
        data_host1, data_host2, data_vm, start_time = load_file_data([file_host1, file_host2, file_vm])

        # plot data
        ax[0][j].plot(data_vm["time"], data_vm["cpu"], color='#da1a30')
        ax[1][j].plot(data_vm["time"], data_vm["mem"], color='#da1a30')

        # general layout
        for i in range(2):
            ax[i][j].grid(True, linestyle=':')
            ax[i][j].spines['right'].set_visible(False)
            ax[i][j].spines['top'].set_visible(False)
            ax[i][j].spines['left'].set_linewidth(1.5)
            ax[i][j].spines['bottom'].set_linewidth(1.5)
            ax[i][j].xaxis.set_label_coords(1.04,0.035)
            ax[i][j].set_xlabel('sec', rotation='horizontal')
            ax[i][j].set_xlim([0, max(data_vm["time"])])
            ax[i][j].plot((max(data_vm["time"])), (0), ls="", marker=">", ms=5, color="k", transform=ax[i][j].get_xaxis_transform(), clip_on=False)

        ax[0][j].set_ylim([0, max(data_vm["cpu"])*1.1])
        ax[1][j].set_ylim([min(data_vm["mem"])*0.9, max(data_vm["mem"])*1.1])
        ax[0][j].plot((0), (max(data_vm["cpu"])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[0][j].get_yaxis_transform(), clip_on=False)
        ax[1][j].plot((0), (max(data_vm["mem"])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[1][j].get_yaxis_transform(), clip_on=False)

    # plot titles
    ax[0][0].title.set_text('Resource Usage R-Car VM\n' + r'\small{CPU Usage in \%}')
    ax[1][0].title.set_text('Resource Usage R-Car VM\n' + r'\small{Memory Usage in GB}')
    ax[0][1].title.set_text('Resource Usage Xeon VM\n' + r'\small{CPU Usage in \%}')
    ax[1][1].title.set_text('Resource Usage Xeon VM\n' + r'\small{Memory Usage in GB}')

    fig.tight_layout(pad=3.0)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/109_migration_usecase_test/use-case-migration-vm.pdf', transparent=True)


if __name__ == "__main__":
    main_rcar()
    main_xeon()
    main_vm()