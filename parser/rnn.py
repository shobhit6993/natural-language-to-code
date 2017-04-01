from __future__ import absolute_import

import logging

import tensorflow as tf

from parser.constants import TrainVariables


class LatentAttentionNetwork(object):
    """The RNN underlying the implemented model for IFTTT domain.

    This class replicates the network proposed in the following NIPS 2016 paper:

    Chen, Xinyun, Chang Liu Richard Shin Dawn Song, and Mingcheng Chen.
    "Latent Attention For If-Then Program Synthesis."
    arXiv preprint arXiv:1611.01867 (2016).

    Attributes:
        dropout (tensorflow.placeholder): Placeholder for probability of dropout
            to be used in the Dropout layer. A value of 1.0 results in no
            dropout being applied.
        inputs (tensorflow.placeholder): Placeholder for inputs to the network.
            Input should be a 2D array where the first dimension corresponds to
            batch size and the second dimension is the input dimensionality.
        labels (tensorflow.placeholder): Placeholder for true labels
            corresponding to inputs. Labels should be in the form of a 2D array,
            the first dimension being the batch size, and each row being a
            one-hot vector.
        seq_lens (tensorflow.placeholder): Placeholder for actual lenghts of
            inputs, barring the `NULL` tokens.
        dictionary_embedding (Tensor): Output of dictionary embedding layer.
            Shape=(`self._batch_size`, `self._sent_size`, `self._hidden_size`)
        rnn_embedding (tensorflow.Tensor): Output of RNN embedding layer.
            Shape=(`self._batch_size`, `self._sent_size`, 2*`self._hidden_size`)
        latent_attention (tensorflow.Tensor): Output of latent attention layer.
            Shape=(`self._batch_size`, `self._sent_size`, 1)
        active_attention (tensorflow.Tensor): Output of active attention layer.
            Shape=(`self._batch_size`, `self._sent_size`, 1)
        output_representation (tensorflow.Tensor): The output representation.
            Shape=(`self._batch_size`, 2*`self._hidden_size`, 1)
        prediction (tensorflow.Tensor): Logit predictions.
            Shape=(`self._batch_size`, `self._num_classes`, 1)
        loss (tensorflow.Tensor): Value of loss. Cross-entropy loss is used.
        optimize (tensorflow.op): Operation to optimize loss function.
        error (Tensor): Value of classification error.
    """

    def __init__(self, config, num_classes, train_vars):
        """Sets hyper-parameter values based on the passed `config`

        Args:
            config: A configuration class, similar to
                `configs.PaperConfigurations`.
            num_classes (int): Total number of label classes.
            train_vars (TrainVariables): The mode that determines which set of
                model parameters should be modified during training.
                The mode `TrainVariables.all` causes all model parameters to be
                learned during training.
                The mode `TrainVariables.non_attention` results in only the 
                model parameters that are not part of the attention mechanism 
                to be learned. This includes only the variable named "p".
                The mode `TrainVariables.attention` results in all the attention
                related parameters being learned. This includes all variables 
                except "p".
        """
        self.dropout = tf.placeholder(tf.float32, name='dropout')
        self._learning_rate = config.learning_rate
        """float: Learning rate for optimizer."""
        self._max_gradient_norm = config.max_gradient_norm
        """float: Maximum norm of gradients. If the norm of gradients go above
        this value, they are rescaled."""

        self._hidden_size = config.hidden_size
        """int: Size of embedding for each token, as output by dictionary
        embedding. In the paper, twice of this value is denoted by d."""
        self._batch_size = config.batch_size
        """int: Size of mini-batch, i.e., number of examples in `self.inputs`"""
        self._vocab_size = config.vocab_size
        """int: Size of vocabulary. In the paper, this value is denoted by N."""
        self._sent_size = config.sent_size
        """int: Maximum size of each description. In the paper, this value is
        denoted by j."""
        self._num_classes = num_classes
        """int: Total number of label classes. In the paper, this value is
        denoted by M."""

        self._initializer = tf.random_uniform_initializer(-1, 1)
        """: Initializer to be used to initialize all tensorflow variables. This
        is same as the one proposed in the paper."""

        self.inputs = tf.placeholder(tf.int32,
                                     [None, self._sent_size], 'inputs')
        self.labels = tf.placeholder(tf.float32,
                                     [None, self._num_classes], 'labels')
        self.seq_lens = tf.placeholder(tf.int32, [None], 'seq_lens')

        self.dictionary_embedding = self.dictionary_embedding_layer()
        self.rnn_embedding = self.rnn_embedding_layer()
        self.latent_attention = self.latent_attention_layer()
        self.active_attention = self.active_attention_layer()
        self.output_representation = self.output_representation_layer()
        self.prediction = self.prediction_layer()
        self.loss = self.loss_layer()
        self.optimize = self.optimize_layer(train_vars)
        self.error = self.error_layer()

    def dictionary_embedding_layer(self):
        """Constructs the dictionary embedding layer.

        The dictionary embedding layer is essentially a lookup-table where each
        token in the vocabulary is mapped to an embedding vector.

        Returns:
            tensorflow.Tensor: Output of dictionary embedding layer.
            Shape=(?, `self._sent_size`, `self._hidden_size`)
        """
        dict_embedding_matrix = tf.get_variable(
            name="dict_embedding_matrix",
            shape=[self._vocab_size, self._hidden_size],
            dtype=tf.float32, initializer=self._initializer)
        return tf.nn.embedding_lookup(dict_embedding_matrix, self.inputs)

    def rnn_embedding_layer(self):
        """Constructs the RNN embedding layer.

        In keeping with the paper, a Bidirectional LSTM is used to embed each
        token -- input to the RNN is in the form of an intermediate
        embedding returned by the Dictionary Embedding layer -- in a
        2*`self._hidden_size` space. The embedding is obtained by concatenating
        the outputs of the two LSTMs.

        Returns:
            tensorflow.Tensor: Output of RNN embedding layer.
            Shape=(?, `self._sent_size`, 2*`self._hidden_size`)
        """
        # The forward LSTM cell.
        cell_fw = tf.nn.rnn_cell.LSTMCell(
            num_units=self._hidden_size, initializer=self._initializer)
        # Add dropout wrapper to the cell.
        cell_fw = tf.nn.rnn_cell.DropoutWrapper(cell=cell_fw,
                                                input_keep_prob=self.dropout,
                                                output_keep_prob=self.dropout)

        # The backward LSTM cell.
        cell_bw = tf.nn.rnn_cell.LSTMCell(
            num_units=self._hidden_size, initializer=self._initializer)
        # Add dropout wrapper to the cell.
        cell_bw = tf.nn.rnn_cell.DropoutWrapper(cell=cell_bw,
                                                input_keep_prob=self.dropout,
                                                output_keep_prob=self.dropout)

        # Construct Bidirectional LSTM using the two cells.
        outputs, states = tf.nn.bidirectional_dynamic_rnn(
            cell_fw=cell_fw, cell_bw=cell_bw, inputs=self.dictionary_embedding,
            sequence_length=self.seq_lens, dtype=tf.float32)

        rnn_output_fw, rnn_output_bw = outputs[0], outputs[1]
        # Concatenate the output of the two LSTMs.
        rnn_output_concatenated = tf.concat(2, [rnn_output_fw, rnn_output_bw],
                                            name="rnn_output_batched")
        return rnn_output_concatenated

    def latent_attention_layer(self):
        """Constructs the Latent Attention layer.

        Latent Attention outputs a set of weights over the input tokens, one
        set over each input.

        Returns:
            tensorflow.Tensor: Output of latent attention layer.
            Shape=(`self._batch_size`, `self._sent_size`, 1)
        """
        u = tf.get_variable(name="u", shape=[2 * self._hidden_size, 1],
                            dtype=tf.float32,
                            initializer=self._initializer)
        # Convert `rnn_embedding` to 2D tensor
        embed = tf.reshape(self.rnn_embedding,
                           shape=[-1, 2 * self._hidden_size])
        l_pre_softmax = tf.matmul(embed, u)
        l_pre_softmax = tf.reshape(l_pre_softmax,
                                   shape=[-1, self._sent_size, 1],
                                   name="l_pre_softmax")
        return tf.nn.softmax(l_pre_softmax, dim=1, name="l")

    def active_attention_layer(self):
        """Constructs the Active Attention layer.

        Active Attention outputs a set of weights over the input tokens, one
        set over each input. It utilizes the latent attention weights to come
        up with a new set of weights.

        Returns:
            tensorflow.Tensor: Output of active attention layer.
            Shape=(`self._batch_size`, `self._sent_size`, 1)
        """
        v = tf.get_variable(name="v",
                            shape=[2 * self._hidden_size, self._sent_size],
                            dtype=tf.float32, initializer=self._initializer)
        # Convert rnn_embedding to 2D tensor
        embed = tf.reshape(self.rnn_embedding,
                           shape=[-1, 2 * self._hidden_size])
        a_pre_softmax = tf.matmul(embed, v)
        a_pre_softmax = tf.reshape(a_pre_softmax,
                                   shape=[-1, self._sent_size, self._sent_size],
                                   name="a_pre_softmax")
        a = tf.nn.softmax(a_pre_softmax, dim=1, name="a")
        w = tf.batch_matmul(a, self.latent_attention, name="w")
        return w

    def output_representation_layer(self):
        """Constructs the Output Representation layer.

        Output layer embeds the entire description in a 2*`self._hidden_size`
        space.

        Returns:
            tensorflow.Tensor: The output representation.
            Shape=(`self._batch_size`, 2*`self._hidden_size`, 1)
        """
        w_normalized = tf.nn.l2_normalize(self.active_attention, dim=1,
                                          name="w_normalized")
        embed = tf.transpose(self.rnn_embedding, [0, 2, 1])
        return tf.batch_matmul(embed, w_normalized, name="o")

    def prediction_layer(self):
        """Constructs the final Prediction layer.

        The output of this layer can be interpreted as unscaled probabilities of
        the input belonging to each class.

        Returns:
            Logit predictions.
            Shape=(`self._batch_size`, `self._num_classes`, 1)
        """
        p = tf.get_variable(name="p",
                            shape=[self._num_classes, 2 * self._hidden_size],
                            dtype=tf.float32, initializer=self._initializer)
        initializer = tf.zeros([self._num_classes, 1])
        pred = tf.scan(lambda a, o: tf.matmul(p, o), self.output_representation,
                       initializer=initializer)
        return tf.reshape(pred, shape=[-1, self._num_classes],
                          name="log_predictions")

    def loss_layer(self):
        """Calculates the cross-entropy loss."""
        return tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(self.prediction,
                                                    self.labels),
            name="loss")

    def optimize_layer(self, train_vars):
        """Sets up the optimizer to be used for minimizing the loss function.

        Adam Optimizer is used.
        
        Args:
            train_vars (TrainVariables): The mode that determines which set of
                model parameters should be modified during training.
                The mode `TrainVariables.all` causes all model parameters to be
                learned during training.
                The mode `TrainVariables.non_attention` results in only the 
                model parameters that are not part of the attention mechanism 
                to be learned. This includes only the variable named "p".
                The mode `TrainVariables.attention` results in all the attention
                related parameters being learned. This includes all variables 
                except "p".

        Returns:
            tensorflow.Operation: Operation to be executed to perform
            optimization.
        """
        var_list = []
        if train_vars is TrainVariables.all:
            var_list = tf.trainable_variables()
        elif train_vars is TrainVariables.non_attention:
            var_list = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,
                                        scope='p')
        elif train_vars is TrainVariables.attention:
            all_vars = tf.trainable_variables()
            for var in all_vars:
                if "p:" not in var.name:
                    var_list.append(var)
        else:
            logging.error("Illegal type of `train_vars`: %s", train_vars)
            raise TypeError

        logging.info("Optimizing these variables: %s",
                     [var.name for var in var_list])
        optimizer = tf.train.AdamOptimizer(self._learning_rate)
        grads_and_vars = optimizer.compute_gradients(self.loss,
                                                     var_list=var_list)
        capped_grads_and_vars = [
            (tf.clip_by_norm(grad, self._max_gradient_norm), var)
            for grad, var in grads_and_vars]
        return optimizer.apply_gradients(capped_grads_and_vars)

    def error_layer(self):
        """Calculates the classification error."""
        mistakes = tf.not_equal(tf.argmax(self.labels, 1),
                                tf.argmax(self.prediction, 1))
        return tf.reduce_mean(tf.cast(mistakes, tf.float32), name="error")
