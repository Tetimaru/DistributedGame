import socket
import selectors
import json
import struct

class Message:
    def __init__(self, sel, sock, addr, request):
        self.sel = sel
        self.sock = sock 
        self.addr = addr
        self._send_buffer = b''
        self._recv_buffer = b''
        self._request_queued = False
        self.request = request
        self.server_response = None

    def queue_request(self):
        message = self._json_encode(self.request)
        self._send_buffer += message
        self._request_queued = True
        
    # serialize data (python dict) into bytes
    def _json_encode(self, data):
        return json.dumps(data).encode('utf-8')

    # deserialize bytes into python dict
    def _json_decode(self, data):
        return json.loads(data)
        
    def process_response(self):
        if not self._recv_buffer:
            return
            
        self.server_response = self._json_decode(self._recv_buffer) # dict form
        print('received', repr(self.server_response), 'from', self.addr)

        if self.server_response["function"] == "lock":
            print("Yay!")
            # lock(x, y....)

        self._recv_buffer = b''
        
    def process_events(self, mask):
        # needs to return a bool indicating if this message class is done, eg. make a new one
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

        if self.server_response:
            return self.server_response
    
    # helper function to read data from the socket into _recv_buffer
    def _read(self):
        try:
            data = self.sock.recv(4096) # up to 4096 bytes
            #print(repr(data))
        except BlockingIOError: # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Server closed connection.") 

    def read(self):
        self._read()
        self.process_response()

    # helper function to send the data in _send_buffer through the socket
    def _write(self):
        if self._send_buffer:
            print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
        
    def write(self):
        if not self._request_queued:
            self.queue_request()
            
        self._write()