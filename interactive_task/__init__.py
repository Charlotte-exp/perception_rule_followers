from otree.api import *

import random
import itertools

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'interactive_task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 8

    num_dice_rounds = 12 # same as dice task!!

    percent_accurate = 10
    bonus = cu(2)
    conversion = '34p'

    TG_points = cu(3)
    zero_points = cu(0)
    one_points = cu(1)
    two_points = cu(2)
    three_points = cu(3)

    DG_points = cu(9)


class Subsession(BaseSubsession):
    pass

## to test without dice task and pairings when live interaction
# def creating_session(subsession):
#     """
#     create a fixed sequence of 10 elements for each player bu calling generate_k_sequence function.
#     Stored in a participant.vars since player field cannot be lists (and I don't need it in the database).
#     Because creating_session calls the function every round
#     we force it not to do that by setting a value based on round number instead.
#     """
#     subsession.session.num_dice_rounds = C.NUM_ROUNDS
#
#     treatments = itertools.cycle(['TG', 'DG', 'rating', 'control'])
#     for p in subsession.get_players():
#         p.treatment = next(treatments)
#         p.participant.treatment = p.treatment
#
#         p.participant.reported_dice = random.randint(1, 6)
#         p.participant.original_dice = random.randint(1, 6)
#
#         k_value = sum(generate_k_sequence(p))
#         p.participant.k_value = k_value
#
#         p.participant.randomly_selected_round = random.randint(1, 3)
#         p.participant.randomly_selected_reported_dice = random.randint(1, 6)


def creating_session(subsession):
    """
    create a fixed sequence of 10 elements for each player bu calling generate_k_sequence function.
    Stored in a participant.vars since player field cannot be lists (and I don't need it in the database).
    Because creating_session calls the function every round
    we force it not to do that by setting a value based on round number instead.
    """

    if subsession.round_number == 1:
        for p in subsession.get_players():
            sequence = generate_k_sequence(p)
            p.participant.vars['sequence'] = sequence
            # set first round value directly
            p.k_value = sequence[0]
    else:
        for p in subsession.get_players():
            # for rounds >1, just pick from participant.vars
            p.k_value = p.participant.vars['sequence'][p.round_number - 1]

    ## to test without dice task and pairings when live interaction
    # subsession.session.number_of_trials = 10
    # treatments = itertools.cycle(['TG', 'DG', 'rating', 'control'])
    # for p in subsession.get_players():
    #     p.treatment = next(treatments)
    #     p.participant.treatment = p.treatment
    #
    #     p.participant.reported_dice = random.randint(1, 6)
    #     p.participant.original_dice = random.randint(1, 6)
    #
    #     # k_value = sum(calculate_k(p))
    #     # p.participant.k_value = k_value
    #
    #     p.participant.randomly_selected_round = random.randint(1, 3)
    #     p.participant.randomly_selected_reported_dice = random.randint(1, 6)



class Group(BaseGroup):
    pass


