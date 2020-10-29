from modext.config import Config


def sample():

    cfg = Config("/samples/data/sample.json.cfg")
    cfg.load()

    print(cfg)
    return cfg


# from samples.config_sample import sample
