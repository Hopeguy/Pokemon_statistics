import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import sim_turnament as sim


class Deck:
    def __init__(self, deck_size, num_cards_in_deck):
        # assert num_cards_in_deck < 5 and num_cards_in_deck > 0, "less then 1 card, or more than 4 cards in deck"
        deck = np.zeros(deck_size - num_cards_in_deck, dtype=int)
        deck = np.append((deck), values=np.ones(num_cards_in_deck, dtype=int))

        self.deck = deck

    def rand_deck(self):
        np.random.shuffle(self.deck)

    def draw_start(self):
        self.hand = self.deck[0:7]
        self.deck = np.delete(self.deck, range(7))

    def set_prizes(self):
        self.prizes = self.deck[0:6]
        self.deck = np.delete(self.deck, range(6))

    def check_card_in_prizes(self):
        counter = 0  # counts how many of the specific card is in the prizes
        for card in self.prizes:
            assert isinstance(card, np.int64)
            if card == 1:
                counter += 1
            else:
                pass

        return counter

    def draw_one(self):
        self.hand += self.deck[0]
        self.deck = np.delete(self.deck, range(1))

    def check_cards_in_hand(self):
        counter = 0  # counts how many "supporters" in hand, int with value 1 in the list
        for card in self.hand:
            if card == 1:
                counter += 1
            else:
                pass

        return counter


