"""模倣に役立つツール集"""

import regex


def make_hiragana_small(text: str, size: int = 64, multiline: bool = False) -> str:
    """AviUtlでひらがなを制御文字で小さくする関数(「漢字以外を小さくする」という方が正しい)

    Args:
        text      (str) : 元のテキスト
        size      (int) : ひらがなのサイズ
        multiline (bool): Trueの場合複数行同時に表示する人向け
    """

    text_list = text.splitlines()
    lines = []
    str_size = str(size)

    is_pre_kanji = True
    kanji = regex.compile(r"\p{Script=Han}+")

    for line in text_list:
        lines.append("")
        for i in range(len(line)):
            is_kanji = not (kanji.fullmatch(line[i]) is None)
            if is_kanji == is_pre_kanji:
                # 前の文字と種類が変わらない場合
                lines[-1] += line[i]
            elif is_kanji:
                # 前の字がひらがなで、今の字が漢字の場合
                lines[-1] += "<s>" + line[i]
            else:
                # 前の字が漢字で、今の字がひらがなの場合
                lines[-1] += "<s" + str_size + ">" + line[i]
            is_pre_kanji = is_kanji
        if not multiline:
            is_pre_kanji = True
        print(f'"{line}"->"{lines[-1]}"')

    result_text = "\n".join(lines)

    return result_text
