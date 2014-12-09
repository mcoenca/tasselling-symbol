import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib import mlab




def print_stats(title, stats_list, percentiles):
    print("{} :: count: {} min: {} max: {}"
          .format(title, len(stats_list), min(stats_list), max(stats_list)))
    print("{} :: mean: {} stdev: {}"
          .format(title, '%.2f' % np.mean(stats_list),
                  '%.2f' % np.std(stats_list)))
    for percentile in percentiles:
        print("{} :: {}'th percentile : {}"
              .format(title, percentile,
                      '%.2f' % np.percentile(stats_list, percentile)))


def get_or_compute(filename, function):
    data = None
    try:
        with open(filename, 'r') as infile:
            data = json.load(infile)
        print("loaded data from file")
    except:
        print("computing data")
        data = function()
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)
    return data

def plot(x, n_bins, title=None, xlabel=None, ylabel=None, fname=None, log=False):
  max_data = max(x)
  if log:
    plt.hist(x, bins=np.logspace(0, 3.2), cumulative=True, normed=1)
    plt.semilogx()
    plt.xlim((1,10**3.2))
  else:
    plt.hist(x, n_bins, cumulative=True, normed=1)
    plt.xlim((0,max_data))
  plt.title(title)
  plt.xlabel(xlabel)
  plt.ylabel(ylabel)
  plt.ylim((0,1.01))
  #plt.show()
  plt.savefig(fname, dpi=400)
  plt.clf()
  #histtype='step', 

def hline():
  print(" \\hline")

def latex_table_r(top, other, total=None):
    print("\\begin{table}[H]")
    print(" \\centering")
    print(" INSERT TITLE \\\\")
    print(" \\begin{tabular}{| l | c | c | c | c |}")
    hline()
    print(" &  Min & Max & Mean & Std Dev  \\\\")
    hline()
    print(" Top Critcs & {0} & {1} & {2:.2f} & {3:.2f} \\\\"\
      .format(np.min(top),np.max(top),np.median(top),np.std(top)))
    print(" Other Critics & {0} & {1} & {2:.2f} & {3:.2f} \\\\"\
      .format(np.min(other),np.max(other),np.median(other),np.std(other)))
    if total:
        print(" All Critics & {0} & {1} & {2:.2f} & {3:.2f} \\\\"\
            .format(np.min(total),np.max(total),np.median(total),np.std(total)))
    hline()
    print(" \\end{tabular}")
    print(" \\end{table}")

def latex_table_m(top, other):
    print("\\begin{table}[H]")
    print(" \\centering")
    print(" INSERT TITLE \\\\")
    print(" \\begin{tabular}{| l | c | c | c | c |}")
    hline()
    print(" &  Min & Max & Mean & Std Dev  \\\\")
    hline()
    print(" Critics & {0} & {1} & {2:.2f} & {3:.2f} \\\\"\
      .format(np.min(top),np.max(top),np.median(top),np.std(top)))
    print(" Users & {0} & {1} & {2:.2f} & {3:.2f} \\\\"\
      .format(np.min(other),np.max(other),np.median(other),np.std(other)))
    hline()
    print(" \\end{tabular}")
    print(" \\end{table}")