class Player(BasePlayer):

    k_value = models.IntegerField(initial=99)

    TG_points_sent = models.IntegerField(
        verbose_name='',
        min=0, max=3)

    send_back_1 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=3)

    send_back_2 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=6)

    send_back_3 = models.FloatField(
        verbose_name='You received X points from the other participant: <br>'
                     'How many points to do you send back?',
        min=0, max=9)

    DG_points_kept = models.FloatField(initial=0)

    trustworthiness = models.IntegerField(initial=0)
    likeable = models.IntegerField(initial=0)

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

    q2_TG_failed_attempts = models.IntegerField(initial=0)
    q2_DG_failed_attempts = models.IntegerField(initial=0)
    q2_rating_failed_attempts = models.IntegerField(initial=0)
    q3_failed_attempts = models.IntegerField(initial=0)

    q2_TG = models.IntegerField(
        initial=0,
        choices=[
            [1, f'Only the points I kept, the points I sent cannot be returned to me.'],
            [4, f'Only the points returned to me, the points I kept do not count.'],
            [3, f'The points returned to me by another participant, depending on how much I sent, '
                f'and/or any points I kept.'],
            [2, f'The points returned to me by {C.NUM_ROUNDS} participants, depending on how much I sent to each, '
                f'and/or any points I kept.'],
        ],
        verbose_name='What determines the number of bonus points you will be paid from Part 2?',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    q2_DG = models.IntegerField(
        initial=0,
        choices=[
            [1, f'The sum of the points I choose to keep and not share with all {C.NUM_ROUNDS} participants.'],
            [2, f'Only the points I choose to keep and not share with one other participant, '
                f'the most correct one from {C.NUM_ROUNDS} participants.'],
            [3, f'Only the points I choose to keep and not share with one other participant, '
                f'selected at random from {C.NUM_ROUNDS} participants.'],
        ],
        verbose_name='What determines the number of bonus points you will be paid from Part 2?',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    q2_rating = models.IntegerField(
        initial=0,
        choices=[
            [1, f'Another participant will observe how many times I report the die correctly.'],
            [2, f'I will observe how many times 1 participant reported the die correctly.'],
            [3, f'I will observe how many times {C.NUM_ROUNDS} participants reported the die correctly.'],
        ],
        verbose_name='What will you observe in Part 2?',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    q3 = models.IntegerField(
        initial=0,
        choices=[
            [1, f'All the points sent by a participant from another study, without any action from me.'],
            [2, f'The points I decide to keep from those sent by a participant from another study.'],
            [3, f'The points a participant from another study returns to me if I send them some of my points.'],
        ],
        verbose_name='What determines the number of bonus points you will be paid from Part 3?',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    age = models.IntegerField(
        min=10, max=100,
        verbose_name = 'What is your age?',
    )

    gender = models.StringField(
        choices=[
            [1, f'Female'],
            [2, f'Male'],
            [3, f'Non-binary'],
            [4, f'Prefer not to say'],
        ],
        verbose_name='What is your gender?',
    )

    education = models.StringField(
        choices=[
            [1, f'No formal education/Early childhood education'],
            [2, f'Primary education (ages 5–12)'],
            [3, f'Lower secondary education (ages ~12–15)'],
            [4, f'Upper secondary education (ages ~15–18)'],
            [5, f'Post-secondary non-tertiary education (e.g., vocational training, certificates)'],
            [6, f'Short-cycle tertiary education (e.g., associate degree, advanced diploma)'],
            [7, f'Bachelor’s degree or equivalent'],
            [8, f'Master’s degree or equivalent'],
            [9, f'Doctoral degree (PhD) or equivalent'],
        ]
    )


######## FUNCTIONS #########

def group_by_arrival_time_method(subsession, waiting_players):
    players_TG = [p for p in waiting_players if p.participant.treatment == 'TG']
    players_DG = [p for p in waiting_players if p.participant.treatment == 'DG']
    players_rating = [p for p in waiting_players if p.participant.treatment == 'rating']
    for player_list in [players_TG, players_DG, players_rating]:
        if len(player_list) >= 3:
            players = [player_list[0], player_list[1], player_list[2]]
            return players
    return None

## if live interaction
# def other_players(player: Player):
#     """
#     Get_others_in_group returns a list in ascending order so need to use player ID in group.
#     """
#     number_of_players = C.PLAYERS_PER_GROUP
#     id_in_group = player.id_in_group  # 1, 2, or 3
#
#     # modulo to avoid negative values
#     prev_id = (id_in_group - 2) % number_of_players + 1   # previous player
#     next_id = id_in_group % number_of_players + 1    # next player
#
#     previous_pp = player.group.get_player_by_id(prev_id)
#     next_pp = player.group.get_player_by_id(next_id)
#
#     print(f"Player {id_in_group}: prev={previous_pp.id_in_group}, next={next_pp.id_in_group}")
#     return {
#         "previous": player.group.get_player_by_id(prev_id),
#         "next": player.group.get_player_by_id(next_id),
#     }

## if live interaction
# def calculate_k(player: Player):
#     list_of_correct = []
#     for p in player.in_all_rounds():
#         if p.participant.reported_dice - p.participant.original_dice <= 0:
#             value = 1
#         else:
#             value = 0
#         list_of_correct.append(value)
#         p.participant.k_list = list_of_correct
#         ## if testing only stage 2
#         k_value = sum(list_of_correct)
#         p.participant.k_value = k_value
#     return list_of_correct


def generate_k_sequence(player: Player):
    """
    Generate a random sequence of 10 numbers.
    One different sequence is assigned to a player at creating_session
    4 values are always included, 6 are random.
    each sequence is shuffled before being returned as the values are assigned to each round in order.
    """
    # player.session.num_dice_rounds -> when finish testing
    optional_values = list(range(2, (C.num_dice_rounds-1)))  # 2 to 10
    necessary_values = [0, 1, (C.num_dice_rounds-1), C.num_dice_rounds]
    sequence = necessary_values + random.sample(optional_values, 4)   # adjust number if change NUM_ROUNDS
    random.shuffle(sequence)
    return sequence


######### PAGES #########

# class PairingWaitPage(WaitPage):
#     """
#     The Waitroom. This wait page has two purposes: making sure pps don't wait too long for other players in case there
#     is little traffic, and allows one pp to leave before being grouped with others so that a dropout at the instruction
#     level does not mean all pp in the group are out.
#     The code below keeps the groups the same across all rounds automatically.
#     We added a special pairing method in models.py.
#     The waitroom has a 5min timer after which the pp is given a code to head back to prolific.
#     This is coded on the template below and uses a javascript. (don't forget to paste the correct link!)
#     """
#     group_by_arrival_time = True
#
#     def is_displayed(player: Player):
#         return player.round_number == 1
#
#
#     # def vars_for_template(player: Player):
#     #     player.participant.k_list = calculate_k(player)
#     #     return dict(k_list=player.participant.k_list)
#
#     template_name = 'interactive_task/Waitroom.html'


class InstruStage2(Page):
    form_model = "player"
    # form_fields = ["q2"]

    def get_form_fields(player:Player):
        if player.participant.treatment == 'TG':
            return ['q2_TG']
        elif player.participant.treatment == 'DG':
            return ['q2_DG']
        elif player.participant.treatment == 'rating':
            return ['q2_rating']
        return None

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.participant.treatment != 'control'

    @staticmethod
    def error_message(player: Player, values):
        """
        records the number of time the page was submitted with an error. which specific error is not recorded.
        """
        # solutions = dict(q2=3)
        if player.participant.treatment == 'TG':
            solutions = dict(q2_TG=3)
        elif player.participant.treatment == 'DG':
            solutions = dict(q2_DG=3)
        else:
            solutions = dict(q2_rating=3)

        # error_message can return a dict whose keys are field names and whose values are error messages
        errors = {}
        for question, correct_answer in solutions.items():
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

    def vars_for_template(player: Player):
        # others = other_players(player)
        # next_pp = others["next"]
        return dict(
            treatment=player.participant.treatment,
            num_dice_rounds = player.session.num_dice_rounds,
            half_k = int(player.session.num_dice_rounds/2),
            DG_points = C.DG_points,
            half_points = float(C.DG_points)/2,
        )


class TrustGameSender(Page):
    form_model = "player"
    form_fields = ["TG_points_sent"]

    def is_displayed(player: Player):
        if player.round_number <= C.NUM_ROUNDS and player.participant.treatment == 'TG':
            return True
        return None

    def vars_for_template(player: Player):
        # others = other_players(player)
        # next_pp = others["next"]
        return dict(
            # k_value = sum(next_pp.participant.k_list), ## for live interaction
            k_value=player.k_value,
            num_dice_rounds = player.session.num_dice_rounds,
            TG_points = float(C.TG_points),
            int_TG_points = int(C.TG_points),
        )


class DictGame(Page):
    form_model = "player"
    form_fields = ["DG_points_kept"]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number <= C.NUM_ROUNDS and player.participant.treatment == 'DG':
            return True
        return None

    @staticmethod
    def vars_for_template(player: Player):
        # others = other_players(player)
        # next_pp = others["next"]
        return dict(
            DG_points = float(C.DG_points),
            int_DG_points=int(C.DG_points),
            # k_value = sum(next_pp.participant.k_list), ## for live interaction
            k_value=player.k_value,
            num_dice_rounds = player.session.num_dice_rounds,
            DG_points_kept = player.DG_points_kept,
        )


class Rating(Page):
    form_model = "player"
    form_fields = ["trustworthiness"]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number <= C.NUM_ROUNDS and player.participant.treatment == 'rating':
            return True
        return None

    @staticmethod
    def vars_for_template(player: Player):
        # others = other_players(player)
        # next_pp = others["next"]
        return dict(
            # k_value = sum(next_pp.participant.k_list), ## for live interaction
            k_value=player.k_value,
            num_dice_rounds = player.session.num_dice_rounds,
        )

## only if live interaction
# class ResultsWaitPage(WaitPage):
#     """
#     This wait page is necessary to compile the payoffs as the results can only be displayed on the results page if all
#     the players have made a decision. Thus players have to wait for the decision of the others before moving on to the
#     results page.
#     I use a template for some special text rather than just the body_text variable.
#     """
#     template_name = 'interactive_task/ResultsWaitPage.html'
#     # after_all_players_arrive = set_payoffs
#
#     @staticmethod
#     def is_displayed(player: Player):
#         if player.round_number == C.NUM_ROUNDS and player.participant.treatment != 'rating':
#             return True
#         return None


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
        # others = other_players(player)
        # previous_pp = others["previous"]
        return dict(
            # sent_points = previous_pp.TG_points_sent*3, # multiplied!!!  ## only live interaction
            zero_points_tripled = int(C.zero_points*3),
            one_points_tripled = int(C.one_points*3),
            two_points_tripled = int(C.two_points*3),
            three_points_tripled = int(C.three_points*3),
        )

## only if live interaction
# class EndWaitPage(WaitPage):
#     """
#     In case some people go to payment before their received decided what points to return
#     """
#     template_name = 'interactive_task/EndWaitPage.html'
#     # after_all_players_arrive = set_payoffs
#
#     @staticmethod
#     def is_displayed(player: Player):
#         if player.round_number == C.NUM_ROUNDS and player.participant.treatment == 'TG':
#             return True
#         return None


class InstruStage3(Page):
    form_model = "player"
    form_fields = ["q3"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS and player.participant.treatment != 'control'

    @staticmethod
    def error_message(player: Player, values):
        """
        records the number of time the page was submitted with an error. which specific error is not recorded.
        """
        solutions = dict(q3=2)

        # error_message can return a dict whose keys are field names and whose values are error messages
        errors = {}
        for question, correct_answer in solutions.items():
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

    def vars_for_template(player: Player):
        return dict(
            treatment=player.participant.treatment,
            num_dice_rounds = player.session.num_dice_rounds,
            DG_points = int(C.DG_points),
            half_points = int(C.DG_points/2),
        )


class TrustGameForCCP(Page):
    form_model = "player"
    form_fields = ["send_back_CCP_1", "send_back_CCP_2", "send_back_CCP_3"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS and player.participant.treatment != 'control'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            num_dice_rounds = player.session.num_dice_rounds,
            zero_points_tripled = int(C.zero_points*3),
            one_points_tripled = int(C.one_points*3),
            two_points_tripled = int(C.two_points*3),
            three_points_tripled = int(C.three_points*3),
        )


class Demographics(Page):
    form_model = "player"
    form_fields = ["age", "gender", "education"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    # def vars_for_template(player: Player):
    #     others = other_players(player)
    #     previous_pp = others["previous"]
    #     next_pp = others["next"]
    #     base_data = dict(
    #         player_in_all_rounds=player.in_all_rounds(),
    #         treatment=player.participant.treatment,
    #         random_round=player.participant.randomly_selected_round,
    #         random_reported_dice=player.participant.randomly_selected_reported_dice,
    #     )
    #     if player.participant.treatment == 'TG':
    #         base_data.update(
    #             points_i_sent=player.TG_points_sent,
    #             points_returned_to_me=next_pp.send_back_1,
    #             points_sent_to_me=previous_pp.TG_points_sent*3, #  multiplied !!!
    #             points_i_kept=round(previous_pp.TG_points_sent*3 - player.send_back_1, 1),
    #         )
    #     elif player.participant.treatment == 'DG':
    #         base_data.update(
    #             previous_pp_points_sent=10 - previous_pp.DG_points_kept,
    #             points_sent=10 - player.DG_points_kept,
    #         )
    #     return base_data

    def vars_for_template(player: Player):
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            treatment=player.participant.treatment,
            random_round=player.participant.randomly_selected_round,
            random_reported_dice=player.participant.randomly_selected_reported_dice,
        )


class ProlificLink(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [
    # PairingWaitPage,
                 InstruStage2,
                 TrustGameSender,
                 DictGame,
                 Rating,
                 # ResultsWaitPage,
                 # TrustGameBack,
                 # EndWaitPage,
                 InstruStage3,
                 TrustGameForCCP,
                 Demographics,
                 Payment,
                 ProlificLink]


