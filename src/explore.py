#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 14:25:43 2021

@author: till
"""
import seaborn as sns
import pandas as pd
import numpy as np
import operator
import os
import plots
import simulation

head = None
color_pair_threshhold = 3

class DFrameManager:
    def __init__(self, file_path, chunksize):
        file_extension = os.path.splitext(file_path)[-1].lower()
        if 'xls' in file_extension:
            self.df = pd.read_excel(file_path)
        elif 'txt' in file_extension:
            self.df = pd.read_table(file_path)
        elif 'csv' in file_extension:
            self.df = pd.read_csv(file_path, chunksize=chunksize)
        else:
            raise NotImplementedError("File types other than xls, xlsx, txt and csv need to be implemented first")
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        del self.df



def get_colorpair(row):
    Forest_n = row["deck_Forest"]
    Mountain_n = row["deck_Mountain"]
    Island_n = row["deck_Island"]
    Plains_n = row["deck_Plains"]
    Swamp_n = row["deck_Swamp"]
    if Forest_n == 0 and Mountain_n == 0 and Island_n == 0 and Plains_n >= color_pair_threshhold and Swamp_n >= color_pair_threshhold:
        return "BW"
    if Forest_n == 0 and Mountain_n >= color_pair_threshhold and Island_n >= color_pair_threshhold and Plains_n == 0 and Swamp_n == 0:
        return "RU"
    if Forest_n == 0 and Mountain_n >= color_pair_threshhold and Island_n == 0 and Plains_n >= color_pair_threshhold and Swamp_n == 0:
        return "RW"
    if Forest_n >= color_pair_threshhold and Mountain_n == 0 and Island_n >= color_pair_threshhold and Plains_n == 0 and Swamp_n == 0:
        return "GU"
    if Forest_n >= color_pair_threshhold and Mountain_n == 0 and Island_n == 0 and Plains_n == 0 and Swamp_n >= color_pair_threshhold:
        return "GB"   
    
    #used if you want to look at all colors not just the main represented color pairs
    ### Start lesser relevant color pairs ###
    '''
    if Forest_n >= color_pair_threshhold and Mountain_n == 0 and Island_n == 0 and Plains_n >= color_pair_threshhold and Swamp_n == 0:
        return "GW"
    if Forest_n == 0 and Mountain_n == 0 and Island_n >= color_pair_threshhold and Plains_n == 0 and Swamp_n >= color_pair_threshhold:
        return "UB"
    if Forest_n == 0 and Mountain_n >= color_pair_threshhold and Island_n == 0 and Plains_n == 0 and Swamp_n >= color_pair_threshhold:
        return "RB"
    if Forest_n >= color_pair_threshhold and Mountain_n >= color_pair_threshhold and Island_n == 0 and Plains_n == 0 and Swamp_n == 0:
        return "GR"
    if Forest_n == 0 and Mountain_n == 0 and Island_n >= color_pair_threshhold and Plains_n >= color_pair_threshhold and Swamp_n == 0:
        return "UW"
    if Forest_n >= color_threshhold and Mountain_n == 0 and Island_n == 0 and Plains_n == 0 and Swamp_n == 0:
        return "G"
    if Forest_n == 0 and Mountain_n >= color_threshhold and Island_n == 0 and Plains_n == 0 and Swamp_n == 0:
        return "R"
    if Forest_n == 0 and Mountain_n == 0 and Island_n >= color_threshhold and Plains_n == 0 and Swamp_n == 0:
        return "U"
    if Forest_n == 0 and Mountain_n == 0 and Island_n == 0 and Plains_n >= color_threshhold and Swamp_n == 0:
        return "W"
    if Forest_n == 0 and Mountain_n == 0 and Island_n == 0 and Plains_n == 0 and Swamp_n >= color_threshhold:
        return "B"
    '''
    ### End lesser relevant color pairs ###
    
def read_game_data():    
    chunksize = 10 ** 3
    #chunk = pd.read_csv('../datasets/game_data_public.STX.PremierDraft.csv', chunksize= chunksize)
    #df = chunk.get_chunk()
    #cut = df[["user_win_rate_bucket","user_n_games_bucket",
    #          "deck_Forest","deck_Mountain","deck_Island","deck_Plains","deck_Swamp"]]
    #head = df.head()
    df = None
    with DFrameManager("../datasets/game_data_public.STX.PremierDraft.csv", chunksize) as reader:
        for chunk in reader.df:
            head = chunk.head()
            df_tmp = chunk[["user_win_rate_bucket","user_n_games_bucket","draft_id","rank","won",
              "deck_Forest","deck_Mountain","deck_Island","deck_Plains","deck_Swamp"]]
            if df is None:
                df = df_tmp
            else:
                df = pd.concat([df,df_tmp])
        return df
    
def get_winrate_by_draft(df):
    df_tmp = df.groupby(["draft_id","color"],as_index=False).sum()
    df_tmp["winrate"] = df_tmp["won"] / (df_tmp["won"]+df_tmp["lost"])
    return df_tmp.groupby(["color"]).mean()

def get_winrate_by_game(df):
    df_tmp = df.groupby(["color"]).sum()
    df_tmp["winrate"] = df_tmp["won"] / (df_tmp["won"]+df_tmp["lost"])
    return df_tmp

def get_winrate_by_no_games(df):
    df_tmp = df.groupby(["user_n_games_bucket"]).sum()
    df_tmp["winrate"] = df_tmp["won"] / (df_tmp["won"]+df_tmp["lost"])
    return df_tmp

def get_winrate_by_rank(df):
    #df['rank_simple'] = df['rank'].map(lambda x: x.split('-')[0])
    df_tmp = df.groupby(["rank"]).sum()
    df_tmp["winrate"] = df_tmp["won"] / (df_tmp["won"]+df_tmp["lost"])
    df_tmp = df_tmp.reset_index()
    df_tmp['rank'] = df_tmp['rank'].map(lambda x: x.split('-')[0])
    df_tmp = df_tmp.reset_index()
    return df_tmp




   
df = read_game_data()         
print("df set up")
df["color"] = df.apply(lambda row: get_colorpair(row), axis=1)
df["lost"] = ~df["won"]

winrate_draft = get_winrate_by_draft(df)
winrate_game = get_winrate_by_game(df)
winrate_game['games'] = winrate_game['won'] + winrate_game['lost']

winrate_games_bucket = get_winrate_by_no_games(df)
winrate_rank_bucket = get_winrate_by_rank(df)
winrate_rank_bucket = winrate_rank_bucket.groupby(['rank']).sum()
winrate_rank_bucket["winrate"] = winrate_rank_bucket["won"] / (winrate_rank_bucket["won"]+winrate_rank_bucket["lost"])
winrate_rank_bucket = winrate_rank_bucket.reindex(["Bronze","Silver","Gold","Platinum","Diamond","Mythic"])



plots.visualize_winrate(winrate_draft,'color','winrate','winrate by deck')
plots.visualize_winrate(winrate_game,'color','winrate','winrate by game')
plots.visualize_delta_winrates(winrate_game,winrate_draft)
plots.visualize_winrate(winrate_games_bucket,'user_n_games_bucket','winrate','winrate by games played')
plots.visualize_winrate(winrate_rank_bucket,'rank','winrate','winrate by rank')
plots.draftsvsgames(df)
plots.winrate_by_rank(df, "Silver")
plots.compare_simul_real(df, "GU", 0.50)
simulation.plot_simulation("BW",0.522)



games_played = winrate_game['games']
games_played = games_played.sort_values(ascending=False)
games_played = games_played.reset_index()
games_played.rename(columns = {'0':'games'},inplace = True)
plot = sns.barplot(x='color', y='games',data=games_played.reset_index(),palette=sns.color_palette('pastel', 1), log = True)
plot.set_title('Games Played')




    