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
        file_idle_gateway = master_path  + "/rcar_compute_base/net-test-v1-ping-gateway.txt"
        file_load_gateway = master_path  + "/rcar_compute_load/net-test-v1-ping-gateway.txt"
        file_idle_google = master_path  + "/rcar_compute_base/net-test-v1-ping-partner.txt"
        file_load_google = master_path  + "/rcar_compute_load/net-test-v1-ping-partner.txt"
        name = "net_test_rcar_compute_ping.pdf"
    elif choice == "2":
        file_idle_gateway = master_path  + "/xeon_compute_base/net-test-v1-ping-gateway.txt"
        file_load_gateway = master_path  + "/xeon_compute_load/net-test-v1-ping-gateway.txt"
        file_idle_google = master_path  + "/xeon_compute_base/net-test-v1-ping-partner.txt"
        file_load_google = master_path  + "/xeon_compute_load/net-test-v1-ping-partner.txt"
        name = "net_test_xeon_compute_ping.pdf"
    elif choice == "3":
        file_idle_gateway = master_path  + "/xeon_controller_base/net-test-v1-ping-gateway.txt"
        file_load_gateway = master_path  + "/xeon_controller_load/net-test-v1-ping-gateway.txt"
        file_idle_google = master_path  + "/xeon_controller_base/net-test-v1-ping-partner.txt"
        file_load_google = master_path  + "/xeon_controller_load/net-test-v1-ping-partner.txt"
        name = "net_test_xeon_controller_ping.pdf"
    else:
        print("Invalid choice!")
        exit(1)

    return file_idle_gateway, file_idle_google, file_load_gateway, file_load_google, name


def load_file_data(file_path_gateway, file_path_google):
    data = dict()
    tests = list()
    units = list()

    data["means"] = list()
    data["mins"] = list()
    data["maxs"] = list()

    with open(file_path_gateway) as text_file:
        lines = text_file.readlines()
        results_gateway = lines[len(lines)-1].split("=")[1].split("/")[:3]
    
    with open(file_path_google) as text_file:
        lines = text_file.readlines()
        results_google = lines[len(lines)-1].split("=")[1].split("/")[:3]

    data["means"].append(float(results_gateway[1]))
    data["means"].append(float(results_google[1]))
    data["mins"].append(float(results_gateway[0]))
    data["mins"].append(float(results_google[0]))
    data["maxs"].append(float(results_gateway[2]))
    data["maxs"].append(float(results_google[2]))

    tests.append("Gateway Latency")
    tests.append("Partner Latency")
    units.append("Milliseconds")
    units.append("Milliseconds")

    return [np.array(data[key]) for key in data.keys()], tests, units


def main():

    # setup plot env
    fig, ax = plt.subplots(1, 3, figsize=(10, 5))
    bar_width = 0.4
    handles = list()
    labels  = list()

    for i in range(3):
        file_idle_gateway, file_idle_google, file_load_gateway, file_load_google, name = get_file(str(i+1))

        # parse data
        data_idle, tests_idle, units_idle = load_file_data(file_idle_gateway, file_idle_google)
        data_load, tests_idle, units_idle = load_file_data(file_load_gateway, file_load_google)
    
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
    ax[0].title.set_text('R-Car Compute Node\n' + r'\small{Network Latency in ms}')
    ax[1].title.set_text('Xeon Compute Node\n' + r'\small{Network Latency in ms}')
    ax[2].title.set_text('Xeon Controller Node\n' + r'\small{Network Latency in ms}')

    fig.tight_layout(pad=3.0)
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='lower center', bbox_to_anchor=(0.5, 0), ncol=2)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/105_net_test/all-net-ping.pdf', transparent=True)


if __name__ == "__main__":
    main()
