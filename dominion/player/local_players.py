from abc import abstractmethod
from .player_handle import PlayerHandle
from collections import defaultdict
import time


class LocalPlayerHandle(PlayerHandle):
    def __init__(self, name):
        super().__init__(name)

        self.my_turn = False
        self.is_action_phase = False

        self.turn_number = 0

        self.actions = 0
        self.coins = 0
        self.buys = 0

        self.hand = {}
        self.cards_in_play_area = defaultdict(int)
        self.cards_in_discard = defaultdict(int)
        self.cards_in_discard['copper'] = 7
        self.cards_in_discard['estate'] = 3
        self.cards_in_deck = defaultdict(int)

        self.last_card_played = None

        self.total_of = {}
        self.num_left_of = {}
        self.cost_of = {}
        self.is_action = {}

        self.num_of = defaultdict(int)
        self.num_of['copper'] = 7
        self.num_of['estate'] = 3

        self.choices = []
        self.answers = []

    def notify_joined_game(self, supply_piles, card_costs, card_is_action):
        self.total_of = supply_piles.copy()
        self.total_of['copper'] += 14
        self.total_of['estate'] += 6
        self.num_left_of = supply_piles
        self.cost_of = card_costs
        self.is_action = card_is_action

    def notify_started_action_phase(self, player):
        self.my_turn = player == self.name
        self.is_action_phase = True
        self.last_card_played = None

        if player == self.name:
            self.turn_number += 1
            if self.can_play_anything():
                self.action_phase()
            self.finish_action_phase()

    @abstractmethod
    def action_phase(self):
        pass

    def notify_started_buy_phase(self, player):
        self.is_action_phase = False
        self.last_card_played = None

        if player == self.name:
            if self.can_buy_anything():
                self.buy_phase()
            self.finish_turn()

    @abstractmethod
    def buy_phase(self):
        pass

    def notify_gained_actions(self, player, amount):
        if self.name == player:
            self.actions += amount

    def notify_gained_buys(self, player, amount):
        if self.name == player:
            self.buys += amount

    def notify_gained_coins(self, player, amount):
        if self.name == player:
            self.coins += amount

    def notify_gained_card_to_hand(self, player, card):
        if self.name == player:
            if card not in self.hand:
                self.hand[card] = 0
            self.hand[card] += 1

    def notify_took_card_from_hand(self, player, card):
        if self.name == player:
            self.hand[card] -= 1
            if self.hand[card] == 0:
                del self.hand[card]

    def notify_gained_card_to_deck(self, player, card):
        if self.name == player:
            self.cards_in_deck[card] += 1

    def notify_took_card_from_deck(self, card):
        self.cards_in_deck[card] -= 1

    def notify_gained_card_to_discard(self, player, card):
        if self.name == player:
            self.cards_in_discard[card] += 1

    def notify_took_card_from_discard(self, player, card):
        if self.name == player:
            self.cards_in_discard[card] -= 1

    def notify_played_card(self, player, card):
        self.last_card_played = card

        if self.name == player:
            self.cards_in_play_area[card] += 1

    def notify_took_card_from_play_area(self, card):
        self.cards_in_play_area[card] -= 1

    def notify_card_bought(self, card):
        self.num_left_of[card] -= 1
        if self.my_turn:
            self.num_of[card] += 1

    def notify_trashed_card(self, player, card):
        if self.name == player:
            self.num_of[card] -= 1

    def can_play_anything(self):
        return self.actions > 0 and len(self.cards_can_play()) > 0

    def can_play(self, card_name):
        return card_name in self.cards_can_play()

    def cards_can_play(self):
        return list(filter(lambda card_name: self.is_action[card_name], self.hand))

    def can_buy_anything(self):
        return self.buys > 0 and len(self.cards_can_buy()) > 0

    def can_buy(self, card_name):
        return card_name in self.cards_can_buy()

    def cards_can_buy(self):
        return list(
            filter(lambda card_name: self.num_left_of[card_name] > 0 and self.cost_of[card_name] <= self.coins,
                   self.num_left_of))


class ConsolePlayer(LocalPlayerHandle):
    def __init__(self):
        super().__init__('Player')

    def notify_joined_game(self, supply_piles, card_costs, card_is_action):
        super().notify_joined_game(supply_piles, card_costs, card_is_action)
        print('Joined game: {}'.format(supply_piles))

    def notify_player_joined(self, player):
        super().notify_player_joined(player)
        print('{} joined the game.'.format(player))

    def notify_started_game(self):
        super().notify_started_game()
        print('Game started!')

    def notify_finished_game(self, game_results):
        print('Game finished!')
        print(game_results)

    def notify_trashed_card(self, player, card):
        super().notify_trashed_card(player, card)
        print('{} trashed a {}'.format(player, card))

    def notify_played_card(self, player, card):
        super().notify_played_card(player, card)
        print('{} played {}'.format(player, card))

    def notify_card_bought(self, card):
        super().notify_card_bought(card)
        print('{} was bought.'.format(card))

    def action_phase(self):
        while self.can_play_anything():
            print('Actions: {}, Hand: {}'.format(self.actions, self.hand))
            if not self.ask_yes_or_no('Play action? {}'.format(self.cards_can_play())):
                break

            self.play(self.choose_card_from(self.cards_can_play()))

    def buy_phase(self):
        while self.can_buy_anything():
            print('Buys: {}, Coins: {}, Supply: {}'.format(self.buys, self.coins, self.num_left_of))
            if not self.ask_yes_or_no('Buy card? {}'.format(self.cards_can_buy())):
                break

            self.buy(self.choose_card_from(self.cards_can_buy()))

    def choose_card_from(self, collection):
        while True:
            card_name = input('Choose card from: {}'.format(collection)).strip()
            if card_name in collection:
                return card_name

    def ask_yes_or_no(self, prompt):
        while True:
            answer = input(prompt).strip()
            if answer == 'y':
                return True
            elif answer == 'n':
                return False


class AIPlayer(LocalPlayerHandle):
    @abstractmethod
    def requires(self):
        return []
