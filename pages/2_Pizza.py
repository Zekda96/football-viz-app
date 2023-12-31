import streamlit as st
import numpy as np
import pandas as pd
from mplsoccer import PyPizza, add_image, FontManager
import matplotlib.pyplot as plt

# Load fonts
font_normal = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/roboto/'
                          'Roboto%5Bwdth,wght%5D.ttf')
font_italic = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/roboto/'
                          'Roboto-Italic%5Bwdth,wght%5D.ttf')
font_bold = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/'
                        'RobotoSlab%5Bwght%5D.ttf')

green = '#2ba02b'
red = '#d70232'
yellow = '#ff9300'
blue = '#1a78cf'

# --------------------------------- FUNCTIONS ---------------------------------
def map_stat_labels(labels_list):
    map_labels = {'Tackles\nplus\nInterceptions': 'Tackles +\nInterceptions',
                  'Percent\nof\nChallenge\nSuccess': 'Succ. Challenge %'}

    for i, label in enumerate(labels_list):
        if label in map_labels.keys():
            labels_list[i] = map_labels[label]

    return labels_list


def rank_data(stat_list, input_df, exclude_vals):
    vals = []
    debug = pd.DataFrame(input_df[['player', 'team', '90s']])

    for val in stat_list:
        ranks_df = pd.DataFrame(input_df[['player', 'team', '90s']])
        ranks_df.loc[:, val] = input_df[val]
        debug.loc[:, val] = input_df[val]
        # Eliminate columns with 0 on stat to be ranked
        ranks_df = ranks_df[ranks_df[val] != 0]
        # Filter out players with less than 450 mins
        ranks_df = ranks_df[ranks_df['90s'] >= 5]

        # Make stat p90 where applicable
        if val in exclude_vals:
            div = 1
        else:
            div = ranks_df['90s']

        ranks_df.loc[:, val] = ranks_df[val] / div

        # Calculate rank from available players
        ranks_df.loc[:, val] = round(ranks_df[val].rank(pct=True) * 100, 2)
        debug.loc[:, val] = ranks_df.loc[:, val]  # copy ranks to debug table
        # Store rank for selected player
        try:
            vals.append(ranks_df[val][ranks_df['player'] == player].iloc[0])

        except IndexError:
            vals.append(0)

    return vals, debug


# -------------------------------- DATA ---------------------------------------
df = st.session_state['database']
pizza_rank = pd.DataFrame(df)


exclude_values_p90 = st.session_state['exclude_values_p90']

rv_df = df.iloc[:, 12:]  # Exclude categorical columns
ranked_vals = rv_df.select_dtypes(include=np.number).columns.tolist()

# ------------------------ Page config ----------------------------------------
st.set_page_config(
    page_title='Data Analysis',
    page_icon=':soccer:'
)

# ------------------------- RANK PIZZA PLOT ------------------------------
st.subheader('Rank bar plot')

# Tabs for stats select
tab_def, tab_poss, tab_pmk, tab_atk = st.tabs(["Defense",
                                               "Possession",
                                               "Playmaking",
                                               "Attack"
                                               ]
                                              )

with tab_def:
    # Choose defense stats for pizza plot
    with st.expander('Advanced Settings'):
        stats_def = st.multiselect(
            'Choose stats',
            ranked_vals,
            default=[
                'Tkl+Int',
                'TklWinPoss',
                'DrbTkl%',
                'AerialWin%',
                'Clr',
            ]
        )

with tab_poss:
    # Choose possession stats for pizza plot
    with st.expander('Advanced Settings'):
        stats_poss = st.multiselect(
            'Choose stats',
            ranked_vals,
            default=[
                'PassesAttempted',
                'TotCmp%',
                'LiveTouch',
                'ProgCarries',
                'Switches'
            ]
        )

with tab_pmk:
    # Choose playmaking stats for pizza plot
    with st.expander('Advanced Settings'):
        stats_pmk = st.multiselect(
            'Choose stats',
            ranked_vals,
            default=[
                'CarriesToFinalThird',
                'ProgPasses',
                'SuccDrb',
                'KeyPasses',
                'SCA90',
            ]
        )

with tab_atk:
    # Choose possession stats for pizza plot
    with st.expander('Advanced Settings'):
        stats_atk = st.multiselect(
            'Choose stats',
            ranked_vals,
            default=[
                'npxG',
                'Shots',
                'SoT%',
                'npG-xG',
                'ProgPassesRec'
            ]
        )

col1, col2 = st.columns(2)

with col1:
    # Filter by team
    teams = pizza_rank.team.unique()
    team = st.selectbox(
        label='Choose Team',
        options=pizza_rank.team.unique(),
        index=int(np.where(teams == 'Manchester City')[0][0]),
    )


with col2:
    # Filter by player
    players_from_team = pizza_rank[pizza_rank['team'] == team].player
    player = st.selectbox(
        label='Choose Player',
        options=players_from_team,
        index=int(np.where(players_from_team == 'Rodri')[0][0]),
        # index=18,
    )
    # Player is filtered after calculating ranks

# Vals for pizza chart
rank_vals_def, ranks_debug_def = rank_data(stats_def,
                                           pizza_rank,
                                           exclude_values_p90
                                           )

