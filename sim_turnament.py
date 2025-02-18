import csv
import random

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


def read_in_statistics_csv(path_csv) -> list:
    """Must be csv"""
    list_of_stats = []
    with open(path_csv, mode="r", newline="") as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            list_of_stats.append(row)

    return list_of_stats


def decks_in_turnament(statistics: list):
    list_of_decks = []

    for matchup in statistics:
        if matchup["deck_1"] not in list_of_decks:
            list_of_decks.append(matchup["deck_1"])
            continue
        elif matchup["deck_2"] not in list_of_decks:
            list_of_decks.append(matchup["deck_2"])
            continue
        else:
            continue

    return list_of_decks


def turnament_rounds(players: int):
    """gives how many rounds to play depending on how many players playing"""
    # first number is max players for that amount of rounds (two phase turnaments)
    turnament_struct = {
        8: 3,
        16: 4,
        32: 6,
        64: 7,
        128: 8,
        256: 9,
        512: 10,
        1024: 11,
        2048: 12,
        4096: 13,
        8192: 14,
    }

    for item, value in turnament_struct.items():
        if item >= players:
            return value


def create_standings(players):
    """takes players df and get the final group of matchups"""
    # Group players by their 'Current Score'
    score_groups = players.groupby("Current Score", group_keys=False)

    # List to handle odd players who can't be paired within their score group
    odd_players = []

    # Create an empty list to store the final grouped players
    final_groups = []

    # First, match players within each score group, from highest score down
    for score in sorted(score_groups.groups.keys(), reverse=True):
        group = score_groups.get_group(score)
        player_ids = group.index.tolist()
        random.shuffle(player_ids)
        group_matches = []

        # Match players in pairs
        while len(player_ids) > 1:
            player1 = player_ids.pop(0)
            player2 = player_ids.pop(0)
            group_matches.append((player1, player2))

        # If there's an odd player, they will get a point and move to the next group
        if player_ids:
            odd_players.append(player_ids[0])

        final_groups.append(group_matches)

    # Now, add odd players to the next highest group
    for odd_player in odd_players:
        if final_groups:
            # Add the odd player to the next group
            final_groups[-1].append(
                (odd_player, None)
            )  # Opponent is None, just give the point

    return final_groups


# Function to get the win percentage for a deck pair
def get_win_percentage(deck_1, deck_2, stats) -> int:
    for matchup in stats:
        if (matchup["deck_1"] == deck_1 and matchup["deck_2"] == deck_2) or (
            matchup["deck_1"] == deck_2 and matchup["deck_2"] == deck_1
        ):
            return int(matchup["win_perc"])
    return 50  # Default to 50% if no matchup found


def prep_turn_from_stats(path_csv):
    list_of_stats = read_in_statistics_csv(path_csv)
    list_of_decks = decks_in_turnament(list_of_stats)
    return list_of_decks, list_of_stats


def plot_winnings_proportions(players, inputs):
    # Group by 'Deck' and 'Current Score', and count how many players have each combination
    score_distribution = (
        players.groupby(["Deck", "Current Score"])
        .size()
        .reset_index(name="Player Count")
    )

    # -------------------------------
    # Get the total number of players per deck from the inputs
    # -------------------------------

    # Assuming 'decks' is a dictionary or list with the number of players per deck
    total_players_per_deck = {
        deck: players_count for deck, players_count in inputs.items()
    }

    # -------------------------------
    # Calculate the Proportion of Players per Score for each Deck
    # -------------------------------

    # Add a new column 'Proportion' which is 'Player Count' divided by total players for that deck
    score_distribution["Proportion"] = score_distribution.apply(
        lambda row: row["Player Count"] / total_players_per_deck[row["Deck"]],
        axis=1,
    )

    # -------------------------------
    # Reshape the data to get each deck as a column for each score
    # -------------------------------

    # Pivot the dataframe so that each 'Current Score' is a row and each 'Deck' is a column
    score_pivot = score_distribution.pivot_table(
        index="Current Score",
        columns="Deck",
        values="Proportion",
        aggfunc="sum",
        fill_value=0,
    )

    # -------------------------------
    # Create the Bar Chart using Matplotlib (better control within Streamlit)
    # -------------------------------

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot bars for each deck next to each other for each score
    score_pivot.plot(kind="bar", ax=ax, width=0.8)

    # Set chart labels and title
    ax.set_xlabel("Points", fontsize=14)
    ax.set_ylabel("Proportion of Players", fontsize=14)
    ax.set_title("Proportion of Players' Points per Deck", fontsize=16)

    # Display the plot in Streamlit
    st.pyplot(fig)


