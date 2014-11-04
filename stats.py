import numpy as np
import json


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
