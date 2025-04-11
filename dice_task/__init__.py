from otree.api import *

import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'dice_task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    original_dice = models.IntegerField(initial=0)
    reported_dice = models.IntegerField(
        initial=0,
        choices=[
            [1, f'value 1'], [2, f'value 2'], [3, f'value 3'],
            [4, f'value 4'], [5, f'value 5'], [6, f'value 6'],
        ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    send_back_1 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=10)

    send_back_2 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=10)

    send_back_3 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=10)

    send_back_4 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=10)

    send_back_5 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=10)

    q1 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'],
        ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    q2 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'],
        ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    def dice_roll(player):
        """
        Pairs of original and reported dice from the prolific pilot.
        could also be attributed to all participants when the session is created but then must be in the creating_session of the first app...
        """
        dice_faces = list(range(1, 7))
        og_dice = random.choice(dice_faces)
        player.original_dice = og_dice
        print(player.original_dice)
        return player.original_dice


######## FUNCTIONS #########

# def creating_session(subsession):
#     """
#
#     """
#     order = itertools.cycle(['treatment-control', 'control-treatment'])
#     for p in subsession.get_players():
#         p.balanced_order = next(order)
#         p.participant.balanced_order = p.balanced_order
#         if subsession.round_number <= C.half_rounds:
#             # First half of the rounds
#             p.treatment = 'treatment' if p.balanced_order == 'treatment-control' else 'control'
#             p.part_round_number = subsession.round_number
#         else:
#             # Second half of the rounds
#             p.treatment = 'control' if p.balanced_order == 'treatment-control' else 'treatment'
#             p.part_round_number = subsession.round_number-C.half_rounds


######### PAGES #########

class Consent(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Instructions(Page):
    form_model = "player"
    form_fields = ["q1", "q2"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Dice(Page):
    form_model = "player"
    form_fields = ["reported_dice"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            dice_roll = player.dice_roll(),
            original_dice = player.original_dice,
        )

class TrustGame(Page):
    form_model = "player"
    form_fields = ["send_back_1", "send_back_2", "send_back_3", "send_back_4", "send_back_5", ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
        )

class End(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

class ProlificLink(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Consent,
                 Instructions,
                 Dice,
                 TrustGame,
                 End,
                 Payment,
                 ProlificLink]
