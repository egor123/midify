import json
import argparse
import spotify
import time

def getArgs():
    parser = argparse.ArgumentParser(prog="asfy")
    subparsers = parser.add_subparsers(title='actions', dest="action")
    parser_play = subparsers.add_parser("play")
    parser_play.add_argument("-s", "--shuffle", action="store_true")
    parser_play.add_argument("-g", "--isGlobal", action="store_true")
    parser_play.add_argument(
        "-t", "--type", choices=["track", "playlist", "album", "artist"], default="playlist")
    parser_play.add_argument("name")
    parser_stop = subparsers.add_parser("stop")
    parser_next = subparsers.add_parser("next")
    parcer_continue = subparsers.add_parser("cont")
    return parser.parse_args()


def main():
    with open("config.json") as f:
        config = json.load(f)
    sp_core = spotify.Core(
        config['request_timeout'], config['request_retries'])
    args = getArgs()
    if args.action == "play":
        if (args.type != "playlist"):
            args.isGlobal = True
        sp_core.sp.shuffle(args.shuffle)
        sp_core.set_uri(args.name, args.isGlobal, args.type)
    elif args.action == "cont":
        sp_core.sp.start_playback()
    elif args.action == "stop":
        sp_core.sp.pause_playback()
    elif args.action == "next":
        sp_core.sp.next_track()

    time.sleep(1)
    print(sp_core.sp.current_user_playing_track()["item"]["name"])


if __name__ == "__main__":
    main()
