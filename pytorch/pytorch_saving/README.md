Pytorch seems to have very few sources of randomness:
 - main seed in torch.manual_seed(x)
 - seeds in python random, numpy random etc are required only if there is explicite usage of these libraries
 - GPU seeds torch.cuda.manual_seed_all(x)
 - GPU nondeterminism, can be turned off by changing torch.backends.cudnn.enabled = False (only operations in CUDNN are non-deterministic

thread with randomness issues:
https://discuss.pytorch.org/t/non-determinisic-results/459

Pytorch saving has to be done manually, as in the ImageNet example:
https://discuss.pytorch.org/t/saving-and-loading-a-model-in-pytorch/2610/3

It is not very difficult and probably can be implemented in a very generic way.

Preliminary tests with these methods are conducted in Code.ipynb and show that there are no differences between different runs.

The saving functionality is implemented in torch.serialization in save and save_ functions.
https://github.com/pytorch/pytorch/blob/master/torch/serialization.py

**!!! It uses pickle (or cPickle) - VERY DANGEROUS**
<del> It seems quite easy to replace it by some other pickler module (pickle_module parameter in save()) </del>
No, actually it can't be replaced -.-

So, that's actually a problem that I don't have a solution for right now.
