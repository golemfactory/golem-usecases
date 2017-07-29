So, I was not able to load the model saved in keras, train it for one epoch and get the same result as training the original model for two epochs.

First problem was Tensorflow backend:

model construction (as model = Sequential(...)) and model loading (as keras.load_model(...)) are changing random states, I don't know whenever tf state, numpy state or python random state.
I can't do "derandomization", because it requires me to construct a new tf.Session for Keras, with new seed - and since all variables are initialized in one particular session, renewing K.backend.tf.session is impossible at any step of program flow except the very beginning.

# TODO maybe there is a method for hot-replacing random seed in tf.session, without constring a new one?

Theano backend is more forgiving, and it is possible to do derandomization druing training - but it still fails to deliver the same result on the provider and requestor machines (scripts).
Maybe it is because I am not saving models in the right moment - maybe I should save it on_epoch_begin and then on_epoch_end, or maybe on two consecutive on_epoch_begin, or two consecutive on_epoch_end, ...?
I've tried many combinations, and none of the worked.
During training (after initialization etc.), everything was the same in P/R environments, except actually saving the model, but I've checked that it doesn't change random state.
I have no idea what is going on, and keras is terrible to debug (main loop is hidden in the fit() - I've even tried to call fit(epochs=1) in my own training loop, but it doesn't work either), so I think the best idea is to switch libraries and try PyTorch.
