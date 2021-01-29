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
        file_equal = master_path + "/rcar_cluster/vm-equal-distribution-rcar.json"
        file_stacked = master_path + "/rcar_cluster/vm-stacked-distribution-rcar.json"
        name = "rcar_cluster_vm_distribution.pdf"
    elif choice == "2":
        file_equal = master_path + "/xeon_cluster/vm-equal-distribution-xeon.json"
        file_stacked = master_path + "/xeon_cluster/vm-stacked-distribution-xeon.json"
        name = "xeon_cluster_vm_distribution.pdf"
    else:
        print("Invalid choice!")
        exit(1)

    return file_equal, file_stacked, name


def load_file_data(file_path):
    data = dict()
    
    with open(file_path) as json_file:
        results = json.load(json_file)
        data["host_1"] = [0]
        data["host_2"] = [0]
        data["time"] = [0]
        hc1 = 0
        hc2 = 0
        
        for i, vm in enumerate(results, start=1):
            if vm[0]["host"] == "rcar1" or vm[0]["host"] == "kontron1":
                hc1 += 1
            else:
                hc2 += 1
            data["host_1"].append(hc1)
            data["host_2"].append(hc2)
            data["time"].append(i)

    return [np.array(data[key]) for key in data.keys()]


def main():

    # setup plot env
    fig, ax = plt.subplots(2, 2, figsize=(10, 5))
    handles = list()
    labels  = list()

    for i in range(2):
        file_equal, file_stacked, name = get_file(str(i + 1))

        data_equal = load_file_data(file_equal)
        data_stacked = load_file_data(file_stacked)

        ax[i][0].plot(data_equal[2], data_equal[0], color='purple', label='R-Car 1 / Xeon 1')
        ax[i][0].plot(data_equal[2], data_equal[1], color='green', label='R-Car 2 / Xeon 2')
        ax[i][1].plot(data_equal[2], data_stacked[0], color='purple', label='R-Car 1 / Xeon 1')
        ax[i][1].plot(data_equal[2], data_stacked[1], color='green', label='R-Car 2 / Xeon 2')

        # general layout
        for j in range(2):
            ax[i][j].set_axisbelow(True)
            ax[i][j].grid(True, linestyle=':')
            ax[i][j].spines['right'].set_visible(False)
            ax[i][j].spines['top'].set_visible(False)
            ax[i][j].spines['left'].set_linewidth(1.5)
            ax[i][j].spines['bottom'].set_linewidth(1.5)
            ax[i][j].set_xticks([0, 2, 4, 6, 8, 10, 12, 14, 16]) 
            ax[i][j].set_xticklabels([0, 2, 4, 6, 8, 10, 12, 14, 16])
            ax[i][j].set_yticks([0, 2, 4, 6, 8]) 
            ax[i][j].set_yticklabels([0, 2, 4, 6, 8])
            ax[i][j].xaxis.set_label_coords(1.05,0)
            ax[i][j].yaxis.set_label_coords(0,1.02)
            ax[i][j].set_xlabel('Total\nVMs', rotation='horizontal', va='center')
            ax[i][j].set_ylabel('VMs\nper Host', rotation='horizontal')
            ax[i][j].set_xlim([0-8*0.1, 16*1.1])
            ax[i][j].set_ylim([0-8*.1, 8*1.1])
            ax[i][j].plot((max(data_equal[2])*1.1), (0), ls="", marker=">", ms=5, color="k", transform=ax[i][j].get_xaxis_transform(), clip_on=False)
            ax[i][j].plot((0), (8*1.1), ls="", marker="^", ms=5, color="k", transform=ax[i][j].get_yaxis_transform(), clip_on=False)
            
            for h in ax[i][j].get_legend_handles_labels()[0]:
                handles.append(h)
            for l in ax[i][j].get_legend_handles_labels()[1]:
                labels.append(l)

    # plot titles
    ax[0][0].title.set_text('R-Car Nodes\n' + r'\small{Equal VM Distribution}')
    ax[0][1].title.set_text('R-Car Nodes\n' + r'\small{Stacked VM Distribution}')
    ax[1][0].title.set_text('Xeon Nodes\n' + r'\small{Equal VM Distribution}')
    ax[1][1].title.set_text('Xeon Nodes\n' + r'\small{Stacked VM Distribution}')


    fig.tight_layout(pad=3.0)
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='lower center', bbox_to_anchor=(0.5, 0), ncol=4)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/106_distribution_test/all-distribution.pdf', transparent=True)


if __name__ == "__main__":
    main()