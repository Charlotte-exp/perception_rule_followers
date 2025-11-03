from otree.api import *

import random
import itertools

from interactive_task import TrustGameBack

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'dice_task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 3
    participant_fee = 1
    time = 10

    num_dice_rounds = NUM_ROUNDS # from the actor task
    percent_accurate = 10
    bonus = cu(2)

    conversion = '34p'
    zero_points = cu(0)
    one_points = cu(1)
    two_points = cu(2)
    three_points = cu(3)

    DG_points = cu(6)


class Subsession(BaseSubsession):
    pass

def creating_session(subsession):
    """
    create a fixed sequence of 10 elements for each player bu calling generate_k_sequence function.
    Stored in a participant.vars since player field cannot be lists (and I don't need it in the database).
    Because creating_session calls the function every round
    we force it not to do that by setting a value based on round number instead.
    """
    subsession.session.num_dice_rounds = C.NUM_ROUNDS

    treatments = itertools.cycle(['TG', 'DG', 'rating', 'control'])
    for p in subsession.get_players():
        p.treatment = next(treatments)
        p.participant.treatment = p.treatment

    if subsession.round_number == 1:
        for p in subsession.get_players():
            sequence = generate_dice_sequence()
            p.participant.vars['sequence'] = sequence
            # set first round value directly
            p.original_dice = sequence[0]
    else:
        for p in subsession.get_players():
            # for rounds >1, just pick from participant.vars
            p.original_dice = p.participant.vars['sequence'][p.round_number - 1]


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    treatment = models.StringField()

    original_dice = models.IntegerField(blank=True)
    reported_dice = models.IntegerField(
        initial=0,
        choices=[
            [1, f'value 1'], [2, f'value 2'], [3, f'value 3'],
            [4, f'value 4'], [5, f'value 5'], [6, f'value 6'],
        ],
        widget=widgets.RadioSelect,
    )

    q1_failed_attempts = models.IntegerField(initial=0)
    q_treatment_failed_attempts = models.IntegerField(initial=0)

    q1 = models.IntegerField(
        initial=0,
        choices=[
            [1, f'I will be paid the number I roll from one randomly selected die roll.'],
            [2, f'I will be paid the number I report from one randomly selected die roll.'],
            [3, f'I will be paid the number I roll from all {C.NUM_ROUNDS} die rolls summed up.'],
            [4, f'I will be paid the number I report from all {C.NUM_ROUNDS} die rolls summed up.'],
        ],
        verbose_name='What determines the number of bonus points you will be paid from the dice roll?',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )


    q_treatment = models.IntegerField(
        initial=0,
        choices=[
            [1, f'They can share points with you.'],
            [2, f'They are asked to rate how trustworthy they find you.'],
            [3, f'They can take away your points, which are then tripled by the computer.'],
            [4, f'They can send you points, which are then tripled by the computer, and you can choose to send some back to them.'],
        ],
        verbose_name='What can the other participant do after learning how many times you reported the correct number?',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    random_roll = models.StringField(
        initial='',
        choices=['roll', 'whatever'],
    )

    randomly_selected_round = models.IntegerField(initial=0)
    randomly_selected_reported_dice = models.IntegerField(initial=0)

    send_back_1 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=9)

    send_back_2 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=9)

    send_back_3 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=9)


######## FUNCTIONS #########

def generate_dice_sequence():
    """
    Generate a random sequence of C.NUM_ROUNDS numbers.
    One different sequence is assigned to a player at creating_session
    """
    # dice_values = [random.randint(1, 6) for _ in range(C.NUM_ROUNDS)]
    sequence = [random.randint(1, 6) for _ in range(C.NUM_ROUNDS)]
    return sequence


def calculate_k(player: Player):
    list_of_correct = []
    for p in player.in_all_rounds():
        if p.reported_dice - p.original_dice <= 0: # if value 0 or neg, it's an honest answer
            value = 1 # 1 for honest
        else:
            value = 0 # 0 for lies
        list_of_correct.append(value)
        p.participant.k_list = list_of_correct
        # k_value = sum(list_of_correct)
        # p.participant.k_value = k_value


