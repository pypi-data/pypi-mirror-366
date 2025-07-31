# midi_notes

Provides various tables (dicts) and functions for converting between note
names, midi note numbers, frequencies, plus a single "Note" class which allows
you to switch seamlessly between pitch/note name/frequency representations.

## Note class

You can construct a Note with either a (str) note name, (int) midi pitch, or
(float) frequency.

	from midi_notes import *

	note = Note('C4')
	print(f'"{note.name}" has midi pitch {note.pitch}')
	print(f'"{note.name}" is in octave {note.octave}, and has a value of {note.interval_above_c}')
	print(f'"{note.name}" has a frequency of {note.frequency}Hz')

	frequency = 444.4
	note = Note(frequency)
	print(f'"{note.name}" with a frequency of {note.frequency}Hz is closest to {frequency}Hz')

... prints:

	"C4" has MIDI pitch 60
	"C4" is in octave 4, and has a value of 0
	"C4" has a frequency of 261.626Hz
	"A4" with a frequency of 440.0Hz is closest to 444.4Hz

When getting the "name" property of a Note which is an incidental, you can
decide whether to retrieve the "sharp" or "flat" version of the note name
("D♯" is the same pitch as "E♭") by setting the "prefer_flats" property.

	note = Note('D#5')
	print(f'MIDI pitch {note.pitch} is "{note.name}"')
	note.prefer_flats = True
	print(f'MIDI pitch {note.pitch} is also "{note.name}"')

... prints:

	MIDI pitch 75 is "D#5"
	MIDI pitch 75 is also "Eb5"

You can also choose how to render incidentals:

	note = Note('D#5')
	note.incidentals_style = Note.INCIDENTAL_ASCII
	print(f'INCIDENTAL_ASCII: "{note.name}"')
	note.incidentals_style = Note.INCIDENTAL_UNICODE
	print(f'INCIDENTAL_UNICODE: "{note.name}"')
	note.incidentals_style = Note.INCIDENTAL_NAMES
	print(f'INCIDENTAL_NAMES: "{note.name}"')

... prints:

	INCIDENTAL_ASCII: "Eb5"
	INCIDENTAL_UNICODE: "E♭5"
	INCIDENTAL_NAMES: "E flat 5"

