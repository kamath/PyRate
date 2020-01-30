import os
import random
import re
import string

import numpy as np
from keras.activations import softmax
from keras.layers import Input, Embedding, Dropout, Activation, LSTM, Dense, Bidirectional, Concatenate, Dot, Reshape, \
    RepeatVector, Lambda
from keras.models import Model

os.environ['KMP_DUPLICATE_LIB_OK']='True'

CMU_DICT_PATH = os.path.join(
    'input', 'cmu-pronunciation-dictionary-unmodified-07b', 'cmudict-0.7b')
CMU_SYMBOLS_PATH = os.path.join(
    'input', 'cmu-pronouncing-dictionary', 'cmudict.symbols')

# Skip words with numbers or symbols
ILLEGAL_CHAR_REGEX = "[^A-Z-'.]"

# Only 3 words are longer than 20 chars
# Setting a limit now simplifies training our model later
MIN_DICT_WORD_LEN = 2
MAX_DICT_WORD_LEN = 20

START_PHONE_SYM = '\t'
END_PHONE_SYM = '\n'

class LSTM_Model:
    @staticmethod
    def phone_list():
        phones = [START_PHONE_SYM, END_PHONE_SYM]
        with open(CMU_SYMBOLS_PATH) as file:
            for line in file:
                phones.append(line.strip())
        return [''] + phones

    @staticmethod
    def id_mappings_from_list(str_list):
        str_to_id = {s: i for i, s in enumerate(str_list)}
        id_to_str = {i: s for i, s in enumerate(str_list)}
        return str_to_id, id_to_str

    @staticmethod
    def load_clean_phonetic_dictionary():

        def is_alternate_pho_spelling(word):
            # No word has > 9 alternate pronounciations so this is safe
            return word[-1] == ')' and word[-3] == '(' and word[-2].isdigit()

        def should_skip(word):
            if not word[0].isalpha():  # skip symbols
                return True
            if word[-1] == '.':  # skip abbreviations
                return True
            if re.search(ILLEGAL_CHAR_REGEX, word):
                return True
            if len(word) > MAX_DICT_WORD_LEN:
                return True
            if len(word) < MIN_DICT_WORD_LEN:
                return True
            return False

        phonetic_dict = {}
        with open(CMU_DICT_PATH, encoding="ISO-8859-1") as cmu_dict:
            for line in cmu_dict:

                # Skip commented lines
                if line[0:3] == ';;;':
                    continue

                word, phonetic = line.strip().split('  ')

                # Alternate pronounciations are formatted: "WORD(#)  F AH0 N EH1 T IH0 K"
                # We don't want to the "(#)" considered as part of the word
                if is_alternate_pho_spelling(word):
                    word = word[:word.find('(')]

                if should_skip(word):
                    continue

                if word not in phonetic_dict:
                    phonetic_dict[word] = []
                phonetic_dict[word].append(phonetic)

        phonetic_dict = {key:phonetic_dict[key]
                         for key in random.sample(list(phonetic_dict.keys()), 5000)}
        return phonetic_dict

    @staticmethod
    def char_list():
        allowed_symbols = [".", "-", "'"]
        uppercase_letters = list(string.ascii_uppercase)
        return [''] + allowed_symbols + uppercase_letters

    def __init__(self):
        self.phonetic_dict = self.load_clean_phonetic_dictionary()
        self.example_count = np.sum([len(prons) for _, prons in self.phonetic_dict.items()])
        # Create character to ID mappings
        self.char_to_id, self.id_to_char = self.id_mappings_from_list(self.char_list())

        # Load phonetic symbols and create ID mappings
        self.phone_to_id, self.id_to_phone = self.id_mappings_from_list(self.phone_list())

        # Example:
        print('Char to id mapping: \n', self.char_to_id)

        self.CHAR_TOKEN_COUNT = len(self.char_to_id)
        self.PHONE_TOKEN_COUNT = len(self.phone_to_id)
        self.MAX_CHAR_SEQ_LEN = max([len(word) for word, _ in self.phonetic_dict.items()])
        self.MAX_PHONE_SEQ_LEN = max([max([len(pron.split()) for pron in pronuns]) for _, pronuns in self.phonetic_dict.items()])
        ATTENTION_MODEL_WEIGHTS = os.path.join(
            'input', 'predicting-english-pronunciations-model-weights', 'attention_model_weights.hdf5')
        self.attention_model()
        self.model.load_weights(ATTENTION_MODEL_WEIGHTS)

    def embed_word(self, words):
        tor = []
        for word in words:
            word = word.upper()
            word_matrix = np.zeros((self.MAX_CHAR_SEQ_LEN))
            for t, char in enumerate(word):
                word_matrix[t] = self.char_to_id[char]
            tor.append(word_matrix)
        return np.array(tor)

    def attention_model(self, hidden_nodes=256, emb_size=256):
        # Attention Mechanism Layers
        attn_repeat = RepeatVector(self.MAX_CHAR_SEQ_LEN)
        attn_concat = Concatenate(axis=-1)
        attn_dense1 = Dense(128, activation="tanh")
        attn_dense2 = Dense(1, activation="relu")
        attn_softmax = Lambda(lambda x: softmax(x, axis=1))
        attn_dot = Dot(axes=1)

        def get_context(encoder_outputs, h_prev):
            h_prev = attn_repeat(h_prev)
            concat = attn_concat([encoder_outputs, h_prev])
            e = attn_dense1(concat)
            e = attn_dense2(e)
            attention_weights = attn_softmax(e)
            context = attn_dot([attention_weights, encoder_outputs])
            return context

        # Shared Components - Encoder
        char_inputs = Input(shape=(None,))
        char_embedding_layer = Embedding(self.CHAR_TOKEN_COUNT, emb_size, input_length=self.MAX_CHAR_SEQ_LEN)
        encoder = Bidirectional(LSTM(hidden_nodes, return_sequences=True, recurrent_dropout=0.2))

        # Shared Components - Decoder
        decoder = LSTM(hidden_nodes, return_state=True, recurrent_dropout=0.2)
        phone_embedding_layer = Embedding(self.PHONE_TOKEN_COUNT, emb_size)
        embedding_reshaper = Reshape((1, emb_size,))
        context_phone_concat = Concatenate(axis=-1)
        context_phone_dense = Dense(hidden_nodes * 3, activation="relu")
        output_layer = Dense(self.PHONE_TOKEN_COUNT, activation='softmax')

        # Training Model - Encoder
        char_embeddings = char_embedding_layer(char_inputs)
        char_embeddings = Activation('relu')(char_embeddings)
        char_embeddings = Dropout(0.5)(char_embeddings)
        encoder_outputs = encoder(char_embeddings)

        # Training Model - Attention Decoder
        h0 = Input(shape=(hidden_nodes,))
        c0 = Input(shape=(hidden_nodes,))
        h = h0  # hidden state
        c = c0  # cell state

        phone_inputs = []
        phone_outputs = []

        for _ in range(self.MAX_PHONE_SEQ_LEN):
            phone_input = Input(shape=(None,))
            phone_embeddings = phone_embedding_layer(phone_input)
            phone_embeddings = Dropout(0.5)(phone_embeddings)
            phone_embeddings = embedding_reshaper(phone_embeddings)

            context = get_context(encoder_outputs, h)
            phone_and_context = context_phone_concat([context, phone_embeddings])
            phone_and_context = context_phone_dense(phone_and_context)

            decoder_output, h, c = decoder(phone_and_context, initial_state=[h, c])
            decoder_output = Dropout(0.5)(decoder_output)
            phone_output = output_layer(decoder_output)

            phone_inputs.append(phone_input)
            phone_outputs.append(phone_output)

        training_model = Model(inputs=[char_inputs, h0, c0] + phone_inputs, outputs=phone_outputs)

        # Testing Model - Encoder
        testing_encoder_model = Model(char_inputs, encoder_outputs)

        # Testing Model - Decoder
        test_prev_phone_input = Input(shape=(None,))
        test_phone_embeddings = phone_embedding_layer(test_prev_phone_input)
        test_phone_embeddings = embedding_reshaper(test_phone_embeddings)

        test_h = Input(shape=(hidden_nodes,), name='test_h')
        test_c = Input(shape=(hidden_nodes,), name='test_c')

        test_encoding_input = Input(shape=(self.MAX_CHAR_SEQ_LEN, hidden_nodes * 2,))
        test_context = get_context(test_encoding_input, test_h)
        test_phone_and_context = Concatenate(axis=-1)([test_context, test_phone_embeddings])
        test_phone_and_context = context_phone_dense(test_phone_and_context)

        test_seq, out_h, out_c = decoder(test_phone_and_context, initial_state=[test_h, test_c])
        test_out = output_layer(test_seq)

        testing_decoder_model = Model([test_prev_phone_input, test_h, test_c, test_encoding_input],
                                      [test_out, out_h, out_c])

        self.encoder = testing_encoder_model
        self.decoder = testing_decoder_model
        self.model = training_model

    def predict_attention(self, input_char_seq):
        encoder_outputs = self.encoder.predict(input_char_seq)

        output_phone_seq = np.array([[self.phone_to_id[START_PHONE_SYM]]])

        #     h = np.zeros((emb_char_input_train.shape[0], 256))
        #     c = np.zeros((emb_char_input_train.shape[0], 256))
        h = np.zeros((len(input_char_seq), 256))
        c = np.zeros((len(input_char_seq), 256))

        end_found = False
        pronunciation = ''
        while not end_found:
            decoder_output, h, c = self.decoder.predict([output_phone_seq, h, c, encoder_outputs])

            # Predict the phoneme with the highest probability
            predicted_phone_idx = np.argmax(decoder_output[0, :])
            predicted_phone = self.id_to_phone[predicted_phone_idx]

            pronunciation += predicted_phone + ' '

            if predicted_phone == END_PHONE_SYM or len(pronunciation.split()) > self.MAX_PHONE_SEQ_LEN:
                end_found = True

            # Setup inputs for next time step
            output_phone_seq = np.array([[predicted_phone_idx]])

        return pronunciation.strip().split(' ')

    def predict(self, *words):
        return self.predict_attention(self.embed_word(words))