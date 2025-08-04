# --------------------------------------------------------
# Name: Randy Easton
# Date: 8/1/2025
# Assignment: [Insert Assignment Name or Number Here]
# --------------------------------------------------------
# Purpose:
# Handles creation of a deck of playing cards, deals that deck and allows for discarding cards from hand
# --------------------------------------------------------

from . import properties as p
from . import card as c
import random
class Deck():
    def __init__(self, gendeck=False):
        self.deck = []
        self.discard = []
        self.cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']

        if gendeck:
            self.new_deck()
    def new_deck(self):
        for suits in p.Suits:
            for rank in self.cards:
                x = c.Card(rank, suits.name)
                self.deck.append(x)
        random.shuffle(self.deck)
        return self.deck

    def deal(self, num):
        deal = []
        if not self.deck or num > len(self.deck):
            raise p.EmptyDeck("Deck is Empty, or Not enough Cards to draw from in deck. Try using the Discard Pile")
        else:
            for x in range(num):
                deal.append(self.deck.pop(0))
                x +=1
        return deal

    def draw(self):
        return self.deal(1)[0]

    def discard_pile(self, card):
        self.discard.append(card)
    def _getsize(self):
        return len(self.deck)

    def _resetdeck(self):
        self.deck = self.discard.copy()
        random.shuffle(self.deck)
        self.discard = []
        return self.deck




#
# game = Deck()
#
# game.new_deck()
#
# user = game.deal(2)
# pc = game.deal(2)
#
# print(f'The user has {user} in thier hand')
# print(f'The PC has {pc} in thier hands')
#
# user.append(game.draw())
# print(f'The user has {user} in thier hand')

