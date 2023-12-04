import seaborn as sns
import pandas as pd
import numpy as np
import operator
import os
import plots
import matplotlib.pyplot as plt

def simulate_wr_color_comb(winrate):
    num_simul = 20000
    df = pd.DataFrame([(0, 0, 0, 0, 0, 0, 0, 0,0,0)],
                      columns=['0-3','1-3','2-3','3-3','4-3','5-3','6-3','7-2','7-1','7-0'])
    for i in range(0,num_simul):
        wins = 0
        losses = 0
        while True:
            if(coin_toss(winrate) == 1):
                wins += 1
            else:
                losses += 1
            if (wins == 7 or losses == 3):
                break
        df[str(wins)+"-"+str(losses)] += 1
        
    for row in df:
        df[row] = (df[row] /num_simul) * 100
    return df

def coin_toss(winrate):
    return np.random.binomial(1, winrate)

def plot_simulation(colorcombination, winrate):
    df = pd.melt(simulate_wr_color_comb(winrate))
    plot = sns.barplot(y='value',x = 'variable', data=df,color = '#FAC898')
    plot.set_title("simulation "+ colorcombination) 
    plot.set_ylabel("games")
    plot.set_xlabel("record")
    plt.show()
    return df
    

#plot_simulation('low_variance',0.5)
#plot_simulation("BW",0.582)
#plot_simulation("GB",0.537)
#plot_simulation("GU",0.561)
#plot_simulation("RW",0.536)
#plot_simulation("RU",0.54)

