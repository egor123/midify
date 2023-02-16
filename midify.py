from functools import reduce
from requests import ReadTimeout
from inputpanel import open_input
from midi import listen_sorted_midi_input
import spotify
import json


def set_track(name: str):
    global sp_core

    def repl(a, b, arr, v):
        return (reduce(lambda a, b: a.replace(b + " ", ""), arr, a), v) if any(i + " " in a for i in arr) else (a, b)
    if (name is not ""):
        (name, is_global) = repl(name, True, ["-l", "--loclal"], False)
        (name, is_global) = repl(name, is_global, ["-g", "--global"], True)
        (name, type) = repl(name, "playlist", ["-p", "--playlist"], "playlist")
        (name, type) = repl(name, type, ["-t", "--track"], "track")
        (name, type) = repl(name, type, ["-a", "--album"], "album")
        (name, type) = repl(name, type, ["--artist"], "artist")
        sp_core.set_uri(name, is_global, type)


async def midi_input(msg):
    global file, config, track_selector, control_dict
    print(msg)

    def get_key(msg):
        if msg.type in ["note_on", "note_off"]:
            return f"({msg.channel}, {msg.note})"
        elif msg.type in ["control_change"]:
            return f"({msg.channel}, {msg.control})"
    try:
        key = get_key(msg)
        note_dict = json.load([file][file.seek(0)])
        if (msg.type is "note_on" and key in config['track_btns']):
            track = note_dict.get(key, ["", "", ""])[track_selector]
            open_input("", set_track) if track is "" else set_track(track)
        elif (msg.type is "note_off" and key in config['track_btns'] and msg.time >= 0.5):
            def set_dict_value(s):
                input[track_selector] = s
                note_dict.update({key: input})
                file.truncate(file.seek(0))
                file.write(json.dumps(note_dict, indent=4))
                file.flush()
                set_track(s)
            input = note_dict.get(key, ["", "", ""])
            open_input(input[track_selector], set_dict_value)
        elif (msg.type is "control_change"):
            control_dict.get(key, lambda _: '')(msg.value)
    except ReadTimeout as e:
        print(e)
        await midi_input(msg)
    except Exception as e:
        print(e)


def main():
    global file, config, control_dict, track_selector, sp_core
    with open("config.json") as f:
        config = json.load(f)
    sp_core = spotify.Core(
        config['request_timeout'], config['request_retries'])
    track_selector = 0
    ctrls = config['action_ctrls']
    control_dict = {
        ctrls['pause']: lambda v: sp_core.sp.pause_playback(),
        ctrls['start']: lambda v: sp_core.sp.start_playback(),
        ctrls['volume']: lambda v: sp_core.sp.volume(int(v / 127 * 100)),
        ctrls['repeat']: lambda v: sp_core.sp.repeat(["off", "context", "track"][round(v / 127 * 2)]),
        ctrls['track']: lambda v: [sp_core.sp.next_track, sp_core.sp.previous_track][v < 63](),
        ctrls['shuffle_on']: lambda v: sp_core.sp.shuffle(True),
        ctrls['shuffle_off']: lambda v: sp_core.sp.shuffle(False),
        ctrls['time']: lambda v: sp_core.sp.seek_track(sp_core.sp.current_playback()["progress_ms"] + (v - [64, 63][v < 63]) * 10000),
        ctrls['selector']: lambda v: globals().update({"track_selector": round(v / 127 * 2)}),
    }
    with open("settings.json", "r+") as file:
        listen_sorted_midi_input(config['request_frequency'], midi_input)


if __name__ == "__main__":
    main()
