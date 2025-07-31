#  jack_midi_keyboard/__main__.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Simple test of the JackMidiKeyboard class.
Prints note on / off events at the console.
"""
import argparse, logging, sys
from jack import JackError
from jack_midi_keyboard import JackMidiKeyboard


def print_note_on(channel, pitch, velocity, *_):
	print(f' {channel:02d}  {pitch:02d}  {velocity:02d}')


def print_note_off(channel, pitch, *_):
	print(f' {channel:02d}  {pitch:02d}')


def main():
	p = argparse.ArgumentParser()
	p.add_argument("--verbose", "-v", action="store_true", help="Show more detailed debug information")
	options = p.parse_args()
	logging.basicConfig(
		level = logging.DEBUG if options.verbose else logging.ERROR,
		format = "[%(filename)24s:%(lineno)-4d] %(message)s"
	)
	try:
		with JackMidiKeyboard(True) as kbd:
			kbd.on_note_on(print_note_on)
			kbd.on_note_off(print_note_off)
			print('#' * 80)
			print('press Return to quit')
			print('#' * 80)
			input()
		return 0
	except JackError:
		print('Could not connect to JACK server. Is it running?')
		return 1


if __name__ == "__main__":
	sys.exit(main() or 0)


#  end jack_midi_keyboard/__main__.py
