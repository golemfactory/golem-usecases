These are docker scripts for machine learning task:
 - Image for torch part (subtasks and verification) under `torch_image`
 - Image for spearmint part (main task - hyperparams search) under `spearmint_image`
 
To build them, you also need the `entrypoint.sh` script, - current version can be found in the https://github.com/golemfactory/golem/blob/develop/apps/entrypoint.sh

The binary versions can be downloaded from docker hub, respectively from:
  - `jacekjacekjacekg/mlbase`
  - `jacekjacekjacek/mlspearmint`
