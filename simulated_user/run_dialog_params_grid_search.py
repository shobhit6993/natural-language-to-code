# Runs grid search over the dialog parameters -- `DialogConfiguration` -- by
# running dialog sessions between the dialog agent and a simulated user using
# existing recipes and the API documentation of Channels and Functions.

import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sys

from simulated_user.run_pipeline import main


def run_gridsearch(metrics_csv_file):
    """Performs a grid-search over the dialog parameters, and runs dialog
    sessions for each parameter setting between the dialog agent and a simulated
    user using recipes from the IFTTT dataset.

    Args:
        metrics_csv_file (str): Path of the csv file where the metrics collected
        should be saved.
    """
    rows = []
    for alpha in np.linspace(0.05, 0.95, 10):
        for beta in np.linspace(0.05, 0.95, 10):
            if alpha < beta:
                continue
            # sys.argv[1:] = ("--log-level INFO --use-gold --alpha {} "
            #                 "--beta {}".format(alpha, beta).split(' '))
            sys.argv[1:] = ("--log-level CRITICAL --alpha {} "
                            "--beta {}".format(alpha, beta).split(' '))
            (average_dialog_length, percent_successful, percent_failure,
             percent_terminated) = main()

            rows.append({'alpha': alpha, 'beta': beta,
                         'average_dialog_length': average_dialog_length,
                         'success': percent_successful,
                         'failure': percent_failure,
                         'terminated': percent_terminated})

            with open(metrics_csv_file, 'w') \
                    as f:
                w = csv.DictWriter(
                    f, fieldnames=["alpha", "beta", "average_dialog_length",
                                   "success", "failure", "terminated"],
                    extrasaction="ignore")
                w.writeheader()
                w.writerows(rows)


def plot_heatmap(metrics_csv_file):
    """Plots the metrics saved in the `metrics_csv_file` as a heat-map.

    Args:
        metrics_csv_file (str): Path of the csv file where the metrics collected
        should be saved.
    """
    df = pd.read_csv(metrics_csv_file)
    dialog_len = df.pivot("alpha", "beta", "average_dialog_length")
    success = df.pivot("alpha", "beta", "success")
    # failure = df.pivot("alpha", "beta", "failure")
    # terminated = df.pivot("alpha", "beta", "terminated")

    grid_kws = {"height_ratios": (.9, .05), "hspace": .3}
    # fig, ax = plt.subplots(2, 4, gridspec_kw=grid_kws)
    fig, ax = plt.subplots(2, 2, gridspec_kw=grid_kws)

    sns.heatmap(dialog_len, linewidth=0.0, annot=True, ax=ax[0][0],
                cbar_ax=ax[1][0], cbar_kws={"orientation": "horizontal"})
    ax[0][0].set_title('Dialog Length')

    sns.heatmap(success, linewidth=0.0, annot=True, ax=ax[0][1],
                cbar_ax=ax[1][1], cbar_kws={"orientation": "horizontal"})
    ax[0][1].set_title('Success')

    # sns.heatmap(failure, linewidth=0.0, annot=True, ax=ax[0][2],
    #             cbar_ax=ax[1][2], cbar_kws={"orientation": "horizontal"})
    # ax[0][2].set_title('Failure')
    #
    # sns.heatmap(terminated, linewidth=0.0, annot=True, ax=ax[0][3],
    #             cbar_ax=ax[1][3], cbar_kws={"orientation": "horizontal"})
    # ax[0][3].set_title('Terminated')

    sns.plt.suptitle("Simulated user on validation set")
    plt.show()


def plot_learning_curve(metrics_csv_file, x_attribute, y_attribute):
    """Plots the learning curve between the two attributes, `x_attribute` and
     `y_attribute`, based on metrics saved in the `metrics_csv_file`.

    Args:
        metrics_csv_file (str): Path of the csv file where the metrics collected
        should be saved.
        x_attribute (str): The attribute to be plotted on the X-axis. It
            should be same as the corresponding column name in the csv file.
        y_attribute (str): The attribute to be plotted on the Y-axis. It
            should be same as the corresponding column name in the csv file.
    """
    df = pd.read_csv(metrics_csv_file)[[x_attribute, y_attribute, "alpha"]]
    color_list = ['sienna', 'black', 'darkgreen', 'red', 'blue', 'gold',
                  'silver', 'navy', 'orange', 'm', "lime", "grey"]
    sns.lmplot(x_attribute, y_attribute, data=df, hue='alpha',
               palette=color_list, fit_reg=False, legend_out=False, markers='o',
               scatter_kws={"s": 50})
    sns.plt.suptitle("Simulated user on validation set")
    plt.show()


if __name__ == '__main__':
    # run_gridsearch("./experiments/dialog/simulated-user-2/metrics.csv")
    # plot_heatmap("./experiments/dialog/simulated-user-1/metrics.csv")
    plot_learning_curve("./experiments/dialog/simulated-user-3/metrics.csv",
                        y_attribute="success",
                        x_attribute="average_dialog_length")
