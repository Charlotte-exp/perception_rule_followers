from otree.api import *

import random
import itertools

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'interactive_task'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1

    # number_of_trials = NUM_ROUNDS # from the actor task
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

## to test without dice task and pairings
def creating_session(subsession):
    """
    create a fixed sequence of 10 elements for each player bu calling generate_k_sequence function.
    Stored in a participant.vars since player field cannot be lists (and I don't need it in the database).
    Because creating_session calls the function every round
    we force it not to do that by setting a value based on round number instead.
    """
    subsession.session.number_of_trials = C.NUM_ROUNDS

    treatments = itertools.cycle(['TG', 'TG'])
    for p in subsession.get_players():
        p.treatment = next(treatments)
        p.participant.treatment = p.treatment

        p.participant.reported_dice = random.randint(1, 6)
        p.participant.original_dice = random.randint(1, 6)

        k_value = sum(calculate_k(p))
        p.participant.k_value = k_value

        p.participant.randomly_selected_round = random.randint(1, 3)
        p.participant.randomly_selected_reported_dice = random.randint(1, 6)



class Group(BaseGroup):
    pass


class Player(BasePlayer):

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
        min=0, max=9)

    points_kept = models.IntegerField(initial=0)

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

    q2 = models.IntegerField(
        initial=9,
        choices=[
            [0, f'The points returned to me by the next participant, independent of how much I send in the first place'],
            [1, f'The points returned to me by the next participant, depending on how much I send in the first place'],
            [2, f'The points returned to me by the next participant, depending on how much I send in the first place, '
                f'as well as how much I keep from what the previous participant sent to me'],
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


def other_players(player: Player):
    """
    Get_others_in_group returns a list in ascending order so need to use player ID in group.
    """
    number_of_players = C.PLAYERS_PER_GROUP
    id_in_group = player.id_in_group  # 1, 2, or 3

    # modulo to avoid negative values
    prev_id = (id_in_group - 2) % number_of_players + 1   # previous player
    next_id = id_in_group % number_of_players + 1    # next player

    previous_pp = player.group.get_player_by_id(prev_id)
    next_pp = player.group.get_player_by_id(next_id)

    print(f"Player {id_in_group}: prev={previous_pp.id_in_group}, next={next_pp.id_in_group}")
    return {
        "previous": player.group.get_player_by_id(prev_id),
        "next": player.group.get_player_by_id(next_id),
    }


def calculate_k(player: Player):
    list_of_correct = []
    for p in player.in_all_rounds():
        if p.participant.reported_dice - p.participant.original_dice <= 0:
            value = 1
        else:
            value = 0
        list_of_correct.append(value)
        p.participant.k_list = list_of_correct
        ## if testing only stage 2
        k_value = sum(list_of_correct)
        p.participant.k_value = k_value
    return list_of_correct


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
    form_fields = ["q2"]

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
        solutions = dict(q2=2)
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

    def vars_for_template(player: Player):
        others = other_players(player)
        next_pp = others["next"]
        return dict(
            treatment=player.participant.treatment,
        )


class TrustGameSender(Page):
    form_model = "player"
    form_fields = ["trust_points"]

    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS and player.participant.treatment == 'TG':
            return True
        return None

    def vars_for_template(player: Player):
        others = other_players(player)
        next_pp = others["next"]
        return dict(
            k_value=sum(next_pp.participant.k_list),
            number_of_trials = player.session.number_of_trials,
        )


class DictGame(Page):
    form_model = "player"
    form_fields = ["points_kept"]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS and player.participant.treatment == 'DG':
            return True
        return None

    @staticmethod
    def vars_for_template(player: Player):
        others = other_players(player)
        next_pp = others["next"]
        return dict(
            DG_points = int(C.DG_points),
            k_value = sum(next_pp.participant.k_list),
            number_of_trials = player.session.number_of_trials,
            points_kept = player.points_kept,
        )


class Rating(Page):
    form_model = "player"
    form_fields = ["trustworthiness"]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS and player.participant.treatment == 'rating':
            return True
        return None

    @staticmethod
    def vars_for_template(player: Player):
        others = other_players(player)
        next_pp = others["next"]
        return dict(
            k_value = sum(next_pp.participant.k_list),
            number_of_trials = player.session.number_of_trials,
        )


class ResultsWaitPage(WaitPage):
    """
    This wait page is necessary to compile the payoffs as the results can only be displayed on the results page if all
    the players have made a decision. Thus players have to wait for the decision of the others before moving on to the
    results page.
    I use a template for some special text rather than just the body_text variable.
    """
    template_name = 'interactive_task/ResultsWaitPage.html'
    # after_all_players_arrive = set_payoffs

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS and player.participant.treatment != 'rating':
            return True
        return None


class TrustGameBack(Page):
    form_model = "player"
    form_fields = ["send_back_1"]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS and player.participant.treatment == 'TG':
            return True
        return None

    @staticmethod
    def vars_for_template(player: Player):
        others = other_players(player)
        previous_pp = others["previous"]
        return dict(
            sent_points = previous_pp.trust_points*3, # multiplied!!!
            bounds={
                'send_back_1': {'min': 0, 'max': previous_pp.trust_points*3},
            }
        )


class EndWaitPage(WaitPage):
    """
    In case some people go to payment before their received decided what points to return
    """
    template_name = 'interactive_task/EndWaitPage.html'
    # after_all_players_arrive = set_payoffs

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS and player.participant.treatment == 'TG':
            return True
        return None


class InstruStage3(Page):
    form_model = "player"
    form_fields = ["q3"]

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
        solutions = dict(q3=3)
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
            },
        )


class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    def vars_for_template(player: Player):
        others = other_players(player)
        previous_pp = others["previous"]
        next_pp = others["next"]
        base_data = dict(
            player_in_all_rounds=player.in_all_rounds(),
            treatment=player.participant.treatment,
            random_round=player.participant.randomly_selected_round,
            random_reported_dice=player.participant.randomly_selected_reported_dice,
        )
        if player.participant.treatment == 'TG':
            base_data.update(
                points_i_sent=player.trust_points,
                points_returned_to_me=next_pp.send_back_1,
                points_sent_to_me=previous_pp.trust_points*3, #  multiplied !!!
                points_i_kept=round(previous_pp.trust_points*3 - player.send_back_1, 1),
            )
        elif player.participant.treatment == 'DG':
            base_data.update(
                previous_pp_points_sent=10 - previous_pp.points_kept,
                points_sent=10 - player.points_kept,
            )
        return base_data


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
                 ResultsWaitPage,
                 TrustGameBack,
                 EndWaitPage,
                 InstruStage3,
                 TrustGameForCCP,
                 Payment,
                 ProlificLink]