# Step 1: Load the data and process player matches
def load_and_filter_data():
    # Load the matches data
    df = pd.read_csv(
        "data_usa_turnament.csv",
        delimiter="\t",
        header=None,
        names=["Player1", "Player2", "Result", "Points", "Round"],
    )

    # Clean player names and extract country codes
    df["Player1_Country"] = df["Player1"].str.extract(r"\[(..)\]")
    df["Player1"] = df["Player1"].str.replace(r" \[..\]", "", regex=True)

    df["Player2_Country"] = df["Player2"].str.extract(r"\[(..)\]")
    df["Player2"] = df["Player2"].str.replace(r" \[..\]", "", regex=True)

    # Filter rows where player1 played more than 8 rounds
    filtered_rows = []  # Store rows that should be kept
    current_player = None
    player_rows = []  # Temporarily store each player's rows
    played_above_8 = False  # Track if the player has a round > 8

    for index, row in df.iterrows():
        if row["Player1"] != current_player:  # New player detected
            if (
                played_above_8
            ):  # Keep previous player's rows if they played >8 rounds
                filtered_rows.extend(player_rows)

            # Reset for the new player
            current_player = row["Player1"]
            player_rows = []
            played_above_8 = False

        # Store row and check if they played > 8 rounds
        player_rows.append(row)
        if row["Round"] > 8:
            played_above_8 = True

    if played_above_8:
        filtered_rows.extend(player_rows)

    df_filtered = pd.DataFrame(filtered_rows, columns=df.columns)

    return df_filtered


# Step 2: Load decks data
def load_deck_data():
    txt_file = "decks_players.txt"
    players_data = []

    with open(txt_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    i = 1
    while i < len(lines):
        if lines[i].strip().isdigit():  # Skip ranking numbers
            i += 1
            continue

        player_name = lines[i].strip()
        country = lines[i + 1].strip() if (i + 1) < len(lines) else ""
        deck = (
            lines[i + 2].strip()
            if (i + 2) < len(lines) and lines[i + 2].strip()
            else None
        )

        players_data.append([player_name, country, deck])
        i += 3  # Move to the next player's data

    df_decks = pd.DataFrame(
        players_data, columns=["Player", "Country", "Deck"]
    )

    return df_decks


# Step 3: Merge and clean data
def merge_decks_with_matches(df_filtered, df_decks):
    # Merge the decks with df_filtered on Player1
    df_filtered = df_filtered.merge(
        df_decks, left_on="Player1", right_on="Player", how="left"
    )

    # Drop the duplicate "Player" column
    df_filtered.drop(columns=["Player"], inplace=True)

    # Remove players without decks and matches where one player is invalid
    players_with_decks = df_filtered.dropna(
        subset=["Deck"]
    )  # Keep only players with a deck
    valid_players = set(players_with_decks["Player1"])

    df_filtered = df_filtered[
        df_filtered["Player1"].isin(valid_players)
        & df_filtered["Player2"].isin(valid_players)
    ]

    return df_filtered


# Step 4: Calculate match outcomes
def calculate_match_outcomes(df_filtered):
    df_filtered["MatchKey"] = df_filtered.apply(
        lambda row: tuple(sorted([row["Player1"], row["Player2"]])),
        axis=1,
    )

    # Keep only one instance of each match
    df_matches = df_filtered.drop_duplicates(subset="MatchKey").copy()
    df_matches.rename(columns={"Deck": "Deck1"}, inplace=True)

    # Merge Deck2 from Player2
    df_matches = df_matches.merge(
        df_filtered[["Player1", "Deck"]],
        left_on="Player2",
        right_on="Player1",
        how="left",
    )
    df_matches.rename(columns={"Deck": "Deck2"}, inplace=True)

    # Determine win/loss/tie outcome
    df_matches["Result"] = df_matches["Result"].fillna("T")
    df_matches["Win"] = (df_matches["Result"] == "W").astype(int)
    df_matches["Loss"] = (df_matches["Result"] == "L").astype(int)
    df_matches["Tie"] = (df_matches["Result"] == "T").astype(int)

    df_matches.dropna(subset=["Deck1", "Deck2"], inplace=True)

    return df_matches


# Step 5: Aggregate performance data
def aggregate_performance_data(df_matches):
    df_performance = (
        df_matches.groupby(["Deck1", "Deck2"])
        .agg(Wins=("Win", "sum"), Losses=("Loss", "sum"), Ties=("Tie", "sum"))
        .reset_index()
    )
    return df_performance


# Step 6: Visualize Data using Streamlit
def plot_performance_data(df_performance):
    # Step 1: Calculate the win percentage for each matchup
    df_performance["Win_Percentage"] = (
        df_performance["Wins"]
        / (
            df_performance["Wins"]
            + df_performance["Losses"]
            + df_performance["Ties"]
        )
        * 100
    )

    # Round the win percentages to integers and handle NaN values
    df_performance["Win_Percentage"] = (
        df_performance["Win_Percentage"].fillna(0).round(0).astype(int)
    )

    # Step 2: Create a pivot table to structure the data for plotting
    df_pivot = df_performance.pivot_table(
        index="Deck1",
        columns="Deck2",
        values="Win_Percentage",
        aggfunc="mean",
        fill_value=0,  # fill missing values with 0
    )

    # Ensure that the pivoted table is in integer format
    df_pivot = df_pivot.astype(int)

    st.dataframe(df_pivot)  # Display the pivot table in Streamlit

    # Step 3: Plot the heatmap for win percentages
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        df_pivot,
        annot=True,  # Annotate the heatmap with the values
        cmap="Blues",  # Choose color map
        fmt="d",  # Format the values as integers
        linewidths=0.5,  # Add a small border between cells
        cbar=True,  # Show the color bar
    )
    plt.title("Deck Match Win Percentage")
    st.pyplot(plt)  # Display the heatmap in Streamlit
