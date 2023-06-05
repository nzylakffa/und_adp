import pandas as pd
import streamlit as st
import datetime
from datetime import date
from datetime import timedelta
import matplotlib as mpl
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup, SoupStrainer
import requests
import altair as alt


# Create two buttons for the dates's your comparing
# The data will be pulled for each of those dates
# Create a df that compares the differences
# Can do any analysis and graphs we want after that!
st.markdown("<h1 style='text-align: center; '>Input Start & End Dates for ADP</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; '>Please input a start date before the end date</h4>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: center; '>Note: If you use this page late at night, it might open with an error.</h6>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: center; '>All you need to do is adjust the ADP End Date one day back to fix it.</h6>", unsafe_allow_html=True)

start_date = st.date_input(
    "ADP Start Date",
    datetime.date(2023, 5, 6),
    min_value=datetime.date(2023,5,6),
    max_value=date.today() - timedelta(days=1))

end_date = st.date_input(
    "ADP End Date",
    value=date.today() - timedelta(days=1),
    min_value=datetime.date(2023,5,6),
    max_value=date.today())

# Collect ADP's for the two dates given
start_url = "https://raw.githubusercontent.com/nzylakffa/und_adp/main/'" + str(start_date) + "_Underdog_ADP.csv"
end_url = "https://raw.githubusercontent.com/nzylakffa/und_adp/main/'" + str(end_date) + "_Underdog_ADP.csv"

# Create DF's
start_df = pd.read_csv(start_url)
end_df = pd.read_csv(end_url)

# Change column headings
start_df = start_df.rename(columns = {'adp': 'start_adp',
                            'pos_rank': 'start_pos_rank',
                            'date': 'start_date'})

end_df = end_df.rename(columns = {'adp': 'end_adp',
                            'pos_rank': 'end_pos_rank',
                            'date': 'end_date'})

# Merge on id, player_id player_name, position, team
adp_df = start_df.merge(end_df, on = ['id', 'player_id', 'full_name', 'position'])

# Replace "-" with 250
adp_df['start_adp'] = adp_df['start_adp'].str.replace('-','216')
adp_df['end_adp'] = adp_df['end_adp'].str.replace('-','216')

# Change adp columns to floats
adp_df['start_adp'] = adp_df['start_adp'].astype(float)
adp_df['end_adp'] = adp_df['end_adp'].astype(float)

# Calculate change in ADP!
adp_df['ADP Change'] = adp_df['start_adp'] - adp_df['end_adp']

# Only show these columns in the DF
final_adp_df = adp_df[['full_name', 'position', 'team_y', 'start_adp', 'end_adp', 'ADP Change', 'start_pos_rank', 'end_pos_rank']]

# Rename table headers
final_adp_df = final_adp_df.rename(columns = {'full_name': 'Player',
                                              'position': 'Pos',
                                              'team': 'Team',
                                              'start_adp': 'Start ADP',
                                              'end_adp': 'End ADP',
                                              'start_pos_rank': 'Start Pos Rank',
                                              'end_pos_rank': 'End Pos Rank',
                                              'team_y': 'Team'})


# Set up filter
selected_positions = st.multiselect(
    'Would you like to filter by specific positions?',
    ['QB', 'RB', 'WR', 'TE'],
    ['QB', 'RB', 'WR', 'TE'])


# Filter pos
final_adp_df = final_adp_df[final_adp_df['Pos'].isin(selected_positions)]


########
# Tabs #
########

tab_chart, tab_table, tab_player = st.tabs(["ADP Chart", "ADP Table", "Player ADP"])


with tab_table:

    # Print DF
    st.markdown("<h1 style='text-align: center; '>Changes in Underdog ADP</h1>", unsafe_allow_html=True)
    st.dataframe(final_adp_df)
    
    
