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
        file_idle = master_path  + "/rcar_compute_base/net-test-v1.json"
        file_load = master_path  + "/rcar_compute_load/net-test-v1.json"
        name = "net_test_rcar_compute.pdf"
    elif choice == "2":
        file_idle = master_path  + "/xeon_compute_base/net-test-v1.json"
        file_load = master_path  + "/xeon_compute_load/net-test-v1.json"
        name = "net_test_xeon_compute.pdf"
    elif choice == "3":
        file_idle = master_path  + "/xeon_controller_base/net-test-v1.json"
        file_load = master_path  + "/xeon_controller_load/net-test-v1.json"
        name = "net_test_xeon_controller.pdf"
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
            if item["units"] == "Megabits/sec Throughput":
                tmp = item["results"]["net-test-v1"]
                data["means"].append(float(tmp["value"]))
                data["mins"].append(min([float(x) for x in tmp["all_results"].split(":")]))
                data["maxs"].append(max([float(x) for x in tmp["all_results"].split(":")]))
                if "Send File" in item["arguments"]:
                    tests.append("".join(item["arguments"].split(":")[2].split("-")[:1]))
                else:
                    tmp = item["arguments"].split(":")[2].split("-")[:2]
                    tmp.insert(1, "\n")
                    tests.append("".join(tmp))
                units.append(item["units"])
   
    return [np.array(data[key]) for key in data.keys()], tests, units


def main():

    # setup plot env
    fig, ax = plt.subplots(3, 1, figsize=(10, 8))
    bar_width = 0.35
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
        ax[i].barh(x2, data_idle[0], color='#005a9b', height=bar_width, capsize=4, label='Native Values')
        ax[i].barh(x1, data_load[0], color='#da1a30', height=bar_width, capsize=4, label='OpenStack VM Values')

        for i1, data in enumerate(data_idle[0]):
            ax[i].text(x=data*0.99, y=x2[i1], s=f"{round(data, 2)}", ha='right', va='center', color='white')
        for i1, data in enumerate(data_load[0]):
            ax[i].text(x=data*0.99, y=x1[i1], s=f"{round(data, 2)}", ha='right', va='center', color='white')

        # general layout
        ax[i].set_axisbelow(True)
        ax[i].xaxis.grid(True, linestyle=':')
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['left'].set_linewidth(1.5)
        ax[i].spines['bottom'].set_linewidth(1.5)
        ax[i].set_yticks([x + 0.5 * bar_width for x in range(len(data_idle[0]))]) 
        ax[i].set_yticklabels(tests_idle)
        ax[i].set_xlim([0, max(np.concatenate((data_idle[0], data_load[0]))*1.1)])
        ax[i].plot((max(np.concatenate((data_idle[0], data_load[0]))*1.1)), (0), ls="", marker=">", ms=5, color="k", transform=ax[i].get_xaxis_transform(), clip_on=False)
        
        for h in ax[i].get_legend_handles_labels()[0]:
            handles.append(h)
        for l in ax[i].get_legend_handles_labels()[1]:
            labels.append(l)
    
    # plot titles
    ax[0].title.set_text('R-Car Compute Node\n' + r'\small{Network Throughput in MB/s}')
    ax[1].title.set_text('Xeon Compute Node\n' + r'\small{Network Throughput in MB/s}')
    ax[2].title.set_text('Xeon Controller Node\n' + r'\small{Network Throughput in MB/s}')

    fig.tight_layout(pad=3.0)
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='lower center', bbox_to_anchor=(0.5, 0), ncol=2)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/105_net_test/all-net.pdf', transparent=True)


if __name__ == "__main__":
    main()
