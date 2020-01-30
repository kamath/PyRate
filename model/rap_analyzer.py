from model.attn_model import LSTM_Model
from typing import *
from collections import Counter

class Analyzer:
    @staticmethod
    def count_ngrams(bars: List[str]) -> Dict[int, Dict]:
        '''
        Returns the total n-grams of
        :param bars: the bars list separated by 'END'
        :return: all the n-grams within the bars
        '''
        tor = {}
        for n in range(2, len(bars)):
            grams = [tuple(bars[i + x] for i in range(n)) for x in range(len(bars) - n)]
            tor[n] = dict(Counter(grams))
            tor[n] = dict(list(filter(lambda x: x[1] > 1, tor[n].items())))
        return tor

    def __init__(self):
        self.model = LSTM_Model()

    def read_file(self, file: str) -> List[str]:
        '''
        Reads a file and returns the phonetic version of it, line by line.

        :param file: the file containing the bars
        :returns: list of vowels separated by "END"
        '''

        lines = open(file, 'r').read().split('\n')
        bars = []
        for line in lines:
            bar = []
            # Clean string - get rid of unnecessary punctuation and lowercase the whole thing
            words = ''.join([a for a in line if
                            a.isalpha() or
                            a in {'', '\'', '-', ' '}]).lower().split(' ')

            for word in words:
                p = self.model.predict(word)
                bar += p
            bars.append(bar)

        flattened = []
        bars.reverse()
        while bars:
            bar = bars.pop()
            flattened += bar
            flattened.append('END')

        return flattened

    def analyze_assonance(self, bars: List[str]) -> Dict[int, Dict[Tuple[str], int]]:
        return self.count_ngrams(bars)