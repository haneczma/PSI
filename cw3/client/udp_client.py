# simple Python socket client
# (c) G.Blinowski for PSI 2021

import socket
import sys
import io

HOST = '127.0.0.1'  # The server's hostname or IP address
size = 1
binary_stream = io.BytesIO()

if  len(sys.argv) < 2: 
  print("no port, using 8000")
  port=8000
else:
  port = int( sys.argv[1] )

print("Will send to ", HOST, ":", port)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
  while True:
#    buffer = str( size )
    binary_stream.write("Hello, world!\n".encode('ascii'))
    binary_stream.seek(0)
    stream_data = binary_stream.read()
    # print( "Sending buffer size= ", size, "data= ", stream_data  )
    print( "Sending buffer size= ", size  )

    s.sendto( stream_data, (HOST, port)    )
    data = s.recv( size )
    # print('Received', repr(data))
    size = size * 2


print('Client finished.')

