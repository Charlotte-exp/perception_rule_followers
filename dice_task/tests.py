from otree.api import Currency as c, currency_range, expect, Bot
from . import *

import random


class PlayerBot(Bot):
    def play_round(self):
        if self.participant.treatment == 'TG':
            if self.round_number == 1:
                yield Consent
                yield Introduction
                yield InstruPart1, dict(q1=2, q_treatment=4)
            if self.round_number <= C.NUM_ROUNDS:
                yield Roll, dict(random_roll='draw')
                yield Dice, dict(reported_dice=random.choice([1, 6]))
            if self.round_number == C.NUM_ROUNDS:
                yield TrustGameBack, dict(send_back_1=random.choice([1, 3]),
                                          send_back_2=random.choice([1, 6]),
                                          send_back_3=random.choice([1, 9]))
        elif self.participant.treatment == 'DG':
            if self.round_number == 1:
                yield Consent
                yield Introduction
                yield InstruPart1, dict(q1=2, q_treatment=1)
            if self.round_number <= C.NUM_ROUNDS:
                yield Roll, dict(random_roll='draw')
                yield Dice, dict(reported_dice=random.choice([1, 6]))
            if self.round_number == C.NUM_ROUNDS:
                yield FeedbackPart1
        elif self.participant.treatment == 'rating':
            if self.round_number == 1:
                yield Consent
                yield Introduction
                yield InstruPart1, dict(q1=2, q_treatment=2)
            if self.round_number <= C.NUM_ROUNDS:
                yield Roll, dict(random_roll='draw')
                yield Dice, dict(reported_dice=random.choice([1, 6]))
            if self.round_number == C.NUM_ROUNDS:
                yield FeedbackPart1
        elif self.participant.treatment == 'control':
            if self.round_number == 1:
                yield Consent
                yield Introduction
                yield InstruPart1, dict(q1=2)
            if self.round_number <= C.NUM_ROUNDS:
                yield Roll, dict(random_roll='draw')
                yield Dice, dict(reported_dice=random.choice([1, 6]))
