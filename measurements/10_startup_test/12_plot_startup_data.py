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
        file_idle = master_path  + "/rcar_compute_base/startup-test.txt"
        file_load = master_path  + "/rcar_compute_load/startup-test.txt"
        name = "startup_test_rcar_compute.pdf"
    elif choice == "2":
        file_idle = master_path  + "/xeon_compute_base/startup-test.txt"
        file_load = master_path  + "/xeon_compute_load/startup-test.txt"
        name = "startup_test_xeon_compute.pdf"
    elif choice == "3":
        file_idle = master_path  + "/xeon_controller_base/startup-test.txt"
        file_load = master_path  + "/xeon_controller_load/startup-test.txt"
        name = "startup_test_xeon_controller.pdf"
    else:
        print("Invalid choice!")
        exit(1)

    return file_idle, file_load, name


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
    
    return results


def main():

    # setup plot env
    fig, ax = plt.subplots(3, 2, figsize=(10, 8))
    handles = list()
    labels  = list()

    for i in range(3):
        file_idle, file_load, name = get_file(str(i + 1))

        data_idle = load_file_data(file_idle)
        data_load = load_file_data(file_load)
    
        ax[i][0].plot(data_idle["time"], data_idle["cpu"], color='#005a9b', label='Native Usage')
        ax[i][0].plot(data_idle["time"], data_load["cpu"], color='#da1a30', label='Usage with OpenStack')
        ax[i][1].plot(data_idle["time"], data_idle["mem"], color='#005a9b', label='Native Usage')
        ax[i][1].plot(data_idle["time"], data_load["mem"], color='#da1a30', label='Usage with OpenStack')

        # general layout
        for j in range(2):
            ax[i][j].set_axisbelow(True)
            ax[i][j].grid(True, linestyle=':')
            ax[i][j].spines['right'].set_visible(False)
            ax[i][j].spines['top'].set_visible(False)
            ax[i][j].spines['left'].set_linewidth(1.5)
            ax[i][j].spines['bottom'].set_linewidth(1.5)
            ax[i][j].xaxis.set_label_coords(1.05,0.04)
            ax[i][j].set_xlabel('sec', rotation='horizontal')
            ax[i][j].set_xlim([0, max(data_idle["time"])*1.1])
            ax[i][j].plot((max(data_idle["time"])*1.1), (0), ls="", marker=">", ms=5, color="k", transform=ax[i][j].get_xaxis_transform(), clip_on=False)
            for h in ax[i][j].get_legend_handles_labels()[0]:
                handles.append(h)
            for l in ax[i][j].get_legend_handles_labels()[1]:
                labels.append(l)

        ax[i][0].set_ylim([0-max(data_idle["cpu"] + data_load["cpu"])*.1, max(data_idle["cpu"] + data_load["cpu"])*1.1])
        ax[i][1].set_ylim([0-max(data_idle["mem"] + data_load["mem"])*.1, max(data_idle["mem"] + data_load["mem"])*1.1])
        ax[i][0].plot((0), (max(data_idle["cpu"] + data_load["cpu"])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[i][0].get_yaxis_transform(), clip_on=False)
        ax[i][1].plot((0), (max(data_idle["mem"] + data_load["mem"])*1.1), ls="", marker="^", ms=5, color="k", transform=ax[i][1].get_yaxis_transform(), clip_on=False)
        
    # plot titles
    ax[0][0].title.set_text('R-Car Compute Node\n' + r'\small{CPU Usage in \%}')
    ax[0][1].title.set_text('R-Car Compute Node\n' + r'\small{Memory Usage in GB}')
    ax[1][0].title.set_text('Xeon Compute Node\n' + r'\small{CPU Usage in \%}')
    ax[1][1].title.set_text('Xeon Compute Node\n' + r'\small{Memory Usage in GB}')
    ax[2][0].title.set_text('Xeon Controller Node\n' + r'\small{CPU Usage in \%}')
    ax[2][1].title.set_text('Xeon Controller Node\n' + r'\small{Memory Usage in GB}')

    fig.tight_layout(pad=3.0)
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='lower center', bbox_to_anchor=(0.5, 0), ncol=2)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/101_startup_test/all-startup.pdf', transparent=True)


if __name__ == "__main__":
    main()
