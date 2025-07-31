

Example how to use



from python_zatobox.vanubus import Vanubus


host = "192.168.68.102"  # Replace with the actual IP address of the device
client = Vanubus(host)

test = client.discover()

sensordata  = client.getdata([1,2,6])


