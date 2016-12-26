import ElectronicNose as EN
import signal
import sys
import time


def signal_handler(signal, frame):
        print "\nStopping..."

        nose.save("Data.npy")

        sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

print "Creating the ENose object"
nose = EN.ElectronicNose()

print "Starting data collection (CTRL+C to stop)"

while True:
    nose.sniff()
    time.sleep(0.02)



print 'The end, my friend.'
