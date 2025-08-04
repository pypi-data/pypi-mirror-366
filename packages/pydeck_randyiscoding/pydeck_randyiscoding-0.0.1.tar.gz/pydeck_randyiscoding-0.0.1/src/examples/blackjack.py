# --------------------------------------------------------
# Name: Randy Easton
# Date: 8/2/2025
# Assignment: [Insert Assignment Name or Number Here]
# --------------------------------------------------------
# Purpose:
# Provide an example of pydeck in use. This Version will use only one deck.
# --------------------------------------------------------
import pydeck

# This is a Patch for the sole purpose of reassigning the face card values to accomadate the rules of blackjack
def blackjack_value(self, acehigh=False):
    if self.rank in ["Jack", "Queen", "King"]:
        return 10
    elif self.rank == "Ace":
        return 11 if acehigh else 1
    else:
        return int(self.rank)

# Monkey-patch Card.value
pydeck.src.pydeck_randyiscoding.card.value = blackjack_value




def main():
    wallet = 100
    bj = pydeck.Deck(gendeck=True) # Generated an instance of class and a New Deck at the same time

    while wallet > 0:
        if bj._getsize() < 15:
            bj._resetdeck()

        buy_in = valid_wager(wallet)

        user = bj.deal(2)
        dealer = [bj.draw()]
        dealer_facedown = bj.draw()

        print(f"User has: {user} and ${buy_in - wallet} in thier wallet")
        print(f"Dealer shows: {dealer[0]} and a face-down card")

        # Check for dealer blackjack
        if dealer_peek_blackjack(dealer[0], dealer_facedown):
            dealer.append(dealer_facedown)
            print(f"Dealer reveals hole card: {dealer_facedown}")
            print("Dealer has Blackjack!")
            if best_hand_value(user) == 21:
                print("Push! Both have Blackjack.")
                # No win or loss
            else:
                print("You lose.")
                wallet -= buy_in
            again = input("Play another hand? (y/n): ").lower()
            if again != "y":
                print("Thanks for playing!")
                break
            else:
                continue

        # Continue regular game flow
        payout, result = blackjackhand(bj, user, buy_in, dealer, dealer_facedown)
        wallet += payout
        print(result)

        again = input("Play another hand? (y/n): ").lower()
        if again != "y":
            print("Thanks for playing!")
            break

    print("You're out of money! Game over.") if wallet <= 0 else None


    '''
    face cards are worth an increasing number of points
    Jack = 11 to King = 13 & Ace = 14 if 'acehigh' is set to true otherwise its set to 1
    For the purposes of blackjack I used a "Monkey Patch" to change face card values to 10.
    In this case: Ace = 11 if 'acehigh' is set to true otherwise its set to 1
    '''




# Function definitions go here
# Use descriptive names and explain any non-obvious logic
# Example:
def blackjackhand(bj, user, buy_in, dealer, dealer_facedown):
    """
    Plays out a full hand of Blackjack between the user and dealer.
    Returns the payout amount and a result string.
    """
    if check_for_natural_21(user,buy_in,dealer, dealer_facedown) == 0:
        dealer.append(dealer_facedown)
        dealer_value = best_hand_value(dealer)
        user_value = best_hand_value(user)
        while dealer_value < 16:
            dealer.append(bj.draw())
            dealer_value = _hand_value(dealer)
            if dealer_value > 21:
                print("Player wins")
        while user_value < 21:
            print(f"User has {user}")
            #for any()
            play = input("[S]tand or [H]it?")
            match play.capitalize():
                case "S":
                    break
                case "H":
                    user.append(bj.draw())
                    user_value = best_hand_value(user)
        if user_value < 21:
            if user_value > dealer_value:
                return 2 * buy_in, "Player wins"
            else:
                return 0, "Dealer Wins"
    elif check_for_natural_21(user,buy_in,dealer,dealer_facedown) == 1.5 * buy_in:
        for card in user + dealer + [dealer_facedown]:
            bj.discard(card)
        return 1.5 * buy_in,"You won this Hand"
    else:
        for card in user + dealer + [dealer_facedown]:
            bj.discard(card)
        return buy_in, "Tie"
    for card in user + dealer + [dealer_facedown]:
        bj.discard(card)

def valid_wager(wallet): # Checks if wager is valid
    while True:
        try:
            wager = int(input("Enter your wager: "))
            if 1 <= wager <= wallet:
                return wager
            else:
                print(f"Wager must be between 1 and {wallet}.")
        except ValueError:
            print("Please enter a valid number.")
def best_hand_value(hand): # Determine if hand that is being played should be W/ High or Low Ace
    high = _hand_value(hand, acehigh=True)
    if high <= 21:
        return high
    return _hand_value(hand, acehigh=False)


def _hand_value(hand, acehigh=False):
    return sum(blackjack_value(card, acehigh) for card in hand)

def check_for_natural_21(user, bet, dealer, dealer_facedown):
    ranks = [card.rank for card in user]
    if "Ace" in ranks and any(r in ["10", "Jack", "Queen", "King"] for r in ranks):
        dealer_ranks = [dealer[0].rank, dealer_facedown.rank]
        if "Ace" in dealer_ranks and any(r in ["10", "Jack", "Queen", "King"] for r in dealer_ranks):
            return int(bet)  # Push
        else:
            return int(1.5 * bet)
    return 0  # Not natural 21

def dealer_peek_blackjack(dealer_upcard, dealer_downcard):
    """Returns True if dealer has blackjack with an Ace or 10-value card showing"""
    # Check if either card is an Ace and the other is worth 10
    return (
        (dealer_upcard.rank == "Ace" and blackjack_value(dealer_downcard) == 10) or
        (dealer_downcard.rank == "Ace" and blackjack_value(dealer_upcard) == 10)
    )



# Program starts here
if __name__ == "__main__":
    main()
