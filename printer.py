import cups
import time
import threading

class Printer(object):
    def __init__(self, config):
        self._config = config
        self._conn = cups.Connection()
        self._printers = None
        self._printer = None

    def getPrinters(self):
        self._printers = self._conn.getPrinters()

        for printer in self._printers:
            print("Found printer NAME: %s URI: %s" % (printer, self._printers[printer]['device-uri']))
        
        return self._printers

    def setDefaultPrinter(self):
        if self._printers is None:
            self.getPrinters()
        
        self._printer = self._conn.getDefault()

    def _check_jobs(self, completed, timeout):
        printed = False
        
        print("Checking for jobs in a couple of seconds")

        time.sleep(3)

        for _ in range(0, timeout * 2):
            
            current_jobs = self._conn.getJobs()

            if not bool(current_jobs):
                print("The printer completed all jobs!")
                completed(True)
                printed = True
                break

            print("Printer is still printing, Jobs left: %d" % len(current_jobs.keys()))
            time.sleep(0.5)

        if not printed:
            print("Printer timeout out attempting to print the job")
            completed(False)

    def printImage(self, path_to_image, title, completed, timeout=30):
        self._conn.printFile(self._printer, path_to_image, title, {})
        
        print_jobs_thread = threading.Thread(target=self._check_jobs, args=(completed, timeout,))
        print_jobs_thread.setDaemon(True)
        print_jobs_thread.start()
