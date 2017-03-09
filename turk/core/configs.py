class Configs(object):
    use_full_test_set = False
    use_english = False
    use_english_intelligible = False
    use_gold = True

    log_level = "DEBUG"

    trigger_fns_csv = "./ifttt/data/label-maps/trigger-functions.csv"
    action_fns_csv = "./ifttt/data/label-maps/action-functions.csv"
    log_directory = "./experiments/turk/dummy/"
