#  jack_midi_keyboard/__init__.py
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
Provides a comfy interface to MIDI keyboards via JACK.
"""
import sys, os, logging, struct, jack
from midi_notes import (
	MIDI_NOTE_OFF,
	MIDI_NOTE_ON,
	MIDI_POLY_PRESSURE,
	MIDI_CONTROL_CHANGE,
	MIDI_PROGRAM_SELECT,
	MIDI_PRESSURE,
	MIDI_PITCH_BEND,
)

__version__ = "1.0.0"


class JackMidiKeyboard:

	__client	= None
	__port		= None
	__midi_event_callback	= None


	def __init__(self, auto_connect = False):
		"""
		Creates a Jack client and a single MIDI input port.

		Passing "auto_connect = True" will cause the client to connect to the first
		physical MIDI "output" port (which outputs MIDI events)/
		"""
		self.__client = jack.Client(self.__class__.__name__, no_start_server=True)
		self.__port = self.__client.midi_inports.register('input')
		self.__midi_event_callback = self.__null_callback
		self.__note_on_callback = self.__null_callback
		self.__note_off_callback = self.__null_callback
		self.__poly_pressure_callback = self.__null_callback
		self.__control_change_callback = self.__null_callback
		self.__program_select_callback = self.__null_callback
		self.__pressure_callback = self.__null_callback
		self.__pitch_bend_callback = self.__null_callback
		self.__client.set_process_callback(self.__process)
		self.__client.activate()
		self.__client.get_ports()
		if auto_connect:
			self.auto_connect()

	def auto_connect(self):
		for p in self.__client.get_ports(is_output = True, is_midi = True):
			logging.debug('Connecting %s to %s', p.name, self.__port.name)
			try:
				self.__port.connect(p.name)
				break
			except Exception as e:
				print(e)

	def port(self):
		return self.__port

	def __process(self, frames):
		last_frame_time = self.__client.last_frame_time
		for offset, indata in self.__port.incoming_midi_events():
			if len(indata) == 3:
				status, val1, val2 = struct.unpack('3B', indata)
			elif len(indata) == 2:
				status, val1 = struct.unpack('2B', indata)
				val2 = None
			self.__midi_event_callback(status, val1, val2, last_frame_time, offset)
			command = status & 0xF0
			channel = status & 0xF
			if command == MIDI_NOTE_ON:
				self.__note_on_callback(channel, val1, val2, last_frame_time, offset)
			elif command == MIDI_NOTE_OFF:
				self.__note_off_callback(channel, val1, last_frame_time, offset)
			elif command == MIDI_POLY_PRESSURE:
				self.__poly_pressure_callback(channel, val1, val2, last_frame_time, offset)
			elif command == MIDI_CONTROL_CHANGE:
				self.__control_change_callback(channel, val1, val2, last_frame_time, offset)
			elif command == MIDI_PROGRAM_SELECT:
				self.__program_select_callback(channel, val1, last_frame_time, offset)
			elif command == MIDI_PRESSURE:
				self.__pressure_callback(channel, val1, last_frame_time, offset)
			elif command == MIDI_PITCH_BEND:
				self.__pitch_bend_callback(channel, val1 * 128 + val2, last_frame_time, offset)


	def on_midi_event(self, callback):
		"""
		Sets the low-level MIDI event callback which receives very basic information
		from the JACK Client.

		"callback" should take these arguments:
			status_byte			MIDI status byte (i.e. 8n, 9n)
			val1				Usually MIDI pitch
			val2				Usually MIDI velocity value, but may be None
			last_frame_time		Millis since jack server start
			offset				Millis of MIDI event counting from last_frame_time
		i.e.:
			def midi_event(status_byte, val1, val2, last_frame_time, offset):
				pass

		Note:
		The callback function is called from the thread that the Jack Client is running
		in, and that it is not permitted to modify the Jack Client or any of its
		settings in this thread.
		"""
		if not callable(callback):
			raise Exception("Invalid callback")
		self.__midi_event_callback = callback

	def on_note_on(self, callback):
		"""
		Sets the high-level MIDI event callback which receives note on events.
		"callback" should take these arguments:
			channel				0 - 15
			pitch				0 - 127
			velocity			0 - 127
			last_frame_time		Millis since jack server start
			offset				Millis of MIDI event counting from last_frame_time
		i.e.:
			def note_on(channel, pitch, velocity, *_):
				pass

		Note:
		The callback function is called from the thread that the Jack Client is running
		in, and that it is not permitted to modify the Jack Client or any of its
		settings in this thread.
		"""
		if not callable(callback):
			raise Exception("Invalid callback")
		self.__note_on_callback	= callback

	def on_note_off(self, callback):
		"""
		Sets the high-level MIDI event callback which receives note on events.
		"callback" should take these arguments:
			channel				0 - 15
			pitch				0 - 127
			velocity			0 - 127
			last_frame_time		Millis since jack server start
			offset				Millis of MIDI event counting from last_frame_time
		i.e.:
			def note_off(channel, pitch, velocity, *_):
				pass

		Note:
		The callback function is called from the thread that the Jack Client is running
		in, and that it is not permitted to modify the Jack Client or any of its
		settings in this thread.
		"""
		if not callable(callback):
			raise Exception("Invalid callback")
		self.__note_off_callback = callback

	def on_poly_pressure(self, callback):
		"""
		Sets the high-level MIDI event callback which receives note on events.
		"callback" should take these arguments:
			channel				0 - 15
			pitch				0 - 127
			pressure			0 - 127
			last_frame_time		Millis since jack server start
			offset				Millis of MIDI event counting from last_frame_time
		i.e.:
			def poly_pressure(channel, pitch, pressure, *_):
				pass

		Note:
		The callback function is called from the thread that the Jack Client is running
		in, and that it is not permitted to modify the Jack Client or any of its
		settings in this thread.
		"""
		if not callable(callback):
			raise Exception("Invalid callback")
		self.__poly_pressure_callback = callback

	def on_control_change(self, callback):
		"""
		Sets the high-level MIDI event callback which receives control change events.
		"callback" should take these arguments:
			channel				0 - 15
			controller			0 - 127
			value				0 - 127
			last_frame_time		Millis since jack server start
			offset				Millis of MIDI event counting from last_frame_time
		i.e.:
			def control_change(channel, controller, value, *_):
				pass

		Note:
		The callback function is called from the thread that the Jack Client is running
		in, and that it is not permitted to modify the Jack Client or any of its
		settings in this thread.
		"""
		if not callable(callback):
			raise Exception("Invalid callback")
		self.__control_change_callback = callback

	def on_program_select(self, callback):
		"""
		Sets the high-level MIDI event callback which receives program select events.
		"callback" should take these arguments:
			channel				0 - 15
			program				0 - 127
			last_frame_time		Millis since jack server start
			offset				Millis of MIDI event counting from last_frame_time
		i.e.:
			def program_select(channel, program, *_):
				pass

		Note:
		The callback function is called from the thread that the Jack Client is running
		in, and that it is not permitted to modify the Jack Client or any of its
		settings in this thread.
		"""
		if not callable(callback):
			raise Exception("Invalid callback")
		self.__program_select_callback = callback

	def on_pressure(self, callback):
		"""
		Sets the high-level MIDI event callback which receives pressure events.
		"callback" should take these arguments:
			channel				0 - 15
			pressure			0 - 127
			last_frame_time		Millis since jack server start
			offset				Millis of MIDI event counting from last_frame_time
		i.e.:
			def pressure(channel, pressure, *_):
				pass

		Note:
		The callback function is called from the thread that the Jack Client is running
		in, and that it is not permitted to modify the Jack Client or any of its
		settings in this thread.
		"""
		if not callable(callback):
			raise Exception("Invalid callback")
		self.__pressure_callback = callback

	def on_pitch_bend(self, callback):
		"""
		Sets the high-level MIDI event callback which receives pitch bend events.
		"callback" should take these arguments:
			channel				0 - 15
			value				0 - 32768
			last_frame_time		Millis since jack server start
			offset				Millis of MIDI event counting from last_frame_time
		i.e.:
			def pitch_bend(channel, value, *_):
				pass

		Note:
		The callback function is called from the thread that the Jack Client is running
		in, and that it is not permitted to modify the Jack Client or any of its
		settings in this thread.
		"""
		if not callable(callback):
			raise Exception("Invalid callback")
		self.__pitch_bend_callback = callback

	def __null_callback(self, *_):
		pass

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

	def close(self):
		self.__client.deactivate()
		self.__client.close()


#  end jack_midi_keyboard/__init__.py
