#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 15:53:46 2021

@author: till
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import simulation

c_palette = sns.color_palette('pastel', 7)
plt.figure(dpi=300)

def get_winrate_by_draft(df):
    df_tmp = df.groupby(["draft_id","color"],as_index=False).sum()
    df_tmp["winrate"] = df_tmp["won"] / (df_tmp["won"]+df_tmp["lost"])
    return df_tmp.groupby(["color"]).mean()

def get_winrate_by_game(df):
    df_tmp = df.groupby(["color"]).sum()
    df_tmp["winrate"] = df_tmp["won"] / (df_tmp["won"]+df_tmp["lost"])
    return df_tmp

def map_record(record):
    if record.startswith('7'):
        return record
    else:
        return record[0] + '-3' 

def visualize_winrate(dataframe, x_column, y_column, title):
    dataframe["winrate in %"] = dataframe["winrate"] * 100
    plot = sns.barplot(x=x_column, y='winrate in %', data=dataframe.reset_index(),palette=c_palette)
    plot.set_title(title)
    plot.axhline(50,color='r',ls = 'dotted')
    plot.set(ylim=(30, 70))
    plt.show()

    
def visualize_delta_winrates(games_winrates,decks_winrate):
    games_winrates['delta in %'] = (games_winrates['winrate'] - decks_winrate['winrate']) * 100 
    plot = sns.barplot(x='color', y='delta in %', data=games_winrates.reset_index(),palette=c_palette)
    plot.set_title('Difference in winrates')
    plot.set(ylim=(4, 10))
    plt.show()
    
def visualize_record(df,title):
    plt.figure(dpi=300)
    df_tmp = df.copy()
    df_tmp["won"] = df_tmp["won"].apply(str)
    df_tmp["lost"] = df_tmp["lost"].apply(str)
    df_tmp["record"] = df_tmp["won"] + '-' + df_tmp["lost"]
    df_tmp.reset_index
    df_tmp["record"] = df_tmp["record"].apply(lambda record: map_record(record))
    df_tmp.reset_index
    df_tmp = df_tmp.groupby(["record"],as_index = False).count()
    df_tmp = df_tmp.reindex([0,1,2,3,4,5,6,9,8,7])
    
    #df_tmp.loc['Total',:] = df_tmp.sum(axis=0)
    #total = df_tmp.loc['Total',:] [2]
    total = df_tmp.sum(axis=0) [1]
    df_tmp['percentage'] = (df_tmp['draft_id'] / total ) * 100
    plot = sns.barplot(x="record", y='percentage', data=df_tmp.reset_index(),palette=c_palette)
    plot.set_ylabel("percentage of decks")
    plot.set_xlabel("games won in Tournament")
    plot.set(ylim=(0, 30))
    plot.set_title(title)
    plt.show()
    return df_tmp
    
    
def plot_high_low_variance():
    plt.figure(dpi=300)
    df_var_high = {'record': ['0-3','1-3','2-3','3-3','4-3','5-3','6-3','7-2','7-1','7-0'],
              'percentage': [50,0,0,0,0,0,0,0,0,50]}
    plot = sns.barplot(x="record", y='percentage', data=df_var_high,color='#99cccc')
    plot.set_ylabel("percentage of decks")
    plot.set_xlabel("games won in Tournament")
    plot.set(ylim=(0, 100))
    plot.set_title('var_high')
    plt.show()
    
def get_records(df):
    df_by_drafts = df.groupby(["draft_id","color"],as_index=False).sum()
    df_GU = df_by_drafts[df_by_drafts["color"].str.match("GU")]
    df_GB = df_by_drafts[df_by_drafts["color"].str.match("GB")]
    df_RW = df_by_drafts[df_by_drafts["color"].str.match("RW")]
    df_BW = df_by_drafts[df_by_drafts["color"].str.match("BW")]
    df_RU = df_by_drafts[df_by_drafts["color"].str.match("RU")]
    return_df = visualize_record(df_GU,"GU Records")
    visualize_record(df_GB,"GB Records")
    visualize_record(df_RW,"RW Records")
    visualize_record(df_BW,"BW Records")
    visualize_record(df_RU,"RU Records")
    return return_df
    
    
def compare_simul_real(df, color, winrate):
    real = get_records(df)
    simul = simulation.plot_simulation(color, winrate)
    simul = simul.rename(columns={"value":"simulation", "variable":"record"})
    result = pd.merge(real, simul, left_on='record', right_on='record')
    result = result.drop(["draft_id","color","user_win_rate_bucket","user_n_games_bucket","won","lost","deck_Plains","deck_Mountain","deck_Island","deck_Swamp", "deck_Forest"], axis=1)
    result = result.rename(columns={"percentage":"real"})
    result = result.melt(id_vars="record")
    result = result.rename(columns={"value":"percentage"})
    plot = sns.catplot(x="record", y="percentage", hue="variable", data=result,kind="bar")
    plot.fig.suptitle("Winrate " + color)
    plt.show()
    
def filter_by_rank(df, rank):
    df_tmp = df['rank'].str.contains(rank, na=False)
    df_tmp = df[df_tmp]
    return df_tmp

def winrate_by_rank(df, rank):
    rank_filter = filter_by_rank(df, rank)
    color_wr = get_winrate_by_game(rank_filter)
    visualize_winrate(color_wr,'color','winrate', 'winrate in ' + rank)
    
def draftsvsgames(df):
    winrate_draft = get_winrate_by_draft(df)
    winrate_game = get_winrate_by_game(df)
    winrate_game['games'] = winrate_game['won'] + winrate_game['lost']
    games_played = winrate_game['games']
    games_played = games_played.sort_values(ascending=False)
    games_played = games_played.reset_index()
    games_played.rename(columns = {'0':'games'},inplace = True)
    drafts_vs_games={
        'number' :[df.nunique()['draft_id'], games_played['games'].sum()],
        'type':  ["decks","games"]
        } 
    df_games_drafts = pd.DataFrame(drafts_vs_games, columns = ["number","type"])
    plotdvsgames = sns.barplot(x='type',y='number',data=df_games_drafts,palette=sns.color_palette('pastel', 7))
    plotdvsgames.set_title("Decks and Games")
    plt.show()


    