rank_vals_poss, ranks_debug_poss = rank_data(stats_poss,
                                             pizza_rank,
                                             exclude_values_p90
                                             )

rank_vals_pmk, ranks_debug_pmk = rank_data(stats_pmk,
                                           pizza_rank,
                                           exclude_values_p90,
                                           )

rank_vals_atk, ranks_debug_atk = rank_data(stats_atk,
                                           pizza_rank,
                                           exclude_values_p90
                                           )

# Format labels for pizza plot
labels = [x.replace('_', '\n') for x in
          stats_def
          + stats_poss
          + stats_pmk
          + stats_atk]
labels = map_stat_labels(labels)

# ---------------------- Plotting the Pizza Chart -----------------------------
n_def = len(rank_vals_def)
n_poss = len(rank_vals_poss)
n_pmk = len(rank_vals_pmk)
n_atk = len(rank_vals_atk)
# color for the slices and text
# slice_colors = ["#1A78CF"] * 5 + ["#FF9300"] * 5 + ["#D70232"] * 5
slice_colors = ["#1A78CF"] * n_def \
               + ["#FF9300"] * n_poss \
               + ['#2ba02b'] * n_pmk \
               + ["#D70232"] * n_atk \



# text_colors = ["#000000"] * 10 + ["#F2F2F2"] * 5
text_colors = ["#000000"] * (n_def + n_poss + n_pmk) + ["#F2F2F2"] * n_atk

concat_of_vals = rank_vals_def + rank_vals_poss + rank_vals_pmk + rank_vals_atk

baker = PyPizza(
    params=labels,
    background_color="#222222",  # background color
    straight_line_color="#000000",  # color for straight lines
    straight_line_lw=1,
    last_circle_lw=1,  # linewidth of last circle
    other_circle_lw=0,  # linewidth for other circles
    inner_circle_size=20  # size of inner circle

)

fig_pizza, ax = baker.make_pizza(
    values=concat_of_vals,
    figsize=(8, 8.5),  # adjust the figsize according to your need
    color_blank_space="same",  # use the same color to fill blank space
    slice_colors=slice_colors,  # color for individual slices
    value_colors=text_colors,  # color for the value-text
    value_bck_colors=slice_colors,  # color for the blank spaces
    blank_alpha=0.4,  # alpha for blank-space colors
    kwargs_slices=dict(
        edgecolor="#000000", zorder=2, linewidth=1
    ),  # values to be used when plotting slices
    kwargs_params=dict(
        color="#F2F2F2", fontsize=11,
        va='center',
        wrap=True
    ),  # values to be used when adding parameter labels
    kwargs_values=dict(
        color="#F2F2F2", fontsize=11,
        zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="cornflowerblue",
            boxstyle="round,pad=0.2", lw=1
        )
    )  # values to be used when adding parameter-values labels
)

# ----------------------------- TEXT ELEMENTS
# Add credits
CREDIT_1 = "data: opta via fbref"
CREDIT_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

fig_pizza.text(
    0.01, 0.02, f"{CREDIT_1}\n{CREDIT_2}", size=9,
    color="#F2F2F2",
    ha="left"
)

# Add title
fig_pizza.text(
    0.515, 0.975, f"{player} - {team}", size=16,
    ha="center", fontproperties=font_bold.prop, color="#F2F2F2"
)

# add subtitle
league = 'Premier League'
season = '22-23'
fig_pizza.text(
    0.515, 0.95,
    f"Percentile Rank vs {league} Midfielders | Season {season}",
    size=13,
    ha="center", fontproperties=font_bold.prop, color="#F2F2F2"
)

leg_h = 0.92

# add text
fig_pizza.text(
    0.24, leg_h, "Attacking"
                 + "       "
                 + "Playmaking"
                 + "       "
                 + "Possession"
                 + "       "
                 + "Defending",
    size=14,
    fontproperties=font_bold.prop, color="#F2F2F2"
)

# add rectangles
fig_pizza.patches.extend([
    plt.Rectangle(
        (0.205, leg_h), 0.025, 0.021, fill=True, color=red,
        transform=fig_pizza.transFigure, figure=fig_pizza
    ),
    plt.Rectangle(
        (0.365, leg_h), 0.025, 0.021, fill=True, color=green,
        transform=fig_pizza.transFigure, figure=fig_pizza
    ),
    plt.Rectangle(
        (0.545, leg_h), 0.025, 0.021, fill=True, color=yellow,
        transform=fig_pizza.transFigure, figure=fig_pizza
    ),
    plt.Rectangle(
        (0.715, leg_h), 0.025, 0.021, fill=True, color=blue,
        transform=fig_pizza.transFigure, figure=fig_pizza
    ),
])

# Show plot
st.pyplot(fig_pizza)

st.divider()
# ----------------------------- Ranks Datatable


# Create datatable for checking ranks from all players
ranks_debug = ranks_debug_def.merge(ranks_debug_poss, how='left')
ranks_debug = ranks_debug.merge(ranks_debug_atk, how='left')

st.dataframe(ranks_debug[['player'] + stats_def + stats_poss + stats_atk])

st.divider()

st.text('TO-DO\n'
        '- Make ranks per position (Pizza)\n'
        '- Get Positions from TransferMarket\n')
