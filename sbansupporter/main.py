import regex
import mido
from PIL import Image, ImageDraw
import math
import os


def num_to_midi(text: str, path: str, time: int = 120):
    """バイナリデータのテキストをMIDIに変換する関数(36進数まで対応してます)

    Args:
        text (str): テキスト
        path (str): 出力するMIDIファイルのパス
        time (int): 1クリックあたりの長さ
    """

    mid = mido.MidiFile()
    track = mido.MidiTrack()

    for i in range(len(text)):
        note = 0
        if text[i].isdigit():
            note = int(text[i])
        elif text[i].isalnum():
            note = ord(text[i].upper()) - 55
        else:
            continue
        track.append(mido.Message("note_on", note=60 + note, velocity=64, time=0))
        track.append(mido.Message("note_off", note=60 + note, velocity=64, time=time))

    print(track)

    mid.tracks.append(track)
    mid.save(path)
    print(f"{path}を出力しました")


def morse_to_midi(
    text: str,
    out: str,
    time: int = 120,
    dit: tuple = (".", "・"),
    dah: tuple = ("-", "ー"),
    space: tuple = (" ", "　"),
):
    """モールス信号のテキストをMIDIに変換する関数

    Args:
        text  (str): モールス信号のテキスト
        out   (str): 出力するMIDIファイルのパス
        dit   (tuple): 点にあたる文字
        dah  (tuple): 線にあたる文字
        space (tuple): 空白にあたる文字
        time  (int): 点あたりの長さ
    """
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    space_num = 0

    for i in list(text):
        if i in dit:
            track.append(mido.Message("note_on", note=60, velocity=64, time=space_num))
            track.append(mido.Message("note_off", note=60, velocity=64, time=time))
            space_num = 0
        elif i in dah:
            track.append(mido.Message("note_on", note=60, velocity=64, time=space_num))
            track.append(mido.Message("note_off", note=60, velocity=64, time=time * 2))
            space_num = 0
        elif i in space:
            space_num += time

    print(track)

    mid.tracks.append(track)
    mid.save(out)
    print(f"{out}を出力しました")


def tenji_to_midi(text: str, out: str, time: int = 120):
    """点字のテキストをMIDIに変換する関数

    Args:
        text (str): 点字のテキスト
        out  (str): 出力するMIDIファイルのパス
        time (int): 1クリックあたりの長さ
    """
    text_list = list(text)
    base16 = [x.encode(encoding="unicode-escape") for x in text_list]
    base16_str = [x.decode(encoding="utf-8")[2:] for x in base16]
    base10 = [int(x, 16) for x in base16_str]
    base10_format = [x - 10240 for x in base10]
    base2 = [bin(x)[2:] for x in base10_format]
    base2_filled = [x.zfill(6) for x in base2]
    base2_split = []
    for x in base2_filled:
        base2_split.append(x[3:])
        base2_split.append(x[:3])
    print(base2_split)

    mid = mido.MidiFile()
    track = mido.MidiTrack()
    space = 0

    for x in base2_split:
        if x == "000":
            space += time
            continue
        for y in range(len(x)):
            if x[y] == "1":
                track.append(
                    mido.Message("note_on", note=60 + int(y), velocity=64, time=space)
                )
                space = 0
                print(track[-1])
        track.append(mido.Message("note_off", note=62, velocity=64, time=time))
        track.append(mido.Message("note_off", note=61, velocity=64, time=0))
        track.append(mido.Message("note_off", note=60, velocity=64, time=0))

    print(track)

    mid.tracks.append(track)
    mid.save(out)
    print(f"{out}を出力しました")


