from environs import Env

env = Env()
env.read_env()

ALLEGRORSS_HIDE_ADS = env.bool("ALLEGRORSS_HIDE_ADS", True)
ALLEGRORSS_LIMIT_OFFERS = env.int("ALLEGRORSS_LIMIT_OFFERS", 10)
