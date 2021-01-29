import json
import os

import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np

rc('text', usetex=True)


prompt = """Which test do you want to plot?\n
    1. stream\n
    2. ramspeed\n 
Please enter your choice: """


def get_file(choice=None):
    
    if choice is None:
        choice = input(prompt)

    master_path = os.path.dirname(os.path.realpath(__file__))
    if choice == "1":
        file_idle = master_path  + "/rcar_compute_base/mem-test-v1.json"
        file_load = master_path  + "/rcar_compute_load/mem-test-v1.json"
        name = "mem_test_rcar_compute.pdf"
    elif choice == "2":
        file_idle = master_path  + "/xeon_compute_base/mem-test-v1.json"
        file_load = master_path  + "/xeon_compute_load/mem-test-v1.json"
        name = "mem_test_xeon_compute.pdf"
    elif choice == "3":
        file_idle = master_path  + "/xeon_controller_base/mem-test-v1.json"
        file_load = master_path  + "/xeon_controller_load/mem-test-v1.json"
        name = "mem_test_xeon_controller.pdf"
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
            if "v1" in file_path:
                tmp = item["results"]["mem-test-v1"]
                tests.append(item["arguments"].split(":")[1].strip())
                units.append(item["units"])
            elif "v2" in file_path:
                tmp = item["results"]["mem-test-v2"]
                tests.append("\n".join([item.split(":")[1].strip() for item in item["arguments"].split("-")]))
                units.append(item["units"])
            data["means"].append(float(tmp["value"]))
            data["mins"].append(min([float(x) for x in tmp["all_results"].split(":")]))
            data["maxs"].append(max([float(x) for x in tmp["all_results"].split(":")]))
            
    return [np.array(data[key]) for key in data.keys()], tests, units


def main():

    # setup plot env
    fig, ax = plt.subplots(3, 1, figsize=(10, 8))
    bar_width = 0.35
    handles = list()
    labels  = list()

    for i in range(3):
        file_idle, file_load, _ = get_file(str(i + 1))

        data_idle, tests_idle, _ = load_file_data(file_idle)
        data_load, _, _ = load_file_data(file_load)

        for j, item in enumerate(data_idle):
            data_idle[j] = item[1:]
        for j, item in enumerate(data_load):
            data_load[j] = item[1:]
    
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
        ax[i].set_yticklabels(tests_idle[1:])
        ax[i].set_xlim([0, max(np.concatenate((data_idle[0], data_load[0]))*1.1)])
        ax[i].plot((max(np.concatenate((data_idle[0], data_load[0]))*1.1)), (0), ls="", marker=">", ms=5, color="k", transform=ax[i].get_xaxis_transform(), clip_on=False)
        
        for h in ax[i].get_legend_handles_labels()[0]:
            handles.append(h)
        for l in ax[i].get_legend_handles_labels()[1]:
            labels.append(l)
    
    # plot titles
    ax[0].title.set_text('R-Car Compute Node\n' + r'\small{Memory Throughput in MB/s}')
    ax[1].title.set_text('Xeon Compute Node\n' + r'\small{Memory Throughput in MB/s}')
    ax[2].title.set_text('Xeon Controller Node\n' + r'\small{Memory Throughput in MB/s}')

    fig.tight_layout(pad=3.0)
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='lower center', bbox_to_anchor=(0.5, 0), ncol=2)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/104_mem_test/all-mem.pdf', transparent=True)

if __name__ == "__main__":
    main()
