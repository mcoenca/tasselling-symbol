import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib import mlab
import json
import traceback
import argparse
import os
from os.path import isfile, join
import errno


def load_data(dirname):
    onlyfiles = [f for f in os.listdir(dirname) if isfile(join(dirname, f))]
    print(len(onlyfiles))
    data = []
    for filename in onlyfiles:
        to_open = str(join(dirname, filename))
        with open(to_open) as fp:
            data.append((json.load(fp),filename))
    for datum in data:
        draw(*datum)
    
def extract(item):
    return (item[1], item[2]/item[3])


def plot(tr_x, tr_y, te_x, te_y, fname, lambda_val):
    plt.plot(tr_x, tr_y, 'ro', te_x, te_y, 'g^')
    plt.title("Plot of Mean Squared Error vs. Iteration")
    plt.xlabel("Iteration")
    plt.ylabel("Error")
    plt.xlim((0,100))
    plt.ylim((0.0,1))
    plt.legend(['Training Error','Test Error'])
    plt.savefig("{}.{}".format(fname.split('.')[0],"png"), dpi=400)
    plt.clf()
 
def draw(data, filename):
    lambda_val = int(data["lambda"])
    dimension = int(data["dimension"])
    step = float(data["step"])
    result = data["result"]
    train_info = [tup[0] for tup in result]
    test_info = [tup[1] for tup in result]
    train_pts = [extract(tup) for tup in train_info]
    test_pts = [extract(tup) for tup in test_info]
    train_x, train_y = zip(*train_pts)
    test_x, test_y = zip(*test_pts)
    plot(train_x,train_y,test_x,test_y,filename,lambda_val)

def print_latex():
    for d in [1,10,25,40]:
        print("\\begin{figure}[H]")
        print("\\centering")
        for i in [0,1,3,10]:
            print("\\includegraphics[width=0.48\\textwidth]{plots/test-i100d"+\
                    str(d)+"l"+str(i)+".png}")
        print("\\caption{Mean squared training and test error over 100 iterations in the "+
            "stochastic matrix factorization model. Stocastic gradient descent was done using "+
            "a step size of 0.02. The learned critic matrix was count(critics) by "+str(d)+
            ", and the learned movie matrix was "+str(d)+" by count(movies).}")
        print("\\label{fig:"+str(d)+"}")
        print("\\end{figure}")



def main(): 
    print_latex()
    load_data("factor_results")

if __name__ == '__main__':
    main()
