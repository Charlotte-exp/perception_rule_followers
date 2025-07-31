from otree.api import *

import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'dice_task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5

    zero_points = cu(0)
    one_points = cu(1)
    two_points = cu(2)
    three_points = cu(3)


class Subsession(BaseSubsession):
    pass

def creating_session(subsession):
    """
    Pairs of original and reported dice from the prolific pilot.
    Must be called from a separate page or in the creating_session
    """
    for p in subsession.get_players():
        p.dice_roll()


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    original_dice = models.IntegerField(blank=True)
    reported_dice = models.IntegerField(blank=True)

    original_dice_1 = models.IntegerField(initial=0)
    reported_dice_1 = models.IntegerField(
        initial=0,
        choices=[
            [1, f'value 1'], [2, f'value 2'], [3, f'value 3'],
            [4, f'value 4'], [5, f'value 5'], [6, f'value 6'],
        ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    original_dice_2 = models.IntegerField(initial=0)
    reported_dice_2 = models.IntegerField(
        initial=0,
        choices=[
            [1, f'value 1'], [2, f'value 2'], [3, f'value 3'],
            [4, f'value 4'], [5, f'value 5'], [6, f'value 6'],
        ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    original_dice_3 = models.IntegerField(initial=0)
    reported_dice_3 = models.IntegerField(
        initial=0,
        choices=[
            [1, f'value 1'], [2, f'value 2'], [3, f'value 3'],
            [4, f'value 4'], [5, f'value 5'], [6, f'value 6'],
        ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    original_dice_4 = models.IntegerField(initial=0)
    reported_dice_4 = models.IntegerField(
        initial=0,
        choices=[
            [1, f'value 1'], [2, f'value 2'], [3, f'value 3'],
            [4, f'value 4'], [5, f'value 5'], [6, f'value 6'],
        ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    original_dice_5 = models.IntegerField(initial=0)
    reported_dice_5 = models.IntegerField(
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
        min=0, max=C.one_points*3)

    send_back_2 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=C.two_points*3)

    send_back_3 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=C.three_points*3)

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

    # ### for one round version ###
    # def dice_roll(player):
    #     """
    #     Pairs of original and reported dice from the prolific pilot.
    #     could also be attributed to all participants when the session is created but then must be in the creating_session of the first app...
    #     """
    #     dice_values = list(range(1, 7))
    #     og_dice = random.choice(dice_values)
    #     player.original_dice = og_dice
    #     print(player.original_dice)
    #     return player.original_dice

    def dice_roll(player):
        dice_values = [random.randint(1, 6) for _ in range(C.NUM_ROUNDS)]

        # Save each value to the corresponding player field
        for i, value in enumerate(dice_values, start=1):
            setattr(player, f'original_dice_{i}', value)
            # print(f'original_dice_{i}', value)



######## FUNCTIONS #########



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
        reported_dice_field = f'reported_dice_{player.round_number}'
        reported_dice = getattr(player, reported_dice_field, None)  # Default to None if not set
        original_dice_field = f'original_dice_{player.round_number}'
        original_dice = getattr(player, original_dice_field, None)
        return dict(
            original_dice = original_dice,
            reported_dice = reported_dice,
        )

    def before_next_page(player, timeout_happened):
        round_field = f'reported_dice_{player.round_number}'
        setattr(player, round_field, player.reported_dice)

class TrustGame(Page):
    form_model = "player"
    # def get_form_fields(player: Player):
    #     if player.round_number == 1:
    #         return ['send_back_1']
    #     elif player.round_number == 2:
    #         return ['send_back_2']
    #     elif player.round_number == 3:
    #         return ['send_back_3']
    #     elif player.round_number == 4:
    #         return ['send_back_4']
    #     return None

    ### if only one trust game use this ###
    form_fields = ["send_back_1", "send_back_2", "send_back_3"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            zero_points_tripled = C.zero_points,
            one_points_tripled = C.one_points,
            two_points_tripled = C.two_points,
            three_points_tripled = C.three_points,
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
