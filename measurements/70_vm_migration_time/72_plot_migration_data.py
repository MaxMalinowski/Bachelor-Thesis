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
        file_01 = master_path  + "/rcar_cluster/vm-migration-rcar-01-256-06.json"
        file_02 = master_path  + "/rcar_cluster/vm-migration-rcar-02-256-06.json"
        file_03 = master_path  + "/rcar_cluster/vm-migration-rcar-01-512-06.json"
        file_04 = master_path  + "/rcar_cluster/vm-migration-rcar-01-256-12.json"
        file_05 = master_path  + "/rcar_cluster/vm-migration-rcar-max.json"
        name = "rcar_cluster_migration_time.pdf"
    elif choice == "2":
        file_01 = master_path  + "/xeon_cluster/vm-migration-xeon-06-21504-106.json"
        file_02 = master_path  + "/xeon_cluster/vm-migration-xeon-12-21504-106.json"
        file_03 = master_path  + "/xeon_cluster/vm-migration-xeon-06-43008-106.json"
        file_04 = master_path  + "/xeon_cluster/vm-migration-xeon-06-21504-212.json"
        file_05 = master_path  + "/xeon_cluster/vm-migration-xeon-max.json"
        name = "xeon_cluster_migration_time.pdf"
    else:
        print("Invalid choice!")
        exit(1)

    return [file_01, file_02, file_03, file_04, file_05], name


def load_file_data(file_path):
    data = dict()
    data["avg"] = list()
    data["min"] = list()
    data["max"] = list()
    
    with open(file_path) as json_file:
        results = json.load(json_file)
        data["avg"].append(results["average"])
        data["min"].append(min(results["values"]))
        data["max"].append(max(results["values"]))
   
    return data["avg"][0]


def main():

    # setup plot env
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    bar_width = 0.5

    for i in range(2):

        file_list, name = get_file(str(i +1))

        # parse data
        data_list = list()
        for item in file_list:
            data_list.append(load_file_data(item))

        x1 = np.arange(len(data_list))
    
        # create bars
        ax[i].barh(x1, data_list, height=bar_width, color='#da1a30', capsize=4)
        
        for i1, data in enumerate(data_list):
            ax[i].text(x=data*0.99 , y=x1[i1], s=f"{round(data, 2)}", ha='right', va='center', color='white')

        # general layout
        ax[i].set_axisbelow(True)
        ax[i].xaxis.grid(True, linestyle=':')
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['left'].set_linewidth(1.5)
        ax[i].spines['bottom'].set_linewidth(1.5)
        ax[i].set_yticks(x1) 
        ax[i].set_xlim([0, max(data_list)*1.1])
        ax[i].plot((max(data_list)*1.1), (0), ls="", marker=">", ms=5, color="k", transform=ax[i].get_xaxis_transform(), clip_on=False)
    
    ax[0].set_yticklabels(['rcar-01-\n256-06', 'rcar-02-\n256-06', 'rcar-01-\n512-06', 'rcar-01-\n256-12', 'rcar-max'], ha='right')
    ax[1].set_yticklabels(['xeon-06-\n21504-106', 'xeon-12-\n21504-106', 'xeon-06-\n43008-106', 'xeon-06-\n21504-212', 'xeon-max'], ha='right')
    
    # plot titles
    ax[0].title.set_text('R-Car Nodes\n' + r'\small{Migration Times in s}')
    ax[1].title.set_text('Xeon Nodes\n' + r'\small{Migration Times in s}')

    fig.tight_layout(pad=3.0)
    plt.show()
    fig.savefig(os.path.dirname(os.path.realpath(__file__)) + '/../100_results/107_migration_time_test/all-migration.pdf', transparent=True)


if __name__ == "__main__":
    main()
