from .core import util_fn
import os

@util_fn
def decode_file(p, fname):
    return p >> ['filesrc', {'location':os.path.abspath(fname)}] >> 'decodebin'

@util_fn
def decode_uri(p, uri):
    return p >> ['uridecodebin', {'uri':uri}]

@util_fn
def display_video(p):
    res = p >> 'videoconvert'
    res >> 'autovideosink'
    return res

@util_fn
def scale_video(p, w, h):
    return p >> 'videoscale' >> ('video/x-raw', {'width':w, 'height':h})

@util_fn
def play_audio(p):
    res = p >> 'audioconvert'
    res >> 'autoaudiosink'
    return res

FRAG_SHADER_TEMPLATE = '''
 #version 100
 #ifdef GL_ES
 precision mediump float;
 #endif
 varying vec2 v_texcoord;
 uniform sampler2D tex;
 uniform float time;
 uniform float width;
 uniform float height;

 void main () {
   gl_FragColor = %s
 }
'''

@util_fn
def gl_shader(p, shader_expr):
    shader_code = FRAG_SHADER_TEMPLATE % shader_expr
    return p >> 'glupload' >> ['glshader', {'fragment':shader_code}]
