import pandas as pd
import numpy as np
import time
import plotly.express as px
import streamlit as st

class Deck():
    def __init__(self, deck_size, num_cards_in_deck):
        #assert num_cards_in_deck < 5 and num_cards_in_deck > 0, "less then 1 card, or more than 4 cards in deck"
        deck = np.zeros(deck_size-num_cards_in_deck,dtype=int)
        deck = np.append((deck), values= np.ones(num_cards_in_deck,dtype=int))
        
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
        counter = 0 #counts how many of the specific card is in the prizes
        for card in self.prizes:
            assert type(card) == np.int32, "This is not an Interger"
            if card == 1:
                counter += 1
            else:
                pass
        
        return counter
    
    def draw_one(self):
        self.hand += self.deck[0]
        self.deck = np.delete(self.deck, range(1))

    def check_cards_in_hand(self):
        counter = 0 #counts how many "supporters" in hand, int with value 1 in the list
        for card in self.hand:
            if card == 1:
                counter += 1
            else:
                pass

        return counter



def main():
    st.header("Pokemon Statistics")
    #Calculats chanes of cards being in prizes

    cards_in_prizes_tab, Supp_tab = st.tabs(["Cards in prize", "Chanes of starting with a supporter in hand"])

    with cards_in_prizes_tab:
        st.header("Cards in prizes")

        Result_list = []
        for card_quantity in range(4):
            Test_size = 10000 #number of times the test is run
            Result = np.zeros(Test_size, dtype=int)
            deck_size = 60
            Specific_card_quantity = card_quantity +1
            for i in range(Test_size):

                deck = Deck(deck_size,Specific_card_quantity)
                deck.rand_deck()
                deck.draw_start()
                deck.set_prizes()
                Result[i] = deck.check_card_in_prizes()

            #checks how many of the specific card that ended up in the prizes    
            number_times_in_prizes = np.zeros(card_quantity+1)
            for index, i in enumerate(number_times_in_prizes):
                number_times_in_prizes[index] = (np.count_nonzero(Result >= index + 1)/Test_size)*100

            Result_list.append(number_times_in_prizes)
            #print(f'Percentage times card is in prizes {(number_times_in_prizes/Test_size)*100} %')
        
        index = ["1","2","3","4"]
        df = pd.DataFrame(Result_list, columns=["1 copy in deck","2 copies in deck","3 copies in deck","4 copies in deck"], index = index)
        df  = df.fillna(0)
        fig = px.bar(df, text_auto = True, title = "Chance of card being in prizes %", 
                    labels = {"'1 copy', '2 copies', '3 copies', '4 copies'": "Cards in deck"})
        fig.update_xaxes(title="Card/s in prizes")



        st.plotly_chart(fig)

    with Supp_tab:
        #Calculates the chances of starting with a supporter in hand<
        st.header("Chance of having a supporter in the starting hand plus draw after prices")
        num_supp = st.slider("How many supporters in the deck?", min_value=1, max_value=20)
        Test_size = 1000 #number of times the test is run
        Result2 = np.zeros(Test_size, dtype=int) # %of times a supporter was in the starting hand
        deck_size = 60
        for i in range(Test_size):
            deck = Deck(deck_size,num_supp)
            deck.rand_deck()
            deck.draw_start()
            deck.set_prizes()
            deck.draw_one()
            Result2[i] = deck.check_cards_in_hand()

        final_result = (np.count_nonzero(Result2)/Test_size) * 100
        st.write(final_result)

        



if __name__ == "__main__":
    
    main()
