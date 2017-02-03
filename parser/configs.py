from constants import NUM_SPECIAL_TOKENS


class PaperConfiguration(object):
    """
    Configurations and hyper-parameter values used in the original paper.
    """
    dropout = 1.0
    learning_rate = 0.001
    max_gradient_norm = 40.

    hidden_size = 25  # d/2
    batch_size = 32

    # (N) Number of tokens in vocabulary, including special ones.
    vocab_size = 4000 + NUM_SPECIAL_TOKENS
    sent_size = 25  # (j) Number of tokens in input.
    num_tokens_left = 12  # Number of tokens to be used from the left.
    num_tokens_right = 13  # Number of tokens to be used from the right.

    num_epochs = 50
