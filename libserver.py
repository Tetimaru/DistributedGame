import socket
import selectors
import struct
import json
import random

class MessageOut:
    def __init__(self, sel, conn, addr, request): # constructor
        self.sel = sel 
        self.sock = conn 
        self.addr = addr
        self._send_buffer = b''
        self.outgoing_request = request
        self.response_created = False
         
    # serialize data (python dict) into bytes
    def _json_encode(self, data):
        return json.dumps(data).encode('utf-8')

    def create_response(self):
        message = self._json_encode(self.outgoing_request)
        self.response_created = True
        self._send_buffer += message
        # send messages to all the other clients
        
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
        
    def write(self):
        if not self.response_created:
            self.create_response()
                
        self._write()


class MessageIn:
    def __init__(self, sel, conn, addr): # constructor
        self.sel = sel 
        self.sock = conn 
        self.addr = addr
        self._recv_buffer = b''
        self.client_request = None
    
    def color(self, player, x, y, fill):
        pass
        
    # player, x, y: int 
    # lock grid(x,y) for player
    def lock(self, player, x, y):
        print("locking grid(", x, y, ") for player", player)

    # deserialize bytes into python dict
    def _json_decode(self, data):
        return json.loads(data.decode('utf-8'))
                        
    def process_read_buffer(self):
        if not self._recv_buffer:
            return
           
        self.client_request = self._json_decode(self._recv_buffer) # dict form
        print('SERVER####### received', repr(self.client_request), 'from', self.addr)


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
                # client socket closed connection for some reason 
                self.close()
    
    # entry point when data is available to be read on socket
    def read(self):
        self._read()
        self.process_read_buffer()

        if self.client_request:
        	return self.client_request

    def close(self):
        print('closing connection to', self.addr)
        self.sel.unregister(self.sock)
        self.sock.close()
    

