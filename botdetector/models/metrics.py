from tensorflow.python.keras import backend as keras

def rmse(label: int, prediction: int) -> float:
    mask_true = keras.cast(keras.not_equal(label, 0), keras.floatx())
    masked_squared_error = mask_true * keras.square((label - prediction))
    masked_mse = keras.sum(masked_squared_error, axis=-1) / keras.sum(mask_true, axis=-1)

    return keras.sqrt(masked_mse)
