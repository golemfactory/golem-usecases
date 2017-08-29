import numpy as np
import sys
import math
import time

def branin(x):
  return x*math.log(x)

# Write a function like this called 'main'
def main(job_id, params):
  return branin(params['X'])