def main():
    st.header("Pokemon Statistics")
    # Calculats chanes of cards being in prizes

    cards_in_prizes_tab, Supp_tab, turnament_tab = st.tabs(
        [
            "Cards in prize",
            "Chanes of starting with a supporter in hand",
            "turnament simulation",
        ]
    )

    with cards_in_prizes_tab:
        st.header("Cards in prizes")

        Result_list = []
        for card_quantity in range(4):
            Test_size = 10000  # number of times the test is run
            Result = np.zeros(Test_size, dtype=int)
            deck_size = 60
            Specific_card_quantity = card_quantity + 1
            for i in range(Test_size):
                deck = Deck(deck_size, Specific_card_quantity)
                deck.rand_deck()
                deck.draw_start()
                deck.set_prizes()
                Result[i] = deck.check_card_in_prizes()

            # checks how many of the specific card that ended up in the prizes
            number_times_in_prizes = np.zeros(card_quantity + 1)
            for index, i in enumerate(number_times_in_prizes):
                number_times_in_prizes[index] = (
                    np.count_nonzero(Result >= index + 1) / Test_size
                ) * 100

            Result_list.append(number_times_in_prizes)
            # print(f'Percentage times card is in prizes {(number_times_in_prizes/Test_size)*100} %')

        index = ["1", "2", "3", "4"]
        df = pd.DataFrame(
            Result_list,
            columns=[
                "1 copy in deck",
                "2 copies in deck",
                "3 copies in deck",
                "4 copies in deck",
            ],
            index=index,
        )
        df = df.fillna(0)
        fig = px.bar(
            df,
            text_auto=True,
            title="Chance of card/s being in prizes %",
            labels={
                "'1 copy', '2 copies', '3 copies', '4 copies'": "Cards in deck"
            },
        )
        fig.update_xaxes(title="Card/s in prizes")

        st.plotly_chart(fig)

    with Supp_tab:
        # Calculates the chances of starting with a supporter in hand<
        st.header(
            "Chance of having a supporter in the starting hand plus draw after prices"
        )
        num_supp = st.slider(
            "How many supporters in the deck (1-20)?",
            min_value=1,
            max_value=20,
        )
        Test_size = 1000  # number of times the test is run
        Result2 = np.zeros(
            Test_size, dtype=int
        )  # %of times a supporter was in the starting hand
        deck_size = 60
        for i in range(Test_size):
            deck = Deck(deck_size, num_supp)
            deck.rand_deck()
            deck.draw_start()
            deck.set_prizes()
            deck.draw_one()
            Result2[i] = deck.check_cards_in_hand()

        final_result = (np.count_nonzero(Result2) / Test_size) * 100
        st.write(final_result)

    with turnament_tab:
        decks, stats = sim.prep_turn_from_stats("turnament_stats.csv")
        inputs = {}
        for string in decks:
            # Create a number input box for each string
            input_value = st.number_input(
                f"Players playing {string}", min_value=0, step=1
            )

            # Store the input value in the dictionary
            inputs[string] = input_value

        total_players = sum(inputs.values())
        # rounds needed (depends on the amount of players)
        rounds = sim.turnament_rounds(total_players)
        st.write(f"number of rounds for {total_players} Players = {rounds}")

        # run simulation of the turnament
        if st.button("Submit"):
            st.write("runnning simulation")
            # Initialize an empty list to hold the data for the DataFrame
            data = []

            # Loop through the inputs and create rows for each deck
            for deck, score in inputs.items():
                for _ in range(score):
                    data.append([deck, 0])

            # Create a DataFrame from the data list
            players = pd.DataFrame(data, columns=["Deck", "Current Score"])
            # Set the index to be player_id (a range of numbers)
            players.index.name = "player_id"
            # progressbar
            progress_bar = st.progress(0)
            round_counter = 0
            for round in range(rounds):
                players[f"round_{round}_opp"] = (
                    None  # Initialize the new column
                )
                round_standings = sim.create_standings(players)
                # Now simulate matches and calculate outcomes for each unique pair
                for group_matches in round_standings:
                    for player1, player2 in group_matches:
                        if player2 is None:
                            # The last odd player wins automatically
                            players.at[player1, f"round_{round}_opp"] = (
                                "No opp"
                            )
                            players.at[player1, "Current Score"] += 1
                        else:
                            # Calculate the win percentage between the decks
                            player1_deck = players.at[player1, "Deck"]
                            player2_deck = players.at[player2, "Deck"]
                            win_percentage = sim.get_win_percentage(
                                player1_deck, player2_deck, stats
                            )

                            # Simulate match outcome (win/loss) based on the win_percentage
                            if random.random() < win_percentage / 100:
                                players.at[player1, "Current Score"] += (
                                    3  # Player1 wins
                                )
                                players.at[player2, "Current Score"] += (
                                    0  # Player2 loses
                                )
                                # Store the matchup information in the round_{round}_opp column
                                players.at[player1, f"round_{round}_opp"] = (
                                    f"Player {player2} (Deck: {player2_deck}): Win"
                                )
                                players.at[player2, f"round_{round}_opp"] = (
                                    f"Player {player1} (Deck: {player1_deck}): Lose"
                                )
                            else:
                                players.at[player2, "Current Score"] += (
                                    3  # Player2 wins
                                )
                                players.at[player1, "Current Score"] += (
                                    0  # Player1 loses
                                )
                                # Store the matchup information in the round_{round}_opp column
                                players.at[player1, f"round_{round}_opp"] = (
                                    f"Player {player2} (Deck: {player2_deck}): Lose"
                                )
                                players.at[player2, f"round_{round}_opp"] = (
                                    f"Player {player1} (Deck: {player1_deck}): Win"
                                )

                round_counter += 1
                progress_bar.progress(round_counter / rounds)

            st.dataframe(
                players.sort_values(by="Current Score", ascending=False)
            )
            st.write("finished")
            # 1. Total points for each deck (sorted from highest to lowest)
            deck_points = (
                players.groupby("Deck")["Current Score"].sum().reset_index()
            )
            deck_points = deck_points.rename(
                columns={"Current Score": "Total Points"}
            )
            deck_points = deck_points.sort_values(
                by="Total Points", ascending=False
            )  # Sort by Total Points (desc)

            # 2. Top 8 players (sorted from highest to lowest)
            top_8_players = players.nlargest(8, "Current Score")[
                ["Deck", "Current Score"]
            ].reset_index(drop=True)
            top_8_players = top_8_players.sort_values(
                by="Current Score", ascending=False
            )  # Sort top 8 by score (desc)

            # Display the sorted dataframes in Streamlit
            st.write("Total Points per Deck (sorted from highest to lowest):")
            st.dataframe(deck_points)

            st.write("Top 8 Players (sorted from highest to lowest):")
            st.dataframe(top_8_players)

            # plot the proportional deck usages to points
            sim.plot_winnings_proportions(players, inputs)


if __name__ == "__main__":
    main()