def random_payment(player: Player):
    """
    This function selects one round among all with equal probability.
    It records the value of each variable on this round as new random_variable fields
    """
    # number_of_rounds = player.session.num_dice_rounds
    number_of_rounds = C.NUM_ROUNDS
    randomly_selected_round = random.randint(1, number_of_rounds)
    me = player.in_round(randomly_selected_round)
    player.randomly_selected_round = randomly_selected_round
    player.participant.randomly_selected_round = randomly_selected_round

    attributes = ['reported_dice']
    for attr in attributes:
        value = getattr(me, attr)
        setattr(player, f'randomly_selected_{attr}', value)
        setattr(player.participant, f'randomly_selected_{attr}', value)



######### PAGES #########

class Consent(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Introduction(Page):
    form_model = "player"
    # form_fields = ["q1"]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True
        return None


class InstruPart1(Page):
    form_model = "player"

    def get_form_fields(player: Player):
        if player.treatment == 'control':
            return ['q1']
        else:
            return ['q1', 'q_treatment']

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True
        return None

    @staticmethod
    def error_message(player: Player, values):
        """
        records the number of time the page was submitted with an error. which specific error is not recorded.
        """
        # solutions = dict(q1=2, q_treatment=1)
        if player.treatment == 'TG':
            solutions = dict(q1=2, q_treatment=4)
        elif player.treatment == 'DG':
            solutions = dict(q1=2, q_treatment=1)
        elif player.treatment == 'rating':
            solutions = dict(q1=2, q_treatment=2)
        else:
            solutions = dict(q1=2)

        # error_message can return a dict whose keys are field names and whose values are error messages
        errors = {}
        for question, correct_answer in solutions.items():
            print(f"Treatment: {player.treatment}")
            print(f"Solutions: {solutions}")
            if values[question] != correct_answer:
                errors[question] = 'This answer is wrong'
                # Increment the specific failed attempt counter for the incorrect question
                failed_attempt_field = f"{question}_failed_attempts"
                if hasattr(player, failed_attempt_field):  # Ensure the field exists
                    setattr(player, failed_attempt_field, getattr(player, failed_attempt_field) + 1)

        if errors:
            return errors
        return None


class Roll(Page):
    form_model = "player"

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            original_dice = player.original_dice,
            reported_dice = player.reported_dice,
            treatment = player.treatment,
        )


class Dice(Page):
    form_model = "player"
    form_fields = ["reported_dice"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            original_dice = player.original_dice,
            reported_dice = player.reported_dice,
            treatment = player.treatment,
        )

    def before_next_page(player: Player, timeout_happened):
        if player.round_number == C.NUM_ROUNDS:
            calculate_k(player)
            random_payment(player),


class TrustGameBack(Page):
    form_model = "player"
    form_fields = ["send_back_1", "send_back_2", "send_back_3"]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS and player.participant.treatment == 'TG':
            return True
        return None

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            zero_points_tripled = C.zero_points*3,
            one_points_tripled = C.one_points*3,
            two_points_tripled = C.two_points*3,
            three_points_tripled = C.three_points*3,
            bounds={
                # 'send_back_1': {'min': 0, 'max': previous_pp.trust_points*3}, ## only live interaction
                'send_back_1': {'min': 0, 'max': C.one_points*3},
                'send_back_2': {'min': 0, 'max': C.two_points*3},
                'send_back_3': {'min': 0, 'max': C.three_points*3},
            }
        )


class FeedbackPart1(Page):
    form_model = "player"

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS and player.participant.treatment != 'TG':
            return True
        return None

    @staticmethod
    def vars_for_template(player: Player):
        return dict(

        )

page_sequence = [Consent,
                 Introduction,
                 InstruPart1,
                 Roll,
                 Dice,
                 TrustGameBack,
                 FeedbackPart1,
                 ]
