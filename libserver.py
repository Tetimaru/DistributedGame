import socket
import selectors
import struct
import json
import random

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
    
    def color(self, player, x, y, fill):
        pass
        
    # player, x, y: int 
    # lock grid(x,y) for player
    def lock(self, player, x, y):
        print("locking grid(", x, y, ") for player", player)
        
    def isLocked(self, x, y):
        print(x, y)
        return True if (random.random() > 0.5) else False
    
    # serialize data (python dict) into bytes
    def _json_encode(self, data):
        return json.dumps(data).encode('utf-8')

    # deserialize bytes into python dict
    def _json_decode(self, data):
        return json.loads(data)
                        
    def process_request(self):
        #content_len = self.jsonheader['content-length']
        #if not len(self._recv_buffer) >= content_len:
            #return
        if not self._recv_buffer:
            return
            
        self.request = self._json_decode(self._recv_buffer) # dict form
        print('received request', repr(self.request), 'from', self.addr)
        #print(locals()["self"])
        if self.request["function"] == "lock":
            #self.request_type = 
            isLocked = self.isLocked(self.request["args"]["x"], self.request["args"]["y"])
            if isLocked:
                pass # block
            else: # can continue
                # send response
                pass 
                #print(getattr(self, self.request["function"])(*self.request["arg_list"])) # call function
        
        self._recv_buffer = b''

        # we want to write a response, so monitor for write availability 
        self.sel.modify(self.sock, selectors.EVENT_WRITE, data=self)

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    # receive data from socket and store in _recv_buffer
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
    
    # entry point when data is available to be read on socket
    def read(self):
        self._read()
        
        #if self._jsonheader_len is None:
            #self.process_protoheader()
        #else:
            #if self.jsonheader is None:
                #self.process_jsonheader()
                
        #if self.jsonheader:
            #if self.request is None:
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
                # when buffer has drained, monitor for read events again
                if sent and not self._send_buffer:
                    self.sel.modify(self.sock, selectors.EVENT_READ, data=self)
    
    def create_response(self):
        if self.request["function"] == "lock":
            # check if the requested grid is already locked or coloured
            args = self.request["args"]
            isLocked = self.isLocked(args["x"], args["y"])
            if isLocked: # block
                response = {
                    "function": "lock",
                    "success": 0
                }
            else: # can lock, update board state
                self.lock(1, args["x"], args["y"])
                response = {
                    "function": "lock",
                    "success": 1
                }

        message = self._json_encode(response)
        self.response_created = True
        self._send_buffer += message
        
    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()
                
        self._write()
        
    def close(self):
        print('closing connection to', self.addr)
        self.sel.unregister(self.sock)
        self.sock.close()
