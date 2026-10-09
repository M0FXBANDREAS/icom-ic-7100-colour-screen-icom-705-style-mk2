#!/usr/bin/env python3
"""Local IC-7100 receive control panel. No transmit commands implemented."""
import argparse
import json
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

MODES = {'LSB': 0, 'USB': 1, 'AM': 2, 'CW': 3, 'RTTY': 4, 'FM': 5, 'CW-R': 7, 'RTTY-R': 8, 'DV': 0x17}

def encode_frequency(hz):
    hz = int(hz)
    if not (30000 <= hz <= 199999999 or 400000000 <= hz <= 470000000):
        raise ValueError('Frequency outside IC-7100 receive ranges')
    return bytes(int(f'{hz:010d}'[i:i+2], 16) for i in range(8, -1, -2))

def decode_frequency(data):
    if len(data) != 5 or any(b >> 4 > 9 or b & 15 > 9 for b in data):
        raise ValueError('Invalid frequency BCD')
    return int(''.join(f'{b:02x}' for b in reversed(data)))

class Radio:
    def __init__(self, args):
        self.lock = threading.Lock()
        self.port = None
        self.address = args.address
        self.state = dict(frequency=None, mode='UNKNOWN', filter=None, connected=False, source='NO AUDIO INPUT', bins=[], error='', audio_error='')
        if args.port:
            try:
                import serial
                self.port = serial.Serial(args.port, args.baud, timeout=.08)
                self.refresh()
            except Exception as exc:
                self.state['error'] = str(exc)
        if args.audio_device is not None:
            try:
                import numpy as np
                import sounddevice as sd
                device = args.audio_device
                if device == 'auto':
                    inputs = [(i, d) for i, d in enumerate(sd.query_devices()) if d['max_input_channels'] > 0]
                    matches = [(i,d) for i,d in inputs if any(x in d['name'].lower() for x in ('icom', 'ic-7100', 'usb audio codec', 'usb audio'))]
                    if len(matches) != 1:
                        raise ValueError('Select the Icom input using --audio-device INDEX; automatic matching was ambiguous or unavailable.')
                    device = matches[0][0]
                else:
                    device = int(device)
                def callback(data, frames, timing, status):
                    spectrum = np.abs(np.fft.rfft(data[:, 0] * np.hanning(frames))) / (frames / 2)
                    db = 20 * np.log10(np.maximum(spectrum, 1e-8))
                    selected = db[:int(3000 * frames / 48000) + 1]
                    with self.lock:
                        self.state['bins'] = np.interp(np.linspace(0, len(selected)-1, 512), np.arange(len(selected)), selected).tolist()
                        self.state['source'] = 'LIVE AF · 0–3 kHz'
                        self.state['audio_error'] = str(status) if status else ''
                self.stream = sd.InputStream(device=device, channels=1, samplerate=48000, blocksize=4096, callback=callback)
                self.stream.start()
            except Exception as exc:
                self.state['audio_error'] = str(exc)

    def exchange(self, command, payload=b'', response_command=None):
        self.port.reset_input_buffer()
        self.port.write(bytes([0xfe, 0xfe, self.address, 0xe0, command]) + payload + b'\xfd')
        deadline = time.monotonic() + 1.2
        buffer = bytearray()
        while time.monotonic() < deadline:
            buffer.extend(self.port.read(64))
            while 0xfd in buffer:
                end = buffer.index(0xfd)
                frame = bytes(buffer[:end+1]); del buffer[:end+1]
                start = frame.find(b'\xfe\xfe')
                frame = frame[start:] if start >= 0 else b''
                if len(frame) < 6 or frame[2:4] != bytes([0xe0, self.address]):
                    continue
                if frame[4] == 0xfa:
                    raise ValueError('Radio rejected command')
                if frame[4] == (response_command if response_command is not None else 0xfb):
                    return frame[5:-1]
        raise TimeoutError('No CI-V reply. Check port, baud, address and radio power.')

    def refresh(self):
        with self.lock:
            try:
                self.state['frequency'] = decode_frequency(self.exchange(3, response_command=3))
                mode = self.exchange(4, response_command=4)
                self.state['mode'] = next((k for k,v in MODES.items() if mode and v == mode[0]), 'UNKNOWN')
                self.state['filter'] = mode[1] if len(mode) > 1 and mode[1] in (1, 2, 3) else None
                self.state.update(connected=True, error='')
            except Exception as exc:
                self.state.update(connected=False, error=str(exc))

    def set(self, changes):
        allowed = {'frequency', 'mode', 'filter', 'tune_steps', 'step_hz'}
        if set(changes) - allowed or not changes:
            raise ValueError('Unsupported receive control')
        if 'frequency' in changes:
            encoded = encode_frequency(changes['frequency'])
        if 'mode' in changes and changes['mode'] not in MODES:
            raise ValueError('Unsupported mode')
        if 'filter' in changes and (type(changes['filter']) is not int or changes['filter'] not in (1,2,3)):
            raise ValueError('Filter must be FIL1, FIL2 or FIL3')
        relative = 'tune_steps' in changes or 'step_hz' in changes
        if relative:
            if set(changes) != {'tune_steps','step_hz'}:
                raise ValueError('Relative tuning requires only tune_steps and step_hz')
            if type(changes['tune_steps']) is not int or abs(changes['tune_steps']) > 1000:
                raise ValueError('Invalid tuning movement')
            if changes['step_hz'] not in (1,10,100,1000,10000):
                raise ValueError('Invalid tuning step')
        with self.lock:
            if not self.port:
                raise ValueError('IC-7100 USB connection unavailable')
            if relative:
                current = decode_frequency(self.exchange(3, response_command=3))
                self.exchange(5, encode_frequency(current + changes['tune_steps'] * changes['step_hz']))
            if 'frequency' in changes:
                self.exchange(5, encoded)
            if 'mode' in changes or 'filter' in changes:
                # Query mode first so a filter-only change preserves the radio mode.
                current_mode = self.exchange(4, response_command=4)
                if not current_mode:
                    raise ValueError('Missing radio mode response')
                mode_code = MODES[changes['mode']] if 'mode' in changes else current_mode[0]
                payload = bytes([mode_code])
                if 'filter' in changes:
                    payload += bytes([changes['filter']])
                self.exchange(6, payload)
        self.refresh()

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent / 'web'), **kwargs)
    def respond(self, status, value):
        data = json.dumps(value).encode()
        self.send_response(status); self.send_header('Content-Type','application/json')
        self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(data)))
        self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if urlsplit(self.path).path == '/api/state':
            if self.server.radio.port: self.server.radio.refresh()
            with self.server.radio.lock: state = dict(self.server.radio.state)
            return self.respond(200, state)
        super().do_GET()
    def do_POST(self):
        if self.path != '/api/control': return self.respond(404, {'error':'Not found'})
        # Local browser origin only; reject cross-site control requests.
        origin = self.headers.get('Origin')
        if origin and origin != 'http://' + self.headers.get('Host',''):
            return self.respond(403, {'error':'Origin rejected'})
        if self.headers.get('Content-Type','').split(';')[0] != 'application/json':
            return self.respond(415, {'error':'JSON required'})
        try:
            length = int(self.headers.get('Content-Length',0))
            if not 0 < length < 1024: raise ValueError('Invalid request size')
            value = json.loads(self.rfile.read(length))
            if not isinstance(value, dict): raise ValueError('Object required')
            self.server.radio.set(value)
            return self.respond(200, self.server.radio.state)
        except Exception as exc:
            return self.respond(400, {'error':str(exc)})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default='/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_IC-7100_03006987_A-if00-port0', help='CI-V device, preferably /dev/serial/by-id/...')
    parser.add_argument('--baud', type=int, default=19200)
    parser.add_argument('--address', type=lambda s:int(s,16), default=0x88)
    parser.add_argument('--audio-device', default='auto', help='Icom audio input index or auto')
    parser.add_argument('--http-port', type=int, default=7100)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.http_port), Handler)
    server.radio = Radio(args)
    print(f'Open http://127.0.0.1:{args.http_port} — IC-7100 live USB control')
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally:
        server.server_close()
        if server.radio.port: server.radio.port.close()
        if hasattr(server.radio,'stream'): server.radio.stream.close()

if __name__ == '__main__': main()
