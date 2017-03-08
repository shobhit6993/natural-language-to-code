class DialogConfiguration(object):
    # Threshold over which the slot is deemed as confidently-filled without a
    # need for confirmation.
    alpha = 0.7
    # Threshold over which -- and below `alpha` -- the slot confirmed explicitly
    # before being fixed.
    beta = 0.4

    assert (alpha >= beta)