with tab_chart:    

    #####################
    # Creating the Plot #
    #####################

    # Sort largest to smallest
    final_adp_df = final_adp_df.sort_values(by = "ADP Change", ascending=False)
    final_adp_df_head = final_adp_df.head(10)

    # Sort smallest to largets
    final_adp_df = final_adp_df.sort_values(by = "ADP Change", ascending=True)
    final_adp_df_tail = final_adp_df.head(10)

    # Stack df's on top of each other
    dfs = [final_adp_df_head, final_adp_df_tail]
    adp_risers_fallers = pd.concat(dfs).reset_index(drop=True)

    # Prepare Data
    x = adp_risers_fallers.loc[:, ['ADP Change']]
    adp_risers_fallers['colors'] = ['red' if x < 0 else 'darkgreen' for x in adp_risers_fallers['ADP Change']]
    adp_risers_fallers.sort_values('ADP Change', inplace=True)
    adp_risers_fallers.reset_index(inplace=True)

    # Draw plot
    fig = plt.figure(figsize=(14,16), dpi= 80)
    plt.scatter(adp_risers_fallers['ADP Change'], adp_risers_fallers.index, s=1500, alpha=.6, color=adp_risers_fallers.colors)
    for x, y, tex in zip(adp_risers_fallers['ADP Change'], adp_risers_fallers.index, adp_risers_fallers['ADP Change']):
        t = plt.text(x, y, round(tex, 1), horizontalalignment='center', 
                     verticalalignment='center', fontdict={'color':'white',
                                                           'size': 15})
    
    # Create start and end dates for title
    start_text = str(start_date)
    end_text = str(end_date)

    # Only keep month and day
    start_text = start_text[5:]
    end_text = end_text[5:]

    # Decorations
    # Lighten borders
    plt.gca().spines["top"].set_alpha(.3)
    plt.gca().spines["bottom"].set_alpha(.3)
    plt.gca().spines["right"].set_alpha(.3)
    plt.gca().spines["left"].set_alpha(.3)

    plt.yticks(adp_risers_fallers.index, adp_risers_fallers['Player'], fontsize=17)
    plt.xticks(fontsize = 17)
    plt.title('10 Biggest Risers & Fallers: ' + start_text + ' -> ' + end_text, fontdict={'size':30})
    plt.xlabel('Change in Underdog ADP', fontdict={'size': 20})
    plt.grid(linestyle='--', alpha=0.5)
    plt.xlim(min(adp_risers_fallers['ADP Change'])-1, max(adp_risers_fallers['ADP Change'])+1)
    plt.axvline(x=0, color='gray', linewidth=0.75)
    st.pyplot(fig)
    
with tab_player:
    df = pd.DataFrame(columns = ["full_name", "adp", "date"])
    st.caption("This tab will pull it's own ADP's!")
    st.caption("That means there's no need to use the above filters")
    st.caption("It will take ~ 15 seconds each time you select a player/players. Please be Patient")
    load = st.checkbox("Check the box to collect ADP's", value=True)
    if load:
        html = requests.get('https://github.com/nzylakffa/und_adp')
        dfs = []
        for link in BeautifulSoup(html.text, parse_only=SoupStrainer('a'), features = 'lxml'):
            if hasattr(link, 'href') and link['href'].endswith('.csv'):
                url = 'https://github.com'+link['href'].replace('/blob/', '/raw/')
                dfs.append(pd.read_csv(url))
                df = pd.concat(dfs)
            

    selected_players = st.multiselect(
    "Which Player's ADP Would You Like to Compare?",
    df['full_name'].unique(),
    ["Kadarius Toney", "Treylon Burks", "Isiah Pacheco"])

    df = df[df['full_name'].isin(selected_players)]

    df = df[['full_name', 'adp', 'date']]
    
    # Rename table headers
    df = df.rename(columns = {'full_name': 'Player'})

    df['date'] = pd.to_datetime(df['date'], format="%Y/%m/%d")

    df = df.sort_values(by = 'Player', ascending = True)
    df = df.sort_values(by = 'date', ascending = True)
    df = df.reset_index(drop=True)

    line_chart = alt.Chart(df).mark_line().encode(
        alt.X('date:T', title = "Date"),
        alt.Y("adp:Q", title = "ADP", scale=alt.Scale(reverse=True, zero=False), axis=alt.Axis(tickCount=8)),
        color=alt.Color("Player", legend=None))
    
    label = line_chart.encode(
    x='max(date):T',
    y=alt.Y('adp:Q', aggregate = alt.ArgmaxDef(argmax='date')),
    text='Player')
    
    text = label.mark_text(align='left', dx=4)

    circle = label.mark_circle()
    
    st.altair_chart(line_chart + circle + text, use_container_width=True)
