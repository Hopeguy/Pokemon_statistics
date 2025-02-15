import csv
import random

import matplotlib.pyplot as plt
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
