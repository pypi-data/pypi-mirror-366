# jack_midi_keyboard

Provides a comfy interface to python from a MIDI keyboard via JACK.

Running from the command line will simply demonstrate its usage, printing out
the notes played on the first physical MIDI input found:

	python -m jack_midi_keyboard

An example of using this package:

	from jack_midi_keyboard import JackMidiKeyboard

	def note_on(channel, pitch, velocity, *_):
		print(f' {channel:02d}  {pitch:02d}  {velocity:02d}')

	def note_off(channel, pitch, *_):
		print(f' {channel:02d}  {pitch:02d}')

	with JackMidiKeyboard(auto_connect = True) as kbd:
		kbd.on_note_on(note_on)
		kbd.on_note_off(note_off)
		input()	# Causes execution to wait for user input

You can also extend the JackMidiKeyboard class with your own class.

## Versatility

Although this package is named "jack_midi_keyboard", this class can be used to
receive MIDI events from any kind of Jack MIDI output port, software or
hardware.
