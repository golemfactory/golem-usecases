Tensorflow uses only one source of randomness, which is tf.set_random_seed(x)
As for CPU, it works very well:
Not as in cases of keras and pytorch, produced (.data) files are exactly the same (checked with diff).

On the other hand, coding in tensorflow is very tedious and debugging is horror...

TODO check how's the determinism on GPU
