import time

class Timer(object):
    """Class to time execution of code. 

    Keeps track of execution time and provides some utilities functions
    for showing time.

    """
    def __init__(self):
        """Sets the initial processing time to 0. """
        self.processing_time = 0.0
        self.start_time = None
        self.end_time = None
    def start(self):
        """Starts the timer. 
        
        Raises an L{OrderError} if the timer has not been stopped since the 
        previous start.

        """
        if self.end_time is not None:
            raise OrderError('attempting to start timer that is already '
                                'running.')
        self.start_time = time.time()
    def stop(self):
        """Stops the timer and increases processing time.
        
        Raises an L{OrderError} if the timer has not been started.

        """
        if self.start_time is None:
            raise OrderError('attempting to stop timer that has not been '
                                'started')
        self.end_time = time.time()
        self.processing_time += self.end_time - self.start_time
        self.start_time = None
        self.end_time = None
    def get_processing_time(self):
        """Gets the processing time for the timer.

        @return: float containing processing time in time.time() format.

        """
        return self.processing_time
    def get_string_processing_time(self):
        """Gets a string representation of the processing time.

        @return: string of processing time on the form::

                 H hours M minutes S seconds MS milliseconds

        """
        string_processing_time = ""
        str_list = []
        pt = self.processing_time
        t_h = (pt - pt % (60*60))/(60*60)
        pt = pt - (t_h * 60 * 60)
        t_m = (pt - pt % 60)/60
        pt = pt - (t_m * 60)
        t_s = pt - pt % 1
        pt = pt - t_s
        t_ms = pt * 1000
        if t_h > 1:
            str_list.append("%d hours" % t_h)
        elif t_h == 1:
            str_list.append("%d hour" % t_h)
        if t_m > 1:
            str_list.append("%d minutes" % t_m)
        elif t_m == 1:
            str_list.append("%d minute" % t_m)
        if t_s > 1:
            str_list.append("%d seconds" % t_s)
        if t_s == 1:
            str_list.append("%d second" % t_s)
        if t_ms > 1:
            str_list.append("%d milliseconds" % t_ms)
        if t_ms == 1:
            str_list.append("%d millisecond" % t_ms)
        return " ".join(str_list)

class Error(Exception):
    pass

class OrderError(Error):
    pass
