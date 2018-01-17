ML task - description
=================

  * [Intro](#intro)
  * [Idea](#idea) - conceptual things
     * [Verification algorithm](#verification-algorithm)
        * [Sketch](#sketch)
        * [Problems](#problems)
  * [Implementation](#implementation) - concrete implementation things
     * [Description](#description)
     * [Workflow](#workflow)
  * [What's left to do](#whats-left-to-do)


## Intro

Machine learning on golem is quite difficult topic. We can't use any of the most-popular, off-the-shelf algorithms, like neural networks, because they are not designed to work in highly parallel, distributed manner (there is of course something like Distributed Gradient Descent algorithms, but they do not work well in the environment with so high latencies as Golem).

So, instead of training one network in distributed way, we focused on finding best set of metaparameters for a given model and data - *hyperparameters search*.

In the long run, there should be a switch to some external service providing tools for model selection and training, as [MLJar](https://mljar.com/) or [SigOpt](https://sigopt.com/) and only doing verification and distribution of computations on our side.

## Idea

So, what are we going to do, is:

```Given ML model (eg neural network class) and input data, find the best set of metaparameters, such that the performance on the test set is best.```

We are going to do that by training a lot of networks, with different parameters (each network is a `subtask`, the whole procedure - a `task`), choosing these parameters using some other ML method - bayesian search.


### Verification algorithm
The core difficulty in this task lies in the verification algorithm.
There have been quite a lot of effort put into designing such algorithm, with results below.

From [wiki (private golem repo)](https://github.com/imapp-pl/golem_rd/wiki/Verification):

*There is quite large class of tasks, where computation consists of many small steps run sequentially. In fact, we can model every program as sequential task, involving executing code instructions sequentially.*  
*We are now focusing on a subclass of sequential tasks, in which there is a possibility of dumping the program state and then restoring it for computation later on (so, for example, it is possible in case of machine learning algorithms, because the state is usually explicitly represented as some collection of matrices and seeds for rand() functions, and is quite hard in case of webserver, where state is implicitly represented as incoming connections, data stored in databases and so on).*

#### Sketch
The description (there are a few simplifications here) of algorithm in a **TL;DR**:

 1. Requestor sends a task to provider.
 2. Provider runs steps (epochs of training) sequentially.
 3. After every update, he commits to the solution by sending hash of the state after the change.
 4. Requestor decides if this particular state should be saved or not.
 5. If it has to be saved, provider dumps state to disk - if not, provider carries on computations.
 6. After the whole training, provider sends backs chosen states transitions, which consist of triple `(state_dump_before_transition, transition_rules, fingerprint_of_state_after_transition)`.
 7. Requestor than loads `state_dump_before_transition`, computes `state_after_transition` using `transition_rules` and compares its fingerprint with `fingerprint_of_state_after_transition`.
   - `transition_rules` are current hyperparameters, number of the current batch (for anty-cyclic buffer defense) and more. 
   - `fingerprint` function is a `small subset of network weights`. It has the benefit of being small, hard to spoof (ie it is hard to compute only part of the network - if that was easy, we would have a perfect algorithm for verification) and also the advantage of *not-being-a-hash*. We don't want to use a hash for fingerprint, because a very small change in floating-point representation or randomness would spoil the verification process, as we would not be able to compare if the results are.
 8. If all fingerprints match (or *almost-match* - taking into account floating-point arithmetic imprecision etc), the subtask is said to be correct and requestor pays provider.


The [full description (private golem repo)](https://github.com/imapp-pl/golem_rd/wiki/Verification-of-sequential-tasks) contains a deeper analysis of the problem, and also extended version of the algorithm, which is designed to allow for provider precommitment to a hash even when there is no way of broadcasting/communicating with requestor. It also has a FAQ section.


#### Problems

1. Cyclic buffer  
  First important problem is that while we are only checking single steps of solution and not some larger portions, there is a threat of attacker constructing a cyclic buffer of honest steps and then feeding it to the algorithm.  
  A deeper analysis of the problem, along with two possible solutions (**A** and **B**), is [here (private golem repo)](https://github.com/imapp-pl/golem_rd/wiki/Cyclic-buffer-problem). As the solution **A** is easier to implement (but at a cost of being less general) - it was chosen to be implemented in the task.  
  Solution in **TL;DR**: We are removing the possibilty of creating cyclic buffers by creating a stream of input data, where there are no cycles in the input stream - so the states are also non-periodic.

2. Growing memory  
  The algorithm in the current form forces user to dump a number of states. As programs' states can be very big - especially in the context of neural network (for details, see analysis [here (private golem repo)](https://github.com/imapp-pl/golem-usecases/blob/machine_learning/memory_check/memo.ipynb)).  
  But, employing some analysis of rational-agent behaviour in context of Golem, it can be showed that our memory requirements are in fact very low - see analysis [here (private golem repo)(for now in polish)(not yet reviewed)(looks better locally, github doesn't render latex properly)](https://github.com/imapp-pl/golem-usecases/blob/machine_learning/memory_check/szacunek.ipynb)

3. Seeing-results-before-paying  
  The obvious problem with this solution is that requestor can lie about correctness of the solution - eg, say that it doesn't work, when in fact it was working - not pay, and steal the solution (since he has 995/1000 step, he has in fact the whole solution).  
  The solution for that is to have a deposit and some node doing **additional verification** - when requestor does something like this, provider talks to the escrow service and it burns requestor's deposit. Since it is guaranteed that punishment will happen - provider knows that he is honest, and has all the communications with requestor signed, so he can prove his case - reqestor won't do that at all.  
  Other solutions can possibly involve `FHE` or something like that, but it is problably hard to do at the moment.  
  Important note: many times, independently, people thought that a good solution for this problem would be to pay for results as soon as they arrive, using something like *atomic swap*. However, it is not going to work, since the algorithm (read the analysis) depends on the fact that it is hard to cheat and not be caught *in the long run* - if we were to pay for every successful compitation before the end of computations, we would lose this advantage and the whole algorithm would be useless.

## Implementation

[Implementation is under `ml_task` branch, in the main golemfactory/golem repo](https://github.com/golemfactory/golem/tree/ml_task)

Implementation of neural network training is done in `PyTorch`. It was chosen after a careful consideration, [this repository (golem private repo)](https://github.com/imapp-pl/golem-usecases/tree/machine_learning) contains a rather unstructured recording of experiments done, plus a number of arugments for and agains each popular framework. **TL;DR** the main reason was the ability to handle randomness easily (so `keras` was out) and then the ease of extending and debugging (so `TF` was out).  
Docker image for this part is available under `golemfactory/mlbase` dockerhub, Dockerfile - under `apps/mlpoc/resources/images/Dockerfile_torch`. It's fairly generic (maybe without that pytorch installation line), downloading `anaconda` distribution and swapping `/usr/bin/python` with version from `conda`.


Implementation of hyperparameters search is done in `spearmint`. It was also chosen after a careful consideration: bayesian optimization has strong mathematical foundations, so there is a lot that can be done to extend the solution and reason about it, the license is ok, the comparision between hyperparameters-tuning software maybe doesn't really favour `spearmint`, but differences are not too big [(see paper here)](http://www.cs.ubc.ca/~hutter/papers/13-BayesOpt_EmpiricalFoundation.pdf). There is also a great advantage of simplicity - `spearmint` can be run in the special `spearmint-lite` mode, which is a single python file (plus some dependencies), which does all computations. All the communications is done by updating file, which is a great convinience, when we have to communicate between docker container and task running outside container.  
Docker image for this part is available under `golemfactory/mlspearmint` dockerhub, Dockerfile - under `apps/mlpoc/resources/images/Dockerfile_spearmint`. It's very different than `mlbase`, because development of this version of `spearmint` was ceased a long time ago. (after that they moved to more restrictive license), so we can't use off-the-shelf `anaconda` distribution.



### Description 
There are three distinct parts of the task:

 1. Training part: it is done inside docker container, on provider's machine. Main script: `provider_main.py`. The code for that is under `mlpoc/resources/impl/`. To understand this part, you don't need any knowledge about other parts, only how the algorithm of verification works.
 Inside docker container, code for training the network is put under `$RESOURCES_DIR/code`, data - under `$RESOURCES_DIR/data`.  
 Since currently only the basic verification algorithm is implemented - with black box on the requestors machine - provider needs a way of communicating with requestor. It is done by messages - outcoming messages files are placed under `$MESSAGE_OUT_DIR` and incoming are read from `$MESSAGE_IN_DIR`.
 2. Parameters search part: it is done inside docker container, but this time on the requestor's machine. Main script: `docker_spearmint.py`. Although it could be in principle done on the provider's machine as well (since `spearmint` can be quite resources-heave), it is not clear what are the dangers of that (colluding problem). The main script waits for a special signal file - when it is found, it runs an appropriate shell command to run `spearmint-lite` update and then deletes the signal file.
 Signal files are not managed by any message framework, because it is only implemented for `DockerJob` and not for `LocalComputer`.
 The code for this part is also found in the `spearmint_utils.py` file - there are all functions for creating signals, reading results, updating config file etc.  
 3. Verification part: it is done inside docker container on the requestor's machine. Main script: `requestor_verification.py`. It is run after getting results from training. Checkpoint files for verification are placed under `$RESOURCES_DIR/checkpoints` (code - as before - under `$RESOURCES_DIR/code`, data under `$RESOURCES_DIR/data`).

### Full workflow

The workflow of the task:
 1. `golemcli` is started, then after some core-level stuff `MLPOCTaskBuilder` is created and feeded with dictionary containing data from `ml.json` input file.
 2. `MLPOCTaskBuilder` builds `MLPOCTaskDefinition`, constructing `MLPOCTaskOptions`, casting types etc (in `build_full_definition`).
 1. After `MLPOCTaskDefinition` is constructed, its method `add_to_resources` is called - temporary directories structure for task execution is created (eg `code`, `data` files are linked or copied in appropriate places).
 2. `MLPOCTask` is constructed, taks variables are set.
 3. `MLPOCTask` method `initialize()` is called, `LocalComputer` with `spearmint` image is constructed, directory structure for `spearmint` is crated, along with `config.cfg` file specifying parameters space to be searched (types and sizes of variables), and then `LocalComputer` is started.
 4. `MLPOCTask` is waiting for `query_additional_data` queries.
 5. If it gets one, it updates `spearmint` state, by using signal file - `spearmint` then adds a new row to the list of suggestions of next points.
 6. `MLPOCTask` gets this new suggestion, constructs `"network_configuration"` dict entry in `extra_data`, which is a list in form of `[(variable_name, variable_value)]` and sends it to the provider - it is then saved in the `params.py`.
 7.  Provider starts working - `ModelRunner` is constructed and run.
 8. **START** Every epoch, it calls `box_callback` to check if he should save the dump of the current state transition. 
 8. `box_callback` saves a message - the question to the requestor - in the `$MESSAGES_OUT_DIR` directory, then it is actively waiting for response (a message in the `$MESSAGES_IN_DIR`).
 9. In the meantime, `TaskServer` (on the providers side) is running in the loop, calling `sync_network` periodically. Inside, it calls `check_for_new_messages` on `TaskComputer`, which then calls it on all `DockerTaskThreads` in the current computations list, which then read messages from `$MESSAGES_OUT_DIR`, pack them into structures and return to `TaskServer`.
 10. `TaskServer` then collects all the messages from all current computations, packs them into `MessageProvToReqSubtask` messages and sends by appropriate `TaskSession`s to  TaskSessions of requestors.
 10. `TaskSession` on requestor side receives message and reacts by `_react_to_provider_to_requestor_message()`, which runs `respond_to_message` method in the `MLPOCTask`.
 11. `MLPOCTask` passes message contents (eg hash of the state) to subtask's-that-send-the-message `black_box`, receives answer (to save or not to save) and returns it to `TaskSession`.
 12. `TaskSession` packs the response into `MessageReqToProvSubtask` and sends it to provider's 'TaskSession`.
 13. Provider's TaskSession' reacts with `_react_to_requestor_to_provider_message`, unpacks the data, passes it into `TaskComputer.receive_message()` method, which then passes it into appropriate `DockerTaskThread` from `current_computations`, which then saves the requestors response data (containing answer `True/False` and some metadata) in the `$MESSAGE_IN_DIR`.
 14. Then `box_callback` from **11** sees the message, reads it, informs `ModelRunner` if it should save the model or not. If it should, it saves model under `$OUTPUT_DIR/EPOCH_NUM/EPOCH_NUM-hash_of_begin_state.begin` and `$OUTPUT_DIR/EPOCH_NUM/EPOCH_NUM-hash_of_end_state.end` and  we are back at the step **START**.
 15. When provider finishes work, he saves evaluation of the whole network under `$OUTPUT_DIR/results.score` json file, which contains a dict of one key: `{score: hyperparameters}`, where hyperparameters are these hyperparams got from `MLPOCTask` at the beginning of subtask.
 16. Then, verificator is called, with these result files list. As the files are not transferred properly, but in the form of list of files (eg directory structure is lost), verificator class has to rebuild that.  
 In function `_check_files` it constructs `code_place`, `data_place` and `checkpoints` directories, copies or links files there and starts a `LocalComputer` docker process, with main src file `requestor_verification.py`.  
 17. Inside docker, this script opens up each epoch directory, trains the `.begin` model for one epoch and checks if the result is the same as the `.end`. For now, it doesn't take into account the possibility of slight variation in results. It also checks if the model's hash is really the name of the file.
 18. If every epoch was tested successfully, process exits with `code 0`. Otherwise, it throws `Exception` and exits with `code != 0`.
 19. `CoreTask` takes care of later steps.

### Running

To run the task, you need to checkout the `ml_task` branch from main golem repository (if it is not merged yet).
Then, run two instances of Golem with 
```
python golemapp.py --datadir $TMPDIR_PRV -r 127.0.0.1:61002 --nogui
python golemapp.py --datadir $TMPDIR_REQ -r 127.0.0.1:61000 --nogui -p 127.0.0.1:40102
```

The order of these commands is important! It is done this way because golem starts its first instance under `40102` port. We're using different protocol versions than the rest of the golem (`TASK_PROTOCOL_ID=51` and `P2P_PROTOCOL_ID=41`), so Golem requestor node wouldn't be able to discover the provider node if not the hardcoded seed. The reason to use different protocol versions is to make debugging easier - you can set up your IDE to run these commands in debug mode, and then you can debug the code with no other nodes constantly asking for tasks headers etc.

`$TMPDIR_PRV` and `$TMPDIR_REQ` are just some temporary directories (can be anything, can be even not exitsing ones - golem will create them).

So, when you have two golem instances started, you can submit the task by running  
```
golemcli tasks create $GOLEM_HOME/apps/mlpoc/test_data/ml.json
```
This `json` file contains some parameters of the task (you're free to modify it) and it's the only way to start before appropriate GUI module will be created.


## What's left to do
The most basic task is finished, but there are still areas in which it should be significantly improved.

Issues (private golem repo):
 - [Issue #114 GPU support for MLPOCTask](https://github.com/imapp-pl/golem_rd/issues/114)
 - [Issue #115 Controlling randomness in MLPOCTask](https://github.com/imapp-pl/golem_rd/issues/115)
 - [Issue #116 Cross validation and train-test split in MLPOCTask](https://github.com/imapp-pl/golem_rd/issues/116)
 - [Issue #117 Model and data flexibility in MLPOCTask](https://github.com/imapp-pl/golem_rd/issues/117)
 - [Issue #118 MLPOCTask should inherit from DummyTask](https://github.com/imapp-pl/golem_rd/issues/118)
 - [Issue #119 Calling black box asynchronously in MLPOCTask](https://github.com/imapp-pl/golem_rd/issues/119)
 - [Issue #120 Asynchronous verification in MLPOCVerificator](https://github.com/imapp-pl/golem_rd/issues/120)
 - [Issue #121 Hashing network in MLPOCTask](https://github.com/imapp-pl/golem_rd/issues/121)
 - [Issue #122 Batch ordering and verification in MLPOCTask](https://github.com/imapp-pl/golem_rd/issues/122)
 - [Issue #135 Scoring function and score verification in MLPOCTask](https://github.com/imapp-pl/golem_rd/issues/135)
 
Additional ideas:

 - **Bayesian modelling as a way of reducing verification steps**  
 Since we are using bayesian optimizer anyway, we have access to information about *how much are we suprized with this particular network score*, where score is this final score on test set. This can be used to additionally improve verification in big-scale tasks - the probability of being checked would be somehow proportional to the degree of our "suprize".  
 Implementation-wise, it would probably require extracting probability distributions from inside `spearmint`.
