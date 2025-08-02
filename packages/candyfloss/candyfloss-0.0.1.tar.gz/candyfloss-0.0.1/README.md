
# Candyfloss

Candyfloss is an ergonomic interface to GStreamer. It allows users to build and run pipelines to decode and encode video files, extract video frames to use from python code, map python code over video frames, etc. 

## Installation

Candyfloss is installable by running setup.py in the normal way. It should also be available on PyPI soon.

Candyfloss requires that gstreamer is installed. Most desktop linux distros have it installed already. If you aren't on linux or don't have it installed check the GStreamer install docs [here](https://gstreamer.freedesktop.org/documentation/installing/index.html?gi-language=c). In addition to the installation methods mentioned there if you're on macos you can install it with homebrew by running `brew install gstreamer`. 

## Examples

```python

# scale a video file to 300x300

from candyfloss import Pipeline
from candyfloss.utils import decode_file

with Pipeline() as p:

    inp_file = p >> decode_file('input.mp4')
    scaled_video = inp_file >> 'videoconvert' >> 'videoscale' >> ('video/x-raw', {'width':300,'height':300})

    mux = p >> 'mp4mux'
    scaled_video >> 'x264enc' >> mux
    inp_file >> 'avenc_aac' >> mux
    mux >> ['filesink', {'location':'output.mp4'}]

```


```python

# iterate over frames from a video file

from candyfloss import Pipeline

for frame in Pipeline(lambda p: p >> decode_file('input.webm')):
    frame.save('frame.jpeg') # frame is a PIL image

```

```python

# display your webcam with the classic emboss effect applied

from candyfloss import Pipeline
from PIL import ImageFilter

with Pipeline() as p:
    p >> 'autovideosrc' >> p.map(lambda frame: frame.filter(ImageFilter.EMBOSS)) >> 'autovideosink'

```

```python

# display random noise frames in a window

from candyfloss import Pipeline
from candyfloss.utils import display_video
from PIL import Image
import numpy as np

def random_frames():
    rgb_shape = (300, 300, 3)
    while 1:
        mat = np.random.randint(0, 256, dtype=np.uint8, size=rgb_shape)
        yield Image.fromarray(mat)

with Pipeline() as p:
    p.from_iter(random_frames(), (300, 300)) >> display_video()

```
