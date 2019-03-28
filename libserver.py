import socket
import selectors
import struct

class Message:
    def __init__(self, sel, conn, addr): # constructor
        self.sel = sel 
        self.sock = conn 
        self.addr = addr
        self._recv_buffer = b''
        self._send_buffer = b''
        self._jsonheader_len = 0
        self.jsonheader = None
        self.request = None
        self.response_created = False
    
    # fixed-length header
    # 2-byte integer containing length of JSON header
    def process_protoheader(self):
        hdrlen = 2 
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack('>H', self._recv_buffer[:hdrlen])[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]
            
    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) > hdrlen:
            #self.jsonheader = self._json_decode(self._recv_buffer[hdrlen], 'utf-8')
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in ('byteorder', 'content-length', 'content-type', 'content-encoding'):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')
                    
    def process_request(self):
        content_len = self.jsonheader['content-length']
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader['content-type'] == 'text/json':
            encoding = self.jsonheader['content-encoding']
            #self.request = self._json_decode(data, encoding)
            print('received request', repr(self.request), 'from', self.addr)
        else:
            # Binary or unknown content-type
            self.request = data
            print(f'received {self.jsonheader["content-type"]} request from', self.addr)
        # we're done reading 
        #self._set_selector_events_mask('w')
    
    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
            print(repr(data))
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")
        
    def read(self):
        self._read()
        
        if self._jsonheader_len is None:
            self.process_protoheader()
        else:
            if self.jsonheader is None:
                self.process_jsonheader()
                
        if self.jsonheader:
            if self.request is None:
                self.process_request()
    
    def _write(self):
        if self._send_buffer:
            print('sending', repr(self._send_buffer), 'to', self.addr)
            try:
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable
                pass 
            else:
                self._send_buffer = self._send_buffer[sent:]
                # close when buffer has drained
                if sent and not self._send_buffer:
                    self.close()
    
    # def create_response(self):
        # if self.jsonheader['content-type'] == 'text/json':
            # response = self._create_response_json_content()
        # else:
            # response = self._create_response_binary_content()
        # message = self._create_message(**response)
        # self.response_created = True
        # self._send_buffer += message
        
    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()
                
        self._write()
        
    def close(self):
        print('closing connection to', self.addr)
        self.sel.unregister(self.sock)
        self.sock.close()