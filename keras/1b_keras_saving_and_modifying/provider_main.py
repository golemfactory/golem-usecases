from keras_adding_eps import config
from keras_adding_eps.neuralnet import NeuralNetRunner

if __name__ == "__main__":

    runner = NeuralNetRunner(config.shared_path,
                             probability=1,
                             verbose=0,
                             save_weights_only=False)

    runner.run()