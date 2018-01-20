#!/usr/bin/env python2.7

import argparse
import datetime
import os
import pdb
import sys

import numpy as np
import pandas as pd
import psycopg2 as pg
import matplotlib.pyplot as plt

# the same weapon colors from XonStat
weapon_colors = {
    "arc": "#b8e9ff",
    "laser": "#ff5933",
    "blaster": "#ff5933",
    "shotgun": "#1f77b4",
    "uzi": "#b9e659",
    "machinegun": "#b9e659",
    "grenadelauncher": "#ff2600",
    "mortar": "#ff2600",
    "minelayer": "#bfbf00",
    "electro": "#597fff",
    "crylink": "#d940ff",
    "nex": "#00e6ff",
    "vortex": "#00e6ff",
    "hagar": "#d98059",
    "rocketlauncher": "#ffbf33",
    "devastator": "#ffbf33",
    "porto": "#7fff7f",
    "minstanex": "#d62728",
    "vaporizer": "#d62728",
    "hook": "#a5ffd8",
    "hlac": "#ffa533",
    "seeker": "#ff5959",
    "rifle": "#9467bd",
    "tuba": "#d87f3f",
    "fireball": "#33ff33"
}


def games_per_month(conn, year):
    """Games played per month."""

    # read the data into a dataframe from the database
    sql = """
        select game_type_cd, date_trunc('month', create_dt), to_char(create_dt, 'Mon') "month",
               count(*)
        from games
        where create_dt between '{}-01-01' and '{}-01-01'
        and game_type_cd in ('dm', 'ctf', 'duel', 'cts', 'tdm', 'ft')
        group by 1, 2, 3
        order by 1, 2;
        """.format(year, year+1)

    df = pd.read_sql(sql, conn)

    # set up the plot
    f, ax1 = plt.subplots(1, figsize=(20, 5))

    # set the bar width
    bar_width = 0.60

    # the number of months present in the dataset
    months = df["month"].unique()

    # positions of the left bar-boundaries
    bar_l = [i + 1 for i in range(len(months))]

    # positions of the x-axis ticks (center of the bars as bar labels)
    tick_pos = [i + (bar_width / 2) for i in bar_l]

    # grid lines
    ax1.set_axisbelow(True)
    ax1.grid(b=True, which='major', color='#aaaaaa')

    # HTML colors encoded as a string, indexed by groups of 6 chars
    colors = "1f77b4ff7f0e2ca02cd627289467bd8c564be377c27f7f7fbcbd2217becf"

    # tracking where the bottoms of the next bars to be drawn should go
    bottoms = [0] * len(months)

    # the height of each of the segments
    segment_heights = [0] * len(months)

    for i, game_type_cd in enumerate(df["game_type_cd"].unique()):

        bar_color = colors[i*6:i*6+6]

        segment_df = df[df.game_type_cd == game_type_cd]

        # create a bar plot, in position tick_pos
        ax1.bar(x=tick_pos,
                height=segment_df['count'],
                width=bar_width,
                label=game_type_cd,
                alpha=0.5,
                color='#{}'.format(bar_color),
                bottom=bottoms
                )

        # update the bottoms, set the labels
        for j, month in enumerate(months):
            height = int(segment_df[df.month == month]['count'])
            segment_heights[j] = height

            # put a label if the bar is big enough
            if height > 2000:
                ax1.text(j + 1.18, bottoms[j] + height/2, str(height), size=8)

            # update the bottoms
            bottoms[j] += height

    # the tick marks along the bottom
    plt.xticks(tick_pos, df['month'])

    # the label along the Y axis
    ax1.set_ylabel("Games")

    # the legend
    plt.legend(loc='best', ncol=3, fontsize='small')

    # set a buffer around the left and right edge
    plt.xlim([min(tick_pos) - bar_width, max(tick_pos) + bar_width])

    # a buffer above the top edge
    plt.ylim([0, max(bottoms)+3500])

    # the label at the top of each bar w/ the total
    for i, month in enumerate(months):
        ax1.text(i + 1.15, bottoms[i] + 300, str(bottoms[i]), size=8)

    plt.title("Games Per Month in {}".format(year))
    plt.savefig("{}_games_per_month.png".format(year))


