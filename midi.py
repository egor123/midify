import threading
import time
import mido
import asyncio


def listen_sorted_midi_input(read_time, callback):
    def read_midi_input_loop(midi_input: dict):
        active_notes = {}
        with mido.open_input() as inport:
            for msg in inport:
                if (msg.type is "note_on"):
                    key = (msg.type, msg.channel, msg.note)
                    msg.time = time.clock()
                    active_notes[(msg.channel, msg.note)] = msg
                elif (msg.type is "note_off"):
                    key = (msg.type, msg.channel, msg.note)
                    msg_on = active_notes.pop((msg.channel, msg.note))
                    t = midi_input[key].time if key in midi_input else 0
                    msg.time = max(time.clock() - msg_on.time, t)
                elif (msg.type is "sysex"):
                    key = (msg.type, msg.data)
                elif (msg.type is "control_change"):
                    key = (msg.type, msg.channel, msg.control)
                midi_input[key] = msg

    midi_input = {}
    t = threading.Thread(target=read_midi_input_loop, args=((midi_input,)))
    t.daemon = True
    t.start()

    async def run_callbacks(input):
        await asyncio.gather(*[callback(m) for m in input.values()])

    while True:
        start_time = time.clock()
        if len(midi_input) > 0:
            midi_input_copy = midi_input.copy()
            midi_input.clear()
            asyncio.run(run_callbacks(midi_input_copy))
        time.sleep(max(0, read_time - (time.clock() - start_time)))
