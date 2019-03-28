import socket
import selectors
import json
import struct

class Message:
    def __init__(self, sel, sock, addr, req):
        self.sel = sel
        self.sock = sock 
        self.addr = addr
        self._send_buffer = b''
        self._recv_buffer = b''
        self._request_queued = False
        self.request = req
        self._jsonheader_len = 0
        self.jsonheader = None
        
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
        
    def _json_encode(self, obj):
        return json.dumps(obj).encode('utf-8')
        
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
        
        if self._request_queued:
            if not self._send_buffer: # done writing
                pass
                # Set selector to listen for read events
                #self._set_selector_events_mask('r')