def players_per_month(conn, year):
    """The number of distinct players (not counting bots) per month."""

    # read the data into a dataframe from the database
    sql = """
        select date_trunc('month', g.create_dt),
               to_char(g.create_dt, 'Mon') "month",
               count(distinct pgs.player_id)
        from games g join player_game_stats pgs on g.game_id = pgs.game_id
        where g.create_dt between '{year}-01-01' and '{next_year}-01-01'
        and pgs.create_dt between '{year}-01-01' and '{next_year}-01-01'
        and pgs.player_id > 1
        group by 1, 2
        order by 1;
        """.format(year=year, next_year=year+1)

    df = pd.read_sql(sql, conn)

    # set up the plot
    f, ax1 = plt.subplots(1, figsize=(20, 5))

    # set the bar width
    bar_width = 0.60

    # the number of months present in the dataset
    months = df["month"].unique()

    # positions of the left bar-boundaries
    bar_l = [i + 1 for i in range(len(months))]

    # positions of the x-axis ticks (center of the bars as bar labels)
    tick_pos = [i + (bar_width / 2) for i in bar_l]

    # grid lines
    ax1.set_axisbelow(True)
    ax1.grid(b=True, which='major', color='#aaaaaa')

    # create a bar plot, in position tick_pos
    ax1.bar(x=tick_pos,
            height=df['count'],
            width=bar_width,
            alpha=0.5,
            color='#1f77b4'
            )

    # the tick marks along the bottom
    plt.xticks(tick_pos, df['month'])

    # the label along the Y axis
    ax1.set_ylabel("Players")

    # the legend
    plt.legend(loc='best', ncol=3, fontsize='small')

    # set a buffer around the left and right edge
    plt.xlim([min(tick_pos) - bar_width, max(tick_pos) + bar_width])

    # a buffer above the top edge
    plt.ylim([0, df['count'].max()+500])

    # the label at the top of each bar w/ the total
    for i, month in enumerate(df["month"].unique()):
        value = int(df[df.month == month]['count'])
        ax1.text(i + 1.15, value + 100, str(value), size=8)

    plt.title("Players Per Month in {}".format(year))
    plt.savefig("{}_players_per_month.png".format(year))


def hours_played(conn, year):
    sql = """
        select to_char(g.create_dt, 'D') day_num,
               to_char(g.create_dt, 'Day') day_name,
               to_char(g.create_dt, 'HH24') hour_num,
               count(*) count
        from games g
        where g.create_dt between '{year}-01-01' and '{next_year}-01-01'
        group by 1, 2, 3
        order by 1, 3;""".format(year=year, next_year=year+1)

    df_raw = pd.read_sql(sql, conn)
    df = df_raw.pivot(index='day_num', columns='hour_num', values='count')

    df_norm = (df - df.mean().mean()) / (df.max().max() - df.min().min())

    # Plot it out
    fig, ax = plt.subplots(figsize=(24,7))
    ax.pcolor(df_norm, cmap=plt.cm.Oranges, alpha=0.8)

    # Format
    plt.gcf()

    # turn off the frame
    ax.set_frame_on(False)

    # help here from http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
    ax.set_yticks(np.arange(df_norm.shape[0]) + 0.5, minor=False)
    ax.set_xticks(np.arange(df_norm.shape[1]) + 0.5, minor=False)

    ax.invert_yaxis()
    ax.xaxis.tick_top()

    ax.set_xticklabels(df_raw.hour_num, minor=False)
    ax.set_yticklabels(df_raw['day_name'].unique(), minor=False)

    ax.grid(False)

    # Turn off all the ticks
    ax = plt.gca()

    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False

    plt.title("Average Games Per Hour (in UTC) in {}".format(year), y=1.08)
    plt.savefig("{}_hours_heatmap.png".format(year))


def weapon_damage_per_month(conn, year):
    """Weapon damage per month."""

    # read the data into a dataframe from the database
    sql = """
        select pws.weapon_cd,
           date_trunc('month', pws.create_dt),
           to_char(create_dt, 'Mon') "month",
           sum(pws.actual) "actual"
        from player_weapon_stats pws join cd_weapon cd on pws.weapon_cd = cd.weapon_cd
        where pws.create_dt between '2016-01-01' and '2017-01-01'
        and cd.weapon_cd not in ('vaporizer', 'hook', 'tuba')
        group by 1, 2, 3
        order by 1, 2
        ;
        """.format(year, year+1)

    df = pd.read_sql(sql, conn)

    # set up the plot
    f, ax1 = plt.subplots(1, figsize=(20, 5))

    # set the bar width
    bar_width = 0.60

    # the number of months present in the dataset
    months = df["month"].unique()

    # positions of the left bar-boundaries
    bar_l = [i + 1 for i in range(len(months))]

    # positions of the x-axis ticks (center of the bars as bar labels)
    tick_pos = [i + (bar_width / 2) for i in bar_l]

    # grid lines
    ax1.set_axisbelow(True)
    ax1.grid(b=True, which='major', color='#aaaaaa')

    # tracking where the bottoms of the next bars to be drawn should go
    bottoms = [0] * len(months)

    # the height of each of the segments
    segment_heights = [0] * len(months)

    for i, weapon_cd in enumerate(df["weapon_cd"].unique()):

        bar_color = weapon_colors[weapon_cd]

        segment_df = df[df.weapon_cd == weapon_cd]

        # create a bar plot, in position tick_pos
        ax1.bar(x=tick_pos,
                height=segment_df['actual'],
                width=bar_width,
                label=weapon_cd,
                alpha=0.5,
                color=bar_color,
                bottom=bottoms
                )

        # update the bottoms, set the labels
        for j, month in enumerate(months):
            height = int(segment_df[df.month == month]['actual'])
            segment_heights[j] = height

            # put a label if the bar is big enough
            if height/1000 > 10000:
                ax1.text(j + 1.3, bottoms[j] + height/2, str(height/1000), size=8, ha='center')

            # update the bottoms
            bottoms[j] += height

    # the tick marks along the bottom
    plt.xticks(tick_pos, df['month'])

    # the label along the Y axis
    ax1.set_ylabel("Damage Points")

    # the legend
    plt.legend(loc='best', ncol=3, fontsize='small')

    # set a buffer around the left and right edge
    plt.xlim([min(tick_pos) - bar_width, max(tick_pos) + bar_width])

    # a buffer above the top edge
    plt.ylim([0, max(bottoms)+5500000])

    # the label at the top of each bar w/ the total
    for i, month in enumerate(months):
        ax1.text(i + 1.3, bottoms[i] + 500000, str(bottoms[i]/1000), size=8, ha='center')

    plt.title("Weapon Damage Per Month in {} (in thousands)".format(year))
    plt.savefig("{}_weapon_damage_per_month.png".format(year))


def weapon_frags_per_month(conn, year):
    """Weapon damage per month."""

    # read the data into a dataframe from the database
    sql = """
        select pws.weapon_cd,
           date_trunc('month', pws.create_dt),
           to_char(create_dt, 'Mon') "month",
           sum(pws.frags) "frags"
        from player_weapon_stats pws join cd_weapon cd on pws.weapon_cd = cd.weapon_cd
        where pws.create_dt between '2016-01-01' and '2017-01-01'
        and cd.weapon_cd not in ('vaporizer', 'hook', 'tuba', 'rifle', 'seeker', 'fireball',
                                 'hlac', 'minelayer')
        group by 1, 2, 3
        order by 1, 2
        ;
        """.format(year, year+1)

    df = pd.read_sql(sql, conn)

    # set up the plot
    f, ax1 = plt.subplots(1, figsize=(20, 5))

    # set the bar width
    bar_width = 0.60

    # the number of months present in the dataset
    months = df["month"].unique()

    # positions of the left bar-boundaries
    bar_l = [i + 1 for i in range(len(months))]

    # positions of the x-axis ticks (center of the bars as bar labels)
    tick_pos = [i + (bar_width / 2) for i in bar_l]

    # grid lines
    ax1.set_axisbelow(True)
    ax1.grid(b=True, which='major', color='#aaaaaa')

    # tracking where the bottoms of the next bars to be drawn should go
    bottoms = [0] * len(months)

    # the height of each of the segments
    segment_heights = [0] * len(months)

    for i, weapon_cd in enumerate(df["weapon_cd"].unique()):

        bar_color = weapon_colors[weapon_cd]

        segment_df = df[df.weapon_cd == weapon_cd]

        # create a bar plot, in position tick_pos
        ax1.bar(x=tick_pos,
                height=segment_df['frags'],
                width=bar_width,
                label=weapon_cd,
                alpha=0.5,
                color=bar_color,
                bottom=bottoms
                )

        # update the bottoms, set the labels
        for j, month in enumerate(months):
            height = int(segment_df[df.month == month]['frags'])
            segment_heights[j] = height

            # put a label if the bar is big enough
            if height > 25000:
                ax1.text(j + 1.3, bottoms[j] + height/2, str(height), size=8, ha='center')

            # update the bottoms
            bottoms[j] += height

    # the tick marks along the bottom
    plt.xticks(tick_pos, df['month'])

    # the label along the Y axis
    ax1.set_ylabel("Frags")

    # the legend
    plt.legend(loc='best', ncol=3, fontsize='small')

    # set a buffer around the left and right edge
    plt.xlim([min(tick_pos) - bar_width, max(tick_pos) + bar_width])

    # a buffer above the top edge
    plt.ylim([0, max(bottoms)+50000])

    # the label at the top of each bar w/ the total
    for i, month in enumerate(months):
        ax1.text(i + 1.3, bottoms[i] + 3500, str(bottoms[i]), size=8, ha='center')

    plt.title("Weapon Frags Per Month in {}".format(year))
    plt.savefig("{}_weapon_frags_per_month.png".format(year))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, help="Year to calculate")
    args = parser.parse_args()

    year = args.year
    if not year:
        year = datetime.datetime.now().year

    pg_user = os.environ.get("PGUSER")
    pg_pass = os.environ.get("PGPASS")
    conn = pg.connect(database="xonstatdb", user=pg_user, password=pg_pass, host="localhost")

    games_per_month(conn, year)
    players_per_month(conn, year)
    hours_played(conn, year)
    weapon_damage_per_month(conn, year)
    weapon_frags_per_month(conn, year)


if __name__ == "__main__":
    sys.exit(main())
