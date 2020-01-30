'''
Uses the LSTM from the model/ subdirectory to show the pronunciation prediction given lyric data
'''
def main():
    from model.rap_analyzer import Analyzer

    a = Analyzer()
    bars = a.read_file('input/lyrics/jid_never.txt')
    print('bars')
    print(a.analyze_assonance(bars))