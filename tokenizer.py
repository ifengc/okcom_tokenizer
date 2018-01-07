from toolz import pipe
import jieba
import jieba.posseg as pseg
import opencc
from preprocessing import Word
from preprocessing import replace_emoji, to_halfwidth, strip_word, recover_emoji, pos_emoji, strip_emoji


class TokenizerNotExistException(Exception):
    pass


class Tokenizer(object):

    def __init__(self):
        pass

    def __call__(self, sentence, pos=True):
        return self.cut(sentence, pos=pos)

    def cut(self, sentence, pos=True):
        raise NotImplementedError


class JiebaTokenizer(Tokenizer):

    def cut(self, sentence, pos=True):
        if pos:
            pairs = pseg.cut(sentence)
            tok = []

            for p in pairs:
                tok.append(Word(p.word, pos=p.flag))
            return tok
        else:
            return [Word(w) for w in jieba.cut(sentence)]


class OpenCCTokenizer(Tokenizer):

    def __init__(self, tokenizer_instance):
        self.tokenizer = tokenizer_instance

    def cut(self, sentence, pos=True):
        simplified = opencc.convert(sentence, config='tw2s.json')

        tokenized = self.tokenizer(simplified, pos=pos)

        recovered = []
        head = 0
        for tok in tokenized:
            l = len(tok.word)
            recovered.append(Word(sentence[head:head + l], pos=tok.pos))
            head += l
        return recovered


class CCEmojiJieba(Tokenizer):

    def __init__(self):
        self.tokenizer = OpenCCTokenizer(JiebaTokenizer())

    def cut(self, sentence, pos=True):
        sentence, emoji_dict = replace_emoji(sentence.strip(), 'jieba')
        words = pipe(sentence,
                     str.lower,
                     to_halfwidth,
                     self.tokenizer.cut,
                     strip_word,
                     pos_emoji)
        recovered = recover_emoji(words, emoji_dict)
        strip_words = strip_emoji(recovered)
        return strip_words
