import pandas as pd
import os
import numpy as np
from tqdm import tqdm
import random
from datetime import datetime

from sklearn.model_selection import train_test_split
from scipy import spatial

import keras
from keras import backend as K
from keras.layers import Input,Conv2D,MaxPooling2D,UpSampling2D, Conv2DTranspose
from keras.layers import Conv1D,MaxPool1D,UpSampling1D
from keras.models import Model
from keras.optimizers import RMSprop
from keras import callbacks

from typing import *

'''
Convolutional Encoder-Decoder network for song recommendations
'''
class Autoencoder:
    autoencoder = None

    @staticmethod
    def define_model(input_image: Input) -> Model:
        '''
        Defines the compiled, pre-fit Keras model

        :param input_image: the Input layer of the Keras model (requires analyzing the input shape)
        :return: the compiled, pre-fit Keras model
        '''

        # encoder
        conv1 = Conv1D(28, (5), activation='relu', padding='same', name='conv1')(input_image)
        pool1 = MaxPool1D(pool_size=(4))(conv1)
        conv2 = Conv1D(64, (5), activation='relu', padding='same', name='conv2')(pool1)
        pool2 = MaxPool1D(pool_size=(4))(conv2)
        conv3 = Conv1D(128, (5), activation='relu', padding='same', name='conv3')(pool2)

        # decoder
        conv4 = Conv1D(128, (5), activation='relu', padding='same', name='conv4')(conv3)
        up1 = UpSampling1D((4))(conv4)
        conv5 = Conv1D(64, (5), activation='relu', padding='same', name='conv5')(up1)
        up2 = UpSampling1D((4))(conv5)
        decoded = Conv1D(28, (5), activation='sigmoid', padding='same', name='conv6')(up2)

        autoencoder = Model(input_image, decoded)

        loss = keras.losses.mse
        optimizer = keras.optimizers.Adam()

        autoencoder.compile(loss=loss, optimizer=optimizer)
        print('Summary\n', autoencoder.summary())
        return autoencoder

    @staticmethod
    def pad_and_normalize(arrs: List[List[List[float]]], to_pad: int) -> np.array:
        '''
        Pads a list to make all subarrays of uniform length, then normalizes the NumPy array by column

        :param arrs: the list of lists of sequences
        :param to_pad: the length to make each array
        :return: the array as a numpy array
        '''
        dim2_length = len(arrs[0][0])

        for i in tqdm(range(len(arrs))):
            if len(arrs[i]) >= to_pad:
                arrs[i] = arrs[i][:to_pad]
            else:
                arrs[i] += [np.zeros(dim2_length) for _ in range(to_pad - len(arrs[i]))]

        arrs = np.array(arrs)  # * 1000
        # arrs = arrs.reshape([*list(arrs.shape), 1]) # Uncomment for 2D Convolutions
        arrs = arrs / arrs.max(axis=0)
        print('Arrs shape:', arrs.shape)
        return arrs

    def __init__(self, model_name: str, train=True, **kwargs):
        if train:
            self.autoencoder = self.train(model_name=model_name, **kwargs)
        else:
            self.autoencoder = self.define_model(input_image = Input(shape=kwargs.get('input_shape')))
            self.autoencoder.load_weights(os.path.join('models', model_name))

        self.get_Z_output = K.function([self.autoencoder.get_layer(name='conv1').input],
                                       [self.autoencoder.get_layer(name='conv3').output])
        self.get_recreated = K.function([self.autoencoder.get_layer(name='conv4').input],
                                              [self.autoencoder.get_layer(name='conv6').output])

    @classmethod
    def train(cls, model_name: str, arrs: List[List[List[float]]], to_pad: int,
              random_state=23, test_size=0.2, batch_size = 8, epochs = 100, verbose=True) -> Model:
        '''
        - Converts arrs (raw data as a list of lists of float values) into a numpy array by limiting each sublist
            to a uniform size
        - Normalizes the array by column
        - Splits into train/test sets and trains the model

        :param arrs: the list of lists of values to train on
        :param to_pad: length of each list
        :return: the trained model
        '''

        arrs = cls.pad_and_normalize(arrs, to_pad)
        X_train, X_test = train_test_split(arrs,
                                           test_size=test_size,
                                           random_state=random_state)

        dt = datetime.today()
        currentDate = ''.join([str(dt.year), str(dt.month), str(dt.day)])

        bestModelName = ''.join([currentDate, model_name, '_AutoEncoder', '.h5'])
        bestModelFilepath = os.path.join('.', 'models', bestModelName)

        checkpoint = callbacks.ModelCheckpoint(bestModelFilepath, monitor='val_loss', verbose=1, save_best_only=True,
                                               mode='min')
        early_stopping = callbacks.EarlyStopping(monitor='val_loss', patience=3, verbose=True)
        history = callbacks.History()

        input_image = Input(shape=arrs.shape[1:])
        autoencoder = cls.define_model(input_image)
        autoencoder.fit(X_train, X_train, batch_size=batch_size, epochs=epochs,
                        callbacks=[early_stopping, checkpoint, history], verbose=verbose, validation_split=0.2)

        return autoencoder

    def store_zVectors(self, arrs: np.array, df: pd.DataFrame) -> pd.DataFrame:
        '''
        Adds Z-Vectors to a dataframe

        :param arrs: the data we trained the autoencoder on
        :param df: the associated dataframe
        :return: the dataframe with zVectors in it
        '''
        zs = []
        print('arrs', arrs.shape)
        for i, arr in enumerate(arrs):
            zVector = self.get_Z_output([arrs[i:i + 1]])[0]
            zs.append(zVector.flatten().reshape(-1, 1))
        df['zVector'] = zs
        return df

    def get_similar(self, df: pd.DataFrame, ind: int=None, vec: np.array=None) -> pd.DataFrame:
        '''
        Gets elements in the dataframe most similar to the given element, given either by index in the dataframe or as
            a separate numpy array

        :param df: the dataframe associated with the data
        :param ind: the index of the element you're trying to analyze
        :param vec: a separate vector if you don't know the index or it's new data
        :return: the similar data as a dataframe
        '''
        def create_cosine_similarity(shoe1, shoe2):
            result = 1 - spatial.distance.cosine(shoe1, shoe2)
            return result

        if ind and vec:
            raise ValueError('Cannot use both index method and vector method - please choose one')

        if not (ind is None or vec is None):
            raise ValueError('Please provide an index or a numpy array')

        if vec:
            ex = self.get_Z_output([vec])[0].flatten().reshape(-1,1)
        else:
            ex = df['zVector'][ind]

        ll = []
        for i in df.zVector:
            ll.append(create_cosine_similarity(i, ex))

        temp = df
        temp['similarity'] = ll
        ind = temp.sort_values(by='similarity', ascending=False)
        return ind