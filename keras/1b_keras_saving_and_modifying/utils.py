
import os
import numpy as np
import random as rn

# import tensorflow as tf

# Setting PYTHONHASHSEED for determinism was not listed anywhere for TensorFlow,
# but apparently it is necessary for the Theano backend
# (https://github.com/fchollet/keras/issues/850).

def derandom(*args, **kwargs):
    os.environ['PYTHONHASHSEED'] = '0'
    np.random.seed(7)
    rn.seed(7)



# # Limit operation to 1 thread for deterministic results.
# session_conf = tf.ConfigProto(
#     intra_op_parallelism_threads=1,
#     inter_op_parallelism_threads=1
# )

# from keras import backend as K

# tf.set_random_seed(7)
# sess = tf.Session(graph=tf.get_default_graph(), config=session_conf)
# K.set_session(sess)


from keras.callbacks import LambdaCallback

derandom_callback = LambdaCallback(on_train_begin=derandom,
                                   on_train_end=derandom,
                                   on_batch_begin=derandom,
                                   on_batch_end=derandom,
                                   on_epoch_begin=derandom,
                                   on_epoch_end=derandom)