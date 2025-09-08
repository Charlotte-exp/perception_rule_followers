from otree.api import *


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

    conversion = '43p'
    zero_points = cu(0)
    one_points = cu(1)
    two_points = cu(2)
    three_points = cu(3)


class Subsession(BaseSubsession):
    pass


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
        min=0, max=C.one_points*3)

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
    previous_pp = player.get_others_in_group()[0]
    next_pp = player.get_others_in_group()[1]
    print(next_pp, previous_pp)
    return previous_pp, next_pp


def calculate_k(player: Player):
    list_of_correct = []
    for p in player.in_all_rounds():
        if p.participant.reported_dice - p.participant.original_dice <= 0:
            value = 1
        else:
            value = 0
        list_of_correct.append(value)
        p.participant.k_list = list_of_correct
        # k_value = sum(list_of_correct)
        # p.participant.k_value = k_value


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

class PairingWaitPage(WaitPage):
    """
    The Waitroom. This wait page has two purposes: making sure pps don't wait too long for other players in case there
    is little traffic, and allows one pp to leave before being grouped with others so that a dropout at the instruction
    level does not mean all pp in the group are out.
    The code below keeps the groups the same across all rounds automatically.
    We added a special pairing method in models.py.
    The waitroom has a 5min timer after which the pp is given a code to head back to prolific.
    This is coded on the template below and uses a javascript. (don't forget to paste the correct link!)
    """
    group_by_arrival_time = True

    def is_displayed(player: Player):
        return player.round_number == 1


    # def vars_for_template(player: Player):
    #     player.participant.k_list = calculate_k(player)
    #     return dict(k_list=player.participant.k_list)

    template_name = 'interactive_task/Waitroom.html'


class TrustGameSender(Page):
    form_model = "player"
    form_fields = ["trust_points"]

    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS and player.participant.treatment == 'TG':
            return True
        return None

    def vars_for_template(player: Player):
        next_pp = other_players(player)[0]
        return dict(
            k_value=sum(player.participant.k_list),
            k_value_next = sum(next_pp.participant.k_list),
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
        if player.round_number == C.NUM_ROUNDS and player.participant.treatment == 'TG':
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
        previous_pp = other_players(player)[1]
        return dict(
            zero_points_tripled = C.zero_points*3,
            one_points_tripled = C.one_points*3,
            two_points_tripled = C.two_points*3,
            three_points_tripled = C.three_points*3,
            sent_points = previous_pp.trust_points,
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
        if player.participant.round_number == C.NUM_ROUNDS and player.participant.treatment == 'rating':
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
        if player.round_number == C.NUM_ROUNDS and player.participant.treatment == 'DG':
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


page_sequence = [PairingWaitPage,
                 TrustGameSender,
                 ResultsWaitPage,
                 TrustGameBack,
                 Rating,
                 NonTrustBasedTask,
                 TrustGameForCCP,
                 RandomSelection,
                 End,
                 Payment,
                 ProlificLink]


