from os import environ
from os import popen

SESSION_CONFIGS = [
    dict(
        name='perception',
        display_name="Dice and trust game",
        app_sequence=['dice_task', 'interactive_task'],
        num_demo_participants=9,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip()
    ),
    dict(
        name='stage2',
        display_name="stage 2 games only",
        app_sequence=['interactive_task'],
        num_demo_participants=9,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip()
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc=""
)

PARTICIPANT_FIELDS = ['original_dice', 'reported_dice', 'treatment', 'k_list']
SESSION_FIELDS = ['number_of_trials']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'GBP'
USE_POINTS = True

ADMIN_USERNAME = 'charlotte'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '5755703414565'