def midi_to_image(path: str, out: str, length: int = 12, mode: int = 0):
    """MIDIを画像に変換する関数

    Args:
        path  (str): MIDIファイルのパス
        out   (str): 出力するフォルダのパス
        length(int): 1ピクセルあたりの長さ
        mode  (int): モード（0=最終画像のみ、1=経過画像も）
    """

    im_height = 120  # 画像の高さ
    im_length = 0  # 画像の長さ(後で再定義)

    mid = mido.MidiFile(path)
    mid_length = 0

    for i, track in enumerate(mid.tracks):
        for msg in track:
            mid_length += msg.time
    im_length = math.ceil(mid_length / length)

    im = Image.new("RGB", (im_length, im_height), (0, 0, 0))
    draw = ImageDraw.Draw(im)
    im_time = 0
    note_list = []

    for i, track in enumerate(mid.tracks):
        for msg in track:
            im_time += math.floor(msg.time / length)
            if msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                # ベロシティが0のnote_onはnote_off扱い
                draw.rectangle(
                    xy=(im_time, im_height - msg.note, im_length, im_height - msg.note),
                    fill=(0, 0, 0),
                )

                for m, n in enumerate(note_list):
                    if n["note"] == im_height - msg.note:
                        note_list_index = m
                note_list[note_list_index]["time"] = (
                    im_time - note_list[note_list_index]["start"] - 1
                )
                print(msg)
            elif msg.type == "note_on":
                draw.rectangle(
                    xy=(im_time, im_height - msg.note, im_length, im_height - msg.note),
                    fill=(255, 255, 255),
                )
                note_list.append(
                    {"start": im_time, "time": 0, "note": im_height - msg.note}
                )
                print(msg)

    if not os.path.exists(out):
        os.makedirs(out)

    if out[-1] == "\\":  # パスの最後にバックスラッシュがつく場合
        im.save(f"{out}export.png", quality=95)
        print(f"{out}export.pngを出力しました")
    else:
        im.save(f"{out}\\export.png", quality=95)
        print(f"{out}\\export.pngを出力しました")

    if mode != 1:
        return

    # ここからmode1のみ
    im = Image.new("RGB", (im_length, im_height), (0, 0, 0))
    draw = ImageDraw.Draw(im)
    im_time = 0
    i = 0
    export_num = 0
    while i < len(note_list):
        j = i
        while note_list[i]["start"] == note_list[j]["start"]:
            draw.rectangle(
                xy=(
                    note_list[i]["start"],
                    note_list[i]["note"],
                    note_list[i]["start"] + note_list[i]["time"],
                    note_list[i]["note"],
                ),
                fill=(255, 255, 255),
            )
            print(note_list[i])
            i += 1
            if len(note_list) <= i:
                break

        if out[-1] == "\\":  # パスの最後にバックスラッシュがつく場合
            if not os.path.exists(f"{out}export"):
                os.makedirs(f"{out}export")
            im.save(f"{out}export\\export{export_num}.png", quality=95)
            print(f"{out}export\\export{export_num}.pngを出力しました")
        else:
            if not os.path.exists(f"{out}\\export"):
                os.makedirs(f"{out}\\export")
            im.save(f"{out}\\export\\export{export_num}.png", quality=95)
            print(f"{out}\\export\\export{export_num}.pngを出力しました")

        export_num += 1

    return


def midi_to_num(path: str) -> list:
    """MIDIから音の高さだけを抜き出す関数

    Args:
        path (str): MIDIファイルのパス
    """
    mid = mido.MidiFile(path)

    result = [msg.note for msg in mid.tracks[0] if msg.type == "note_on"]

    return result


def make_hiragana_small(text: str, size: int = 60, mode: int = 0) -> str:
    """AviUtlでひらがなを制御文字で小さくする関数(「漢字以外を小さくする」という方が正しい)

    Args:
        text (str): 元のテキスト
        size (int): ひらがなのサイズ
        mode (int): モード (0は1行ずつ表示する場合向け、1は複数行同時に表示する場合)
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
        if mode == 0:
            is_pre_kanji = True
        print(f'"{line}"->"{lines[-1]}"')

    result_text = "\n".join(lines)

    return result_text
