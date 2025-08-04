# --------------------------------------------------------
# Name: Randy Easton
# Date: 8/1/2025
# Assignment: [Insert Assignment Name or Number Here]
# --------------------------------------------------------
# Purpose:
# [Brief one-sentence description of what the program does]
# --------------------------------------------------------

from enum import Enum

class Suits(Enum):
    hearts = 1
    clubs = 2
    diamonds = 3
    spades = 4

class EmptyDeck(Exception):
    def __init__(self, Message):
        self.message = Message
        super().__init__(self.message)
