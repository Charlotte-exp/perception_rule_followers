from otree.api import Currency as c, currency_range, expect, Bot
from . import *

import random
import time


# class PlayerBot(Bot):
#     def play_round(self):
#         if self.round_number == 1:
#             yield Consent
#             yield Introduction
#             if self.participant.treatment == 'TG':
#                 yield InstruPart1, dict(q1=2, q_treatment=4)
#             elif self.participant.treatment == 'DG':
#                 yield InstruPart1, dict(q1=2, q_treatment=1)
#             elif self.participant.treatment == 'rating':
#                     yield InstruPart1, dict(q1=2, q_treatment=2)
#             elif self.participant.treatment == 'control':
#                     yield InstruPart1, dict(q1=2)
#         if self.round_number <= C.NUM_ROUNDS:
#             yield Roll, dict(random_roll='draw')
#             yield Dice, dict(reported_dice=random.choice([1, 6]))
#         if self.round_number == C.NUM_ROUNDS:
#             if self.participant.treatment == 'TG':
#                 yield TrustGameBack, dict(send_back_1=random.choice([1, 3]),
#                                           send_back_2=random.choice([1, 6]),
#                                           send_back_3=random.choice([1, 9]))
#             if self.participant.treatment == 'DG' or self.participant.treatment == 'rating':
#                 yield FeedbackPart1

## With wait times
class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield Consent
            time.sleep(random.uniform(1, 3))
            yield Introduction
            time.sleep(random.uniform(2, 4))
            if self.participant.treatment == 'TG':
                yield InstruPart1, dict(q1=2, q_treatment=4)
                time.sleep(random.uniform(10, 15))
            elif self.participant.treatment == 'DG':
                yield InstruPart1, dict(q1=2, q_treatment=1)
                time.sleep(random.uniform(10, 15))
            elif self.participant.treatment == 'rating':
                yield InstruPart1, dict(q1=2, q_treatment=2)
                time.sleep(random.uniform(10, 15))
            elif self.participant.treatment == 'control':
                yield InstruPart1, dict(q1=2)
                time.sleep(random.uniform(10, 15))
        if self.round_number <= C.NUM_ROUNDS:
            yield Roll, dict(random_roll='draw')
            time.sleep(random.uniform(1, 2))
            yield Dice, dict(reported_dice=random.choice([1, 6]))
            time.sleep(random.uniform(6, 8))
        if self.round_number == C.NUM_ROUNDS:
            if self.participant.treatment == 'TG':
                yield TrustGameBack, dict(send_back_1=random.choice([1, 3]),
                                          send_back_2=random.choice([1, 6]),
                                          send_back_3=random.choice([1, 9]))

                time.sleep(random.uniform(12, 16))
            if self.participant.treatment == 'DG' or self.participant.treatment == 'rating':
                yield FeedbackPart1
                time.sleep(random.uniform(2, 3))


