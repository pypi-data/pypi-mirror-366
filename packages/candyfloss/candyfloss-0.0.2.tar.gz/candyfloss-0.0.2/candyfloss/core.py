import c_candyfloss as cc

class PipelineError(Exception):

    def __init__(self, *messages):
        self.message = ' @ '.join(messages)
        self.stack_info = None

    def add_stack_info(self, v):
        self.stack_info = '\n'.join(traceback.StackSummary(v).format())

    def __str__(self):
        info = self.stack_info or ''
        return '%s %s' % (info, self.message)

    def __repr__(self):
        return 'PipelineError: %s' % str(self)

cc.set_exception_class(PipelineError)

import os
import threading
import queue
from inspect import signature
import traceback
import time

from PIL import Image

def parse_dict(inp):
    res = []
    for k, v in inp.items():
        if type(v) == str:
            v = v.encode('utf-8')
        res.append((str(k), v))
    return res


class IteratorSourceWrapper:

    def __init__(self, pipeline, inp_iter, outp_shape, framerate=30):
        self.outp_shape = outp_shape
        self.inp_iter = inp_iter
        self.pipeline = pipeline
        self.nanos_per_frame = int(1000000000 / framerate)

    def __iter__(self):
        try:
            for frame_i, img in enumerate(self.inp_iter):
                if img.width != self.outp_shape[0] or img.height != self.outp_shape[1]:
                    img = img.resize(self.outp_shape)
                if img.format != 'RGB':
                    img = img.convert('RGB')
                yield (
                    img.tobytes(), 
                    int(self.nanos_per_frame * frame_i),
                    self.nanos_per_frame,
                    frame_i)
        except Exception as e:
            self.pipeline.exc = e

class UserCallback:
    
    def __init__(self, pipeline, f):
        self.n_args = len(signature(f).parameters)
        if self.n_args not in (1, 2):
            raise ValueError('invalid callback signature')
        self.f = f
        self.pipeline = pipeline

    def __call__(self, data, inp_shape, outp_shape):
        try:
            img = Image.frombytes('RGB', inp_shape, data)
            if self.n_args == 1:
                res = self.f(img)
            elif self.n_args == 2:
                res = self.f(img, outp_shape)

            if res.width != outp_shape[0] or res.height != outp_shape[1]:
                res = res.resize(outp_shape)

            return res.tobytes()
        except Exception as e:
            self.pipeline.exc = e


def util_fn(f):
    def _res(*args, **kwargs):
        def _r2(pipeline):
            root = PipelineEl(pipeline, None)
            return f(root, *args, **kwargs)
        return _r2
    _res.__name__ = f.__name__
    return _res

class PipelineEl:

    def __init__(self, pipeline, arg):
        self.pipeline = pipeline

        if arg is None:
            self.obj = None
        elif type(arg) == tuple:
            self.obj = cc.make_capsfilter(pipeline.pipeline, arg[0], parse_dict(arg[1]))
        elif type(arg) == str:
            self.obj, name = cc.construct_element(pipeline.pipeline, arg, [])
            self.pipeline.stacks[name] = traceback.extract_stack()
        elif type(arg) == list:
            self.obj, name = cc.construct_element(pipeline.pipeline, arg[0], parse_dict(arg[1]))
            self.pipeline.stacks[name] = traceback.extract_stack()
        else:
            raise TypeError('invalid argument type: %r' % type(arg))

    def link(self, other):
        if self.obj is not None:
            cc.link_elements(self.obj, other.obj)

    @classmethod
    def to_el(cls, upstream, pipeline, v, rec=False):
        if isinstance(v, cls):
            return v
        else:
            try:
                return cls(pipeline, v)
            except TypeError as e:
                if callable(v):
                    return v(pipeline)
                else:
                    raise e
                
    def __rshift__(self, other):
        other = self.to_el(self, self.pipeline, other)
        self.link(other)
        return other

    def from_iter(self, inp, outp_shape, framerate=30, **kwargs):
        res = PipelineEl(self.pipeline, None)
        kwargs['width'] = outp_shape[0]
        kwargs['height'] = outp_shape[1]
        res.obj = cc.make_iterator_source(
            self.pipeline.pipeline, 
            IteratorSourceWrapper(self.pipeline, inp, outp_shape, framerate=framerate),
            list(kwargs.items()))
        return res

    def map(self, f):
        res = PipelineEl(self.pipeline, None)
        res.obj = cc.make_callback_transform(self.pipeline.pipeline, UserCallback(self.pipeline, f))
        return res


class CallbackSink:

    def __init__(self, pipeline, end_el):
        self.pipeline = pipeline
        self.el = cc.make_callback_sink(pipeline.pipeline)
        end_el = end_el >> 'videoconvert'
        cc.link_elements(end_el.obj, self.el)

    def __iter__(self):
        while 1:
            v = cc.appsink_pull_buffer(self.el, 10000000) # 100ms (in nanos)
            if v is False:
                if self.pipeline.is_done:
                    if self.pipeline.exc is not None:
                        raise self.pipeline.exc
                    break
                else:
                    continue
            if v is None:
                break
            buf, w, h = v
            yield Image.frombytes('RGB', (w, h), buf)

import webbrowser, socketserver
def browser_open(data, mime=None):
    class Handler(socketserver.BaseRequestHandler):

        def handle(self):
            self.request.send(b'HTTP/1.1 200 OK\r\n')
            if mime is not None:
                self.request.send(b'Content-Type: %s\r\n' % mime.encode('utf-8'))
            self.request.send(b'\r\n')
            self.request.send(data)

    with socketserver.TCPServer(('127.0.0.1', 0), Handler) as server:
        webbrowser.open('http://127.0.0.1:%d/' % server.server_address[1])
        server.handle_request()

class Pipeline:

    def __init__(self, gen_fn=None, name=None, debug_viz=False):
        if name is None:
            name = str(hash(self))
        self.stacks = {}
        self.error_stack = None
        self.exc = None
        self.run_lock = threading.Lock()
        self.run_lock.acquire(blocking=False)
        self.pipeline = cc.make_pipeline(name, self._on_done)
        self.is_done = False
        self.gen_el = None
        self.debug_viz = debug_viz

        if gen_fn is not None:
            self.gen_el = gen_fn(PipelineEl(self, None))

    def _on_done(self, exc, el_names):
        if not self.is_done:
            if el_names is not None:
                for name in reversed(el_names):
                    try:
                        self.error_stack = self.stacks[name]
                        break
                    except KeyError:
                        pass
            if self.exc is None:
                self.exc = exc
            self.is_done = True
            self.run_lock.release()

    def run_async(self):
        if self.is_done:
            return
        if self.debug_viz:
            import graphviz
            debug_dot = cc.dot_viz(self.pipeline)
            svg = graphviz.pipe('dot', 'svg', debug_dot)
            browser_open(svg, 'image/svg+xml')
        cc.run_pipeline(self.pipeline)

    def run(self):
        self.run_async()
        self.run_lock.acquire()
        self.run_lock.release()
        self._post_run()

    def _post_run(self):
        if self.exc is not None:
            if self.error_stack is not None:
                try:
                    self.exc.add_stack_info(self.error_stack)
                except AttributeError:
                    pass
            raise self.exc

    def __enter__(self):
        return PipelineEl(self, None)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            raise exc_val

        self.run()

    def __iter__(self):
        if self.gen_el is None:
            return []

        res = CallbackSink(self, self.gen_el)
        self.run_async()
        for frame in res:
            yield frame
        self._post_run()
