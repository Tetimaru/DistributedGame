import socket
import selectors
import json
import struct

class Message:
<<<<<<< HEAD
    def __init__(self, sel, sock, addr, req):
=======
    def __init__(self, sel, sock, addr):
>>>>>>> master
        self.sel = sel
        self.sock = sock 
        self.addr = addr
        self._send_buffer = b''
        self._recv_buffer = b''
        self._request_queued = False
<<<<<<< HEAD
        self.request = req
        self._jsonheader_len = 0
        self.jsonheader = None
        
=======
        self.request = None
        self._jsonheader_len = 0
        self.jsonheader = None
        self.server_response = None

        
    def add_new_request(self, request):
        self.request = request 

>>>>>>> master
    def queue_request(self):
        #content = self.request['content']
        #content_type = self.request['type']
        #content_encoding = self.request['encoding']
        # if content_type == 'text/json':
            # req = {
                # 'content_bytes': self._json_encode(content, content_encoding),
                # 'content_type': content_type,
                # 'content_encoding': content_encoding
            # }
        # else:
            # req = {
                # 'content_bytes': content,
                # 'content_type': content_type,
                # 'content_encoding': content_encoding 
            # }
        #message = self._create_message(**req)
        message = self._json_encode(self.request)
        self._send_buffer += message
        self._request_queued = True
        
<<<<<<< HEAD
    def _json_encode(self, obj):
        return json.dumps(obj).encode('utf-8')
=======
    # serialize data (python dict) into bytes
    def _json_encode(self, data):
        return json.dumps(data).encode('utf-8')

    # deserialize bytes into python dict
    def _json_decode(self, data):
        return json.loads(data)
>>>>>>> master
        
    # fixed-length header
    # 2-byte integer containing length of JSON header
    def process_protoheader(self):
        hdrlen = 2 
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack('>H', self._recv_buffer[:hdrlen])[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]
            
    #
    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) > hdrlen:
            self.jsonheader = self._json_decode(self._recv_buffer[hdrlen], 'utf-8')
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in ('byteorder', 'content-length', 'content-type', 'content-encoding'):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')
                    
    def process_response(self):
<<<<<<< HEAD
        content_len = self.jsonheader['content-length']
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader['content-type'] == 'text/json':
            encoding = self.jsonheader['content-encoding']
            self.request = self._json_decode(data, encoding)
            print('received request', repr(self.request), 'from', self.addr)
        else:
            # Binary or unknown content-type
            self.request = data
            print(f'received {self.jsonheader["content-type"]} request from', self.addr)
        # close when response has been processed
        self.close()
            
    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            pass
            #self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()
        
    def _write(self):
        # if there's data in the send buffer
        if self._send_buffer:
            print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                # Should be ready to write
=======
        if not self._recv_buffer:
            return
            
        self.server_response = self._json_decode(self._recv_buffer) # dict form
        print('received', repr(self.server_response), 'from', self.addr)

        if self.server_response["function"] == "lock":
            print("Yay!")

        self._recv_buffer = b''

        
    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()
    
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
                raise RuntimeError("Peer closed.") # ???

    def read(self):
        self._read()
        self.process_response()

    # helper function to send the data in _send_buffer through the socket
    def _write(self):
        if self._send_buffer:
            print("sending", repr(self._send_buffer), "to", self.addr)
            try:
>>>>>>> master
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
        
    def write(self):
        if not self._request_queued:
            self.queue_request()
            
<<<<<<< HEAD
        self._write()
        
        if self._request_queued:
            if not self._send_buffer: # done writing
                pass
                # Set selector to listen for read events
                #self._set_selector_events_mask('r')
=======
        self._write()
>>>>>>> master
