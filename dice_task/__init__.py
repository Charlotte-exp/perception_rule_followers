from otree.api import *

import random
import itertools

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'dice_task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5

    number_of_trials = NUM_ROUNDS # from the actor task
    percent_accurate = 10
    bonus = cu(2)

    conversion = '43p'
    zero_points = cu(0)
    one_points = cu(1)
    two_points = cu(2)
    three_points = cu(3)


class Subsession(BaseSubsession):
    pass

def creating_session(subsession):
    """
    create a fixed sequence of 10 elements for each player bu calling generate_k_sequence function.
    Stored in a participant.vars since player field cannot be lists (and I don't need it in the database).
    Because creating_session calls the function every round
    we force it not to do that by setting a value based on round number instead.
    """
    treatments = itertools.cycle(['TG', 'DG', 'rating', 'dont_know'])
    for p in subsession.get_players():
        p.treatment = next(treatments)
        # p.participant.treatment = p.treatment

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

    k_value = models.IntegerField(initial=99)

    trust_points = models.IntegerField(
        choices=[
            [0, '0 point'], [1, '1 point'], [2, '2 points'], [3, '3 points'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )

    send_back_1 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=C.one_points*3)

    # send_back_2 = models.FloatField(
    #     verbose_name='You received X points from the other participant: <br>'
    #                  'How many points to do you send back?',
    #     min=0, max=C.two_points*3)
    #
    # send_back_3 = models.FloatField(
    #     verbose_name='You received X points from the other participant: <br>'
    #                  'How many points to do you send back?',
    #     min=0, max=C.three_points*3)

    trustworthiness = models.IntegerField(initial=0)

    send_back_CCP_1 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=C.one_points*3)

    send_back_CCP_2 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=C.two_points*3)

    send_back_CCP_3 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=C.three_points*3)

    random_selection = models.StringField(
        initial='',
        choices=['randomise', 'whatever'],
    )

    randomly_selected_round = models.IntegerField(initial=0)
    randomly_selected_reported_dice = models.IntegerField(initial=0)

    q1_failed_attempts = models.IntegerField(initial=0)
    q2_failed_attempts = models.IntegerField(initial=0)

    q1 = models.IntegerField(
        initial=9,
        choices=[
            [0, f'I will be paid the number I roll from one randomly selected die roll'],
            [1, f'I will be paid the number I report from one randomly selected die roll'],
            [2, f'I will be paid the number I roll from all five die rolls summed up'],
            [3, f'I will be paid the number I report from all five die rolls summed up'],
        ],
        verbose_name='What determines the number of bonus points you will be paid from stage 1?',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    q2 = models.IntegerField(
        initial=9,
        choices=[
            [0, f'The points returned to me by another participants, independent of how much I send in the first place'],
            [1, f'The points returned to me by another participants, depending on how much I send in the first place'],
        ],
        verbose_name='What determines the number of bonus points you will be paid from stage 2?',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    q3 = models.IntegerField(
        initial=9,
        choices=[
            [0, f'The points sent the participant in another study'],
            [1, f'The points sent the participant in another study, doubled'],
            [2, f'The points sent the participant in another study, tripled'],
            [3, f'The points I decide to keep from those sent by another participant and tripled by us'],
        ],
        verbose_name='What determines the number of bonus points you will be paid from stage 3?',
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


######## FUNCTIONS #########

def generate_dice_sequence():
    """
    Generate a random sequence of C.NUM_ROUNDS numbers.
    One different sequence is assigned to a player at creating_session
    """
    # dice_values = [random.randint(1, 6) for _ in range(C.NUM_ROUNDS)]
    sequence = [random.randint(1, 6) for _ in range(C.NUM_ROUNDS)]
    return sequence

def other_player(player: Player):
    return player.get_others_in_group()[0]

def random_payment(player: Player):
    """
    This function selects one round among all with equal probability.
    It records the value of each variable on this round as new random_variable fields
    """
    randomly_selected_round = random.randint(1, C.NUM_ROUNDS)
    me = player.in_round(randomly_selected_round)
    player.randomly_selected_round = randomly_selected_round
    #player.participant.randomly_selected_round = randomly_selected_round

    attributes = ['reported_dice']
    for attr in attributes:
        value = getattr(me, attr)
        setattr(player, f'randomly_selected_{attr}', value)
        #setattr(player.participant, f'randomly_selected_{attr}', value)



######### PAGES #########

class Consent(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Introduction(Page):
    form_model = "player"
    form_fields = ["q1"]

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
        solutions = dict(q1=1)
        # if player.treatment == 'treatment':
        #     solutions = dict(q1=1, q2=2)
        # else:
        #     solutions = dict(q5=1, q6=2)

        # error_message can return a dict whose keys are field names and whose values are error messages
        errors = {}
        for question, correct_answer in solutions.items():
            if values[question] != correct_answer:
                errors[question] = 'This answer is wrong'
                # Increment the specific failed attempt counter for the incorrect question
                failed_attempt_field = f"{question}_failed_attempts"
                if hasattr(player, failed_attempt_field):  # Ensure the field exists
                    setattr(player, failed_attempt_field, getattr(player, failed_attempt_field) + 1)

        if errors:
            return errors
        return None


class InstruStage2(Page):
    form_model = "player"
    form_fields = ["q2"]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1 and player.treatment != 'dont_know':
            return True
        return None

    @staticmethod
    def error_message(player: Player, values):
        """
        records the number of time the page was submitted with an error. which specific error is not recorded.
        """
        solutions = dict(q2=1)
        # if player.treatment == 'treatment':
        #     solutions = dict(q1=1, q2=2)
        # else:
        #     solutions = dict(q5=1, q6=2)

        # error_message can return a dict whose keys are field names and whose values are error messages
        errors = {}
        for question, correct_answer in solutions.items():
            if values[question] != correct_answer:
                errors[question] = 'This answer is wrong'
                # Increment the specific failed attempt counter for the incorrect question
                failed_attempt_field = f"{question}_failed_attempts"
                if hasattr(player, failed_attempt_field):  # Ensure the field exists
                    setattr(player, failed_attempt_field, getattr(player, failed_attempt_field) + 1)

        if errors:
            return errors
        return None

class InstruStage3(Page):
    form_model = "player"
    form_fields = ["q3"]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1 and player.treatment != 'dont_know':
            return True
        return None

    @staticmethod
    def error_message(player: Player, values):
        """
        records the number of time the page was submitted with an error. which specific error is not recorded.
        """
        solutions = dict(q3=2)
        # if player.treatment == 'treatment':
        #     solutions = dict(q1=1, q2=2)
        # else:
        #     solutions = dict(q5=1, q6=2)

        # error_message can return a dict whose keys are field names and whose values are error messages
        errors = {}
        for question, correct_answer in solutions.items():
            if values[question] != correct_answer:
                errors[question] = 'This answer is wrong'
                # Increment the specific failed attempt counter for the incorrect question
                failed_attempt_field = f"{question}_failed_attempts"
                if hasattr(player, failed_attempt_field):  # Ensure the field exists
                    setattr(player, failed_attempt_field, getattr(player, failed_attempt_field) + 1)

        if errors:
            return errors
        return None

class Dice(Page):
    form_model = "player"
    form_fields = ["reported_dice"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            original_dice = player.original_dice,
            reported_dice = player.reported_dice,
        )


class TrustGameSender(Page):
    form_model = "player"
    form_fields = ["trust_points"]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS and player.treatment == 'TG':
            return True
        return None

    def vars_for_template(player: Player):
        return dict(
            k_value=player.k_value,
        )


class TrustGameBack(Page):
    form_model = "player"
    form_fields = ["send_back_1"]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS and player.treatment == 'TG':
            return True
        return None

    @staticmethod
    def vars_for_template(player: Player):
        other_pp = other_player(player)
        return dict(
            zero_points_tripled = C.zero_points*3,
            one_points_tripled = C.one_points*3,
            two_points_tripled = C.two_points*3,
            three_points_tripled = C.three_points*3,
            sent_points = player.trust_points,
            bounds={
                'send_back_1': {'min': 0, 'max': C.one_points*3},
                # 'send_back_2': {'min': 0, 'max': C.two_points*3},
                # 'send_back_3': {'min': 0, 'max': C.three_points*3},
            }
        )


class Rating(Page):
    form_model = "player"
    form_fields = ["trustworthiness"]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS and player.treatment == 'rating':
            return True
        return None

    @staticmethod
    def vars_for_template(player: Player):
        return dict(

        )


class NonTrustBasedTask(Page):
    form_model = "player"
    form_fields = ["dictator"]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS and player.treatment == 'DG':
            return True
        return None

    @staticmethod
    def vars_for_template(player: Player):
        return dict(

        )


class TrustGameForCCP(Page):
    form_model = "player"
    form_fields = ["send_back_CCP_1", "send_back_CCP_2", "send_back_CCP_3"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            zero_points_tripled = C.zero_points*3,
            one_points_tripled = C.one_points*3,
            two_points_tripled = C.two_points*3,
            three_points_tripled = C.three_points*3,
            bounds={
                'send_back_CCP_1': {'min': 0, 'max': C.one_points*3},
                'send_back_CCP_2': {'min': 0, 'max': C.two_points*3},
                'send_back_CCP_3': {'min': 0, 'max': C.three_points*3},
            }
        )

class RandomSelection(Page):
    form_model = 'player'
    form_fields = ['random_selection']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    def vars_for_template(player: Player):
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            round_number=player.round_number,

            call_payment=random_payment(player),
        )


class End(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    def vars_for_template(player: Player):
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            round_number=player.round_number,

            random_round=player.randomly_selected_round,
            random_reported_dice=player.randomly_selected_reported_dice,
        )


class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

class ProlificLink(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Consent,
                 Introduction,
                 InstruStage2,
                 InstruStage3,
                 Dice,
                 TrustGameSender,
                 TrustGameBack,
                 Rating,
                 # NonTrustBasedTask,
                 TrustGameForCCP,
                 RandomSelection,
                 End,
                 Payment,
                 ProlificLink]
