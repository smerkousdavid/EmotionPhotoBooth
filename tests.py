import json
import cups
import time
from printer import Printer

'''
config = json.load(open("config/objectoriented.json", 'r'))

print(config)

for key, topic in config['topics'].items():
    print("KEY: %s" % key)
    print("TOPIC: %s\n" % str(topic))


conn = cups.Connection()
printers = conn.getPrinters()

for printer in printers:
    print("%s %s" % (str(printer), printers[printer]['device-uri']))

printer = conn.getDefault()
conn.printFile(printer, 'logo.png', '/home/smerkous/Pictures/Profile/final_log_trns.png', {})

while True:
    print(str(conn.getJobs()))
    time.sleep(1)
'''

def completed(status):
    print("Completed print job status: %s" % str(status))

if __name__ == "__main__":
    printer = Printer(None)
    printer.setDefaultPrinter()
    printer.printImage('/home/smerkous/Pictures/Profile/final_log_trns.png', 'Pseudonymous Logo', completed)
    while True:
        pass
