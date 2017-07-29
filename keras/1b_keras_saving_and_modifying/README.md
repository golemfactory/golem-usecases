Weights extraction is done like
```
for layer in model.layers:
    weights = layer.get_weights() # list of numpy arrays

```
from https://github.com/fchollet/keras/issues/91

TODO check the stability, write an example
