
## Usage

### Synthesize a Word

```python
import mbrola

# Create an MBROLA object
caffe = MBROLA(
    word="caffè",
    phon=["k", "a", "f", "f", "E1"],
    durations=100,  # or [100, 120, 100, 110]
    pitch=[100, [200, 50, 200], 100, 100, 200],
)

# Display phoneme sequence
print(caffe)

# Export PHO file
caffe.export_pho("caffe.pho")

# Synthesize and save audio (WAV file)
caffe.make_sound("caffe.wav", voice="it4")
```

The module uses the MBROLA command line tool under the hood. Ensure MBROLA is installed and available in your system path, or WSL if on Windows.

## Specifying the pitch contour

**pymbrola** implements the piecewise linear pitch specification as different inputs:

If pitch is specified as an **integer**, pitch is assumed constant across phonemes:

```python
phon = list("kasa")
pitch = 200
validate_pitch(200, phon)
# [[(0, 200)], [(0, 200)], [(0, 200)], [(0, 200)]]
```

If pitch is specified as a **list**, each element in mapped to each phoneme. Integers in the list are treated as before (constant pitch for the whole phoneme):

```python
phon = list("kasa")
pitch = [200, 50, 50, 100]
validate_pitch(pitch, phon)
# [[(0, 200)], [(0, 50)], [(0, 50)], [(0, 100)]]
```

Empty lists inside the main list are treated as constant pitch sections:

```python
phon = list("kasa")
pitch = [[], 50, [], 100]
validate_pitch(pitch, phon)
# [[], [(0, 50)], [], [(0, 100)]]
```

Non-empty lists must consist in lists of tuples. Each tuple contains two values. The first value is the time (as a percentage of the duration of the phoneme) at which the pitch should be modified inside the phoneme (as a float or integer), and the second value is the pitch that should be set at that time (as an integer):

```python
phon = list("kasa")
pitch = [[], [(25, 50), (50, 100), (75, 150), (90, 200)], [], 100]
validate_pitch(pitch, phon)
# [[], [(25, 50), (50, 100), (75, 150), (90, 200)], [], [(0, 100)]]
```