from otree.api import Currency as c, currency_range, expect, Bot
from . import *

import random


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            if self.participant.treatment == 'TG':
                yield InstruStage2, dict(q2_TG=3)
            elif self.participant.treatment == 'DG':
                yield InstruStage2, dict(q2_DG=3)
            elif self.participant.treatment == 'rating':
                yield InstruStage2, dict(q2_rating=3)
        if self.round_number <= C.NUM_ROUNDS:
            if self.participant.treatment == 'TG':
                yield TrustGameSender, dict(trust_points=random.choice([0, 3]))
            elif self.participant.treatment == 'DG':
                yield DictGame, dict(points_kept=random.choice([0, 9]))
            elif self.participant.treatment == 'rating':
                yield Rating, dict(trustworthiness=random.choice([0, 100]))
        if self.round_number == C.NUM_ROUNDS and self.participant.treatment != 'control':
            yield InstruStage3, dict(q3=4)
            yield TrustGameForCCP, dict(send_back_CCP_1=random.choice([1, 3]),
                                        send_back_CCP_2=random.choice([1, 6]),
                                        send_back_CCP_3=random.choice([1, 9]))
        if self.round_number == C.NUM_ROUNDS:
            yield Demographics, dict(age='12', gender='1', education='1')
            yield Payment
            yield ProlificLink


## With wait times
# class PlayerBot(Bot):
#     def play_round(self):
#         if self.round_number == 1:
#             if self.participant.treatment == 'TG':
#                 yield InstruStage2, dict(q2_TG=3)
#             elif self.participant.treatment == 'DG':
#                 yield InstruStage2, dict(q2_DG=3)
#             elif self.participant.treatment == 'rating':
#                 yield InstruStage2, dict(q2_rating=3)
#         if self.round_number <= C.NUM_ROUNDS:
#             if self.participant.treatment == 'TG':
#                 yield TrustGameSender, dict(trust_points=random.choice([0, 3]))
#             elif self.participant.treatment == 'DG':
#                 yield DictGame, dict(points_kept=random.choice([0, 9]))
#             elif self.participant.treatment == 'rating':
#                 yield Rating, dict(trustworthiness=random.choice([0, 100]))
#         if self.round_number == C.NUM_ROUNDS and self.participant.treatment != 'control':
#             yield InstruStage3, dict(q3=4)
#             yield TrustGameForCCP, dict(send_back_CCP_1=random.choice([1, 3]),
#                                         send_back_CCP_2=random.choice([1, 6]),
#                                         send_back_CCP_3=random.choice([1, 9]))
#         if self.round_number == C.NUM_ROUNDS:
#             yield Demographics, dict(age='12', gender='1', education='1')
#             yield Payment
#             yield ProlificLink


