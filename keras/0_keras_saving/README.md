So, it appears keras uses many different sources of randomness:
 - numpy seed numpy.random.seed(x)
 - python random seed random.seed(x)
 - tensorflow backend: 
  - tensorflow.set_random_seed(x)
  - tensorflow threads (in session config)
 - theano backend:
  - python env flag os.environ['PYTHONHASHSEED'] = '0'

In addition, even when all these settings are fixed, keras uses h5py library to save models  
The problem is that this library keeps timestamps of last modification/access etc **inside the binary file(!)**, so it's not possible to compare files directly with diff - there has to be something like that:

Important:
The order of setting seeds matters:
As the code in Code.ipynb:
```
import os
import numpy as np
import random as rn
import tensorflow as tf

# Setting PYTHONHASHSEED for determinism was not listed anywhere for TensorFlow,
# but apparently it is necessary for the Theano backend
# (https://github.com/fchollet/keras/issues/850).
os.environ['PYTHONHASHSEED'] = '0'
np.random.seed(7)
rn.seed(7)

# Limit operation to 1 thread for deterministic results.
session_conf = tf.ConfigProto(
    intra_op_parallelism_threads=1,
    inter_op_parallelism_threads=1
)

from keras import backend as K

tf.set_random_seed(7)
sess = tf.Session(graph=tf.get_default_graph(), config=session_conf)
K.set_session(sess)
```

(info from: https://github.com/fchollet/keras/issues/439 )


```
from keras.models import load_model
import numpy as np

model1 = load_model("./model1").get_weights()

model2 = load_model("./model2").get_weights()

for x, y in zip(model1, model2):
    assert(np.equal(x, y).all())
```

H5py mailing list thread with question about that (started by me):
https://groups.google.com/forum/#!topic/h5py/ku-F7a5qjgo

Saving is done in 
https://github.com/fchollet/keras/blob/keras-2/keras/models.py
in function save_model

`class File` definition (it is responsible for the saving behaviour)
https://github.com/h5py/h5py/blob/master/h5py/_hl/files.py
