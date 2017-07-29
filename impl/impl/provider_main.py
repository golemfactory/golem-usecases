from impl import config
from impl.model import ModelRunner

if __name__ == "__main__":

    runner = ModelRunner(config.SHARED_PATH,
                         probability=1,
                         verbose=0,
                         save_model_as_dict=config.SAVE_MODEL_AS_DICT)

    runner.run_full_training()