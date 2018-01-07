import re


URL_REGEX = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
CHAR_REPEAT_REGEX = r'(.)\1+'
WORD_REPEAT_REGEX = r'(\S{2,}?)\1+'
EMOJIS = ['◢▆▅▄▃ 崩╰(〒皿〒)╯潰 ▃▄▅▆◣', '◢▆▅▄▃崩╰(〒皿〒)╯潰▃▄▅▆◣', '(づ′・ω・）づ']


class Word(dict):

    def __init__(self, word, pos='__unknown__'):
        dict.__init__(self, word=word, pos=pos)
        self.word = word
        self.pos = pos


def contain_url(text):
    matched = re.search(URL_REGEX, text)

    if bool(matched):
        return True, matched.group()
    else:
        return False, None


def rm_repeat(text):
    return re.sub(
        WORD_REPEAT_REGEX, r'\1',
        re.sub(CHAR_REPEAT_REGEX, r'\1\1', text)
    )


def to_halfwidth(text):
    """Convert the query string to halfwidth."""
    """
    全形字符 unicode 編碼從 65281 ~ 65374(十六進制 0xFF01 ~ 0xFF5E)
    半形字符 unicode 編碼從 33 ~ 126(十六進制 0x21~ 0x7E)
    空格比較特殊, 全形為12288(0x3000), 半形為32(0x20)
    而且除空格外, 全形/半形按 unicode 編碼排序在順序上是對應的
    所以可以直接通過用+-法來處理非空格字元, 對空格單獨處理.
    """
    rstring = ""
    for char in text:
        code = ord(char)
        if code == 0x3000:
            code = 0x0020
        else:
            code -= 0xfee0
        if code < 0x0020 or code > 0x7e:  # fallback check
            rstring += char
        else:
            rstring += chr(code)
    return rstring


def strip_word(words):
    return [w for w in words if w.word != ' ']


def replace_emoji(sentence, tokenizer):
    inner = '#'
    outer = '_'
    emoji_dict = {}
    emoji_cnt = 1
    for emoji in EMOJIS:
        if emoji in sentence:
            symbol = outer + inner * emoji_cnt + outer
            sentence = sentence.replace(emoji, symbol)
            emoji_dict[symbol] = emoji
            emoji_cnt += 1
    return sentence, emoji_dict


def pos_emoji(words):
    return [Word(w.word, 'emo') if bool(re.match(r'_#+_', w.word)) else w for w in words]


def recover_emoji(words, emoji_dict, pos):
    if pos:
        return [Word(emoji_dict[w.word], w.pos) if bool(re.match(r'_#+_', w.word)) else w for w in words]
    else:
        return [emoji_dict[w] if bool(re.match(r'_#+_', w)) else w for w in words]


def strip_emoji(words, pos):
    if pos:
        return [Word(w.word.replace(' ', ''), w.pos) if w.pos == 'emo' else w for w in words]
    else:
        return [w.replace(' ', '') if w in EMOJIS else w for w in words]
