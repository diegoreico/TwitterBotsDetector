import logging

import pandas as pd
from tensorflow.python.keras.callbacks import EarlyStopping
from tensorflow.python.keras.layers import Dense, Dropout, Input
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.optimizers import SGD

from ars.config import model_config as config
from ars.models import metrics
from ars.models.utils.train_val_tensor_board import TrainValTensorBoard
from ars.utils import check_file_path


class AutoEncoder(object):
    def __init__(self, train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame = None):
        self.model: Model = None
        self.__train = train
        self.__val = val
        self.__test = test
        self.__rmse = -1

        self._build()
        self.batch_size: int = config.autoencoder_batch_size()
        self.epochs: int = config.autoencoder_epochs()
        self.__learning_rate = config.autoencoder_learning_rate()

    def _build(self):
        input_layer = Input(shape=(self.__train.shape[1],))
        encode_layer = Dense(28, activation='selu')(input_layer)
        encode_layer = Dense(56, activation='selu')(encode_layer)
        dropout_layer = Dropout(0.65)(encode_layer)
        decode_layer = Dense(56, activation='selu')(dropout_layer)
        decode_layer = Dense(28, activation='selu')(decode_layer)
        output = Dense(self.__train.shape[1], activation='selu')(decode_layer)

        self.model = Model(inputs=input_layer, outputs=output)

    def save(self):
        self._save_json()
        self._save_weights()

    def fit(self):
        self.model.compile(loss=metrics.rmse, optimizer=self.optimizer)
        self.model.fit(x=self.__train, y=self.__train,
                       batch_size=self.batch_size, epochs=self.epochs,
                       validation_data=(self.__val, self.__val),
                       callbacks=[TrainValTensorBoard(log_dir=config.log_dir()), EarlyStopping(monitor='val_loss')])

    def evaluate(self):
        if self.__test is None:
            raise Exception("No test set has been defined")

        self.__rmse = self.model.evaluate(self.__test, self.__test)
        logging.info("Root Masked Squared Error on test: {}".format(self.__rmse))

    def store_metrics(self):
        file_path = config.autoencoder_metrics_path()
        test_metrics: pd.DataFrame = pd.DataFrame.from_dict({'root_masked_squared_error': [self.__rmse]})

        check_file_path(file_path)
        test_metrics.to_csv(file_path, index=False)

    def _save_json(self):
        json_path = config.autoencoder_model_json_path()
        check_file_path(json_path)

        with open(json_path, "w") as f:
            model_json = self.model.to_json()
            model_json = model_json.replace('GlorotUniform', 'glorot_uniform')
            f.write(model_json)

    def _save_weights(self):
        weights_path = config.autoencoder_model_weights_path()
        check_file_path(weights_path)
        self.model.save_weights(filepath=weights_path)

    @property
    def optimizer(self):
        return SGD(lr=self.__learning_rate)

    @property
    def epochs(self) -> int:
        return self.__epochs

    @epochs.setter
    def epochs(self, epochs: int):
        self.__epochs = epochs

    @property
    def batch_size(self) -> int:
        return self.__batch_size

    @batch_size.setter
    def batch_size(self, batch_size: int):
        self.__batch_size = batch_size

    @property
    def model(self) -> Model:
        return self.__model

    @model.setter
    def model(self, model):
        self.__model = model
