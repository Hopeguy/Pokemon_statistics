import pandas as pd
import numpy as np
import time
import plotly.express as px

class Deck():
    def __init__(self, deck_size, num_cards_in_deck):
        assert num_cards_in_deck < 5 and num_cards_in_deck > 0, "less then 1 card, or more than 4 cards in deck"
        deck = np.zeros(deck_size-num_cards_in_deck,dtype=int)
        deck = np.append((deck), values= np.ones(num_cards_in_deck,dtype=int))
        self.deck_size = len(deck)
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



def main():
    global df
    start = time.time()
    Result_list = []
    for card_quantity in range(4):
        Test_size = 1000 #number of times the test is run
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
    
    df = pd.DataFrame(Result_list, columns=["1 copy","2 copies","3 copies","4 copies"], index = ["1","2","3","4"])
    df  = df.fillna(0)
    print(df)
    fig = px.bar(df, text_auto = True, title = "Chance of card being in prizes %", 
                labels = {"'1 copy', '2 copies', '3 copies', '4 copies'": "Cards in deck"})
    
    fig.show()

    end = time.time()
    print(f'Runtime: {end-start} seconds')


if __name__ == "__main__":
    
    main()
