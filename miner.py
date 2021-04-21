#!/usr/bin/env python3
# Minimal version of Duino-Coin PC Miner. Created by revox 2020-2021, adapted for openwrt by BastelPichi
import hashlib
import os
import socket
import sys  # Only python3 included libraries
import time
import urllib.request


soc = socket.socket()
soc.settimeout(10)

username = "ttuanphong"  # Edit this to your username, mind the quotes
UseLowerDiff = True  # Set it to True to mine with lower difficulty

while True:
    try:
        # This sections grabs pool adress and port from Duino-Coin GitHub file
        # Serverip file URL
        serverip = ("https://raw.githubusercontent.com/"
                    + "revoxhere/"
                    + "duino-coin/gh-pages/"
                    + "serverip.txt")

        with urllib.request.urlopen(serverip) as content:
            # Read content and split into lines
            content = content.read().decode().splitlines()

        # Line 1 = IP
        pool_address = content[0]
        # Line 2 = port
        pool_port = content[1]

        # This section connects and logs user to the server
        soc.connect((str(pool_address), int(pool_port)))
        server_version = soc.recv(3).decode()  # Get server version
        print("Server is on version", server_version)

        # Mining section
        while True:
            if UseLowerDiff:
                # Send job request for lower diff
                soc.send(bytes(
                    "JOB,"
                    + str(username)
                    + ",LOW",
                    encoding="utf8"))
            else:
                # Send job request
                soc.send(bytes(
                    "JOB,"
                    + str(username),
                    encoding="utf8"))

            # Receive work
            job = soc.recv(1024).decode().rstrip("\n")
            # Split received data to job and difficulty
            job = job.split(",")
            difficulty = job[2]
            
            hashingStartTime = time.time()
            base_hash = hashlib.sha1(str(job[0]).encode('ascii'))
            temp_hash = None
            
            for result in range(100 * int(difficulty) + 1):
                # Calculate hash with difficulty
                temp_hash =  base_hash.copy()
                temp_hash.update(str(result).encode('ascii'))
                ducos1 = temp_hash.hexdigest()

                # If hash is even with expected hash result
                if job[1] == ducos1:
                    hashingStopTime = time.time()
                    timeDifference = hashingStopTime - hashingStartTime
                    hashrate = result / timeDifference

                    # Send numeric result to the server
                    soc.send(bytes(
                        str(result)
                        + ","
                        + str(hashrate)
                        + ",Minimal_PC_Miner",
                        encoding="utf8"))

                    # Get feedback about the result
                    feedback = soc.recv(1024).decode().rstrip("\n")
                    # If result was good
                    if feedback == "GOOD":
                        file = open('/sys/class/leds/fritz4040:amber:wlan/brightness','w')# replace that with the led no. 1 name
                        file.write('1')
                        file.close()
                        time.sleep(0.3)
                        file = open('/sys/class/leds/fritz4040:amber:wlan/brightness','w')# replace that with the led no. 1 name
                        file.write('0')
                        file.close()
                        print("Accepted share",
                              result,
                              "Hashrate",
                              int(hashrate/1000),
                              "kH/s",
                              "Difficulty",
                              difficulty)
                        break
                    # If result was incorrect
                    elif feedback == "BAD":
                        file = open('/sys/class/leds/fritz4040:red:wlan/brightness','w')# replace that with the led no. 2 name
                        file.write('1')
                        file.close()
                        time.sleep(0.3)
                        file = open('/sys/class/leds/fritz4040:red:wlan/brightness','w')# replace that with the led no. 2 name
                        file.write('0')
                        file.close()
                        print("Rejected share",
                              result,
                              "Hashrate",
                              int(hashrate/1000),
                              "kH/s",
                              "Difficulty",
                              difficulty)
                        break

    except Exception as e:
        print("Error occured: " + str(e) + ", restarting in 5s.")
        time.sleep(5)
        os.execl(sys.executable, sys.executable, *sys.argv)
