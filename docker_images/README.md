These are docker scripts for machine learning task:
 - Image for torch part (subtasks and verification) under `torch_image`
 - Image for spearmint part (main task - hyperparams search) under `spearmint_image`
 
To build them, you also need the `entrypoint.sh` script, - current version can be found in the https://github.com/golemfactory/golem/blob/develop/apps/entrypoint.sh or dowloaded automatically using `get_current_entrypoint.sh` script.

The binary versions can be downloaded from docker hub, respectively from:
  - `jacekjacekjacekg/mlbase`
  - `jacekjacekjacekg/mlspearmint`
  
To build the images locally, you need to run
```
git clone https://github.com/imapp-pl/golem-usecases
cd golem-usecases
git checkout machine_learning
cd docker_images
docker build torch_image --tag jacekjacekjacekg/mlbase
docker build spearmint_image --tag jacekjacekjacekg/mlspearmint
```
