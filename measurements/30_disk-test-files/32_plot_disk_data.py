import json
import os

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
        file_idle = master_path  + "/rcar_compute_base/disk-test-v1.json"
        file_load = master_path  + "/rcar_compute_load/disk-test-v1.json"
        name = "disk_test_rcar_compute.pdf"
    elif choice == "2":
        file_idle = master_path  + "/xeon_compute_base/disk-test-v1.json"
        file_load = master_path  + "/xeon_compute_load/disk-test-v1.json"
        name = "disk_test_xeon_compute.pdf"
    elif choice == "3":
        file_idle = master_path  + "/xeon_controller_base/disk-test-v1.json"
        file_load = master_path  + "/xeon_controller_load/disk-test-v1.json"
        name = "disk_test_xeon_controller.pdf"
    else:
        print("Invalid choice!")
        exit(1)

    return file_idle, file_load, name


def load_file_data(file_path):
    data = dict()
    tests = list()
    units = list()
    
    with open(file_path) as json_file:
        results = json.load(json_file)
        data["means"] = list()
        data["mins"] = list()
        data["maxs"] = list()
        for item in results["results"]:
            if item["units"] != "IOPS":
                tmp = item["results"]["disk-test-v1"]
                data["means"].append(float(tmp["value"]))
                if tmp["all_results"] != '':
                    data["mins"].append(min([float(x) for x in tmp["all_results"].split(":")]))
                    data["maxs"].append(max([float(x) for x in tmp["all_results"].split(":")]))
                else:
                    data["mins"].append(float(tmp["value"]))
                    data["maxs"].append(float(tmp["value"]))
                tests.append(item["arguments"].split("-")[0].split(":")[1].strip())
                units.append(item["units"])
   
    return [np.array(data[key]) for key in data.keys()], tests, units


def main():

    # setup plot env
    fig, ax = plt.subplots(1, 3, figsize=(10, 5))
    bar_width = 0.4
    handles = list()
    labels  = list()

    for i in range(3):
        file_idle, file_load, name = get_file(str(i + 1))

        data_idle, tests_idle, units_idle = load_file_data(file_idle)
        data_load, tests_idle, units_idle = load_file_data(file_load)
    
        # calculate the x tick positions
        x1 = np.arange(len(data_idle[0]))
        x2 = [x + bar_width for x in x1]

        # create bars
        ax[i].bar(x1, data_idle[0], color='#005a9b', width=bar_width, capsize=4, label='Native Values')
        ax[i].bar(x2, data_load[0], color='#da1a30', width=bar_width, capsize=4, label='OpenStack VM Values')

        for i1, data in enumerate(data_idle[0]):
            ax[i].text(x=x1[i1] , y=data*0.99, s=f"{data}", ha='center', va='top', color='white')
        for i1, data in enumerate(data_load[0]):
            ax[i].text(x=x2[i1] , y=data*0.99 , s=f"{data}", ha='center', va='top', color='white')

        # general layout
        ax[i].set_axisbelow(True)
        ax[i].yaxis.grid(True, linestyle=':')
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['left'].set_linewidth(1.5)
        ax[i].spines['bottom'].set_linewidth(1.5)
        ax[i].set_xticks([x + 0.5 * bar_width for x in range(len(data_idle[0]))]) 
        ax[i].set_xticklabels(tests_idle)
        ax[i].set_ylim([0, max(np.concatenate((data_idle[0], data_load[0]))*1.1)])
        ax[i].plot((0), (max(np.concatenate((data_idle[0], data_load[0]))*1.1)), ls="", marker="^", ms=5, color="k", transform=ax[i].get_yaxis_transform(), clip_on=False)
        
        for h in ax[i].get_legend_handles_labels()[0]:
            handles.append(h)
        for l in ax[i].get_legend_handles_labels()[1]:
            labels.append(l)

    # plot titles
    ax[0].title.set_text('R-Car Compute Node\n' + r'\small{Disk Throughput in MB/s}')
    ax[1].title.set_text('Xeon Compute Node\n' + r'\small{Disk Throughput in MB/s}')
    ax[2].title.set_text('Xeon Controller Node\n' + r'\small{Disk Throughput in MB/s}')

    fig.tight_layout(pad=3.0)
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='lower center', bbox_to_anchor=(0.5, 0), ncol=2)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/103_disk_test/all-disk.pdf', transparent=True)

if __name__ == "__main__":
    main()
