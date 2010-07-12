import time

class Timer(object):
    def __init__(self):
        self.processing_time = 0
    def start(self):
        self.start_time = time.time()
    def stop(self):
        self.end_time = time.time()
        self.processing_time += self.end_time - self.start_time
    def get_processing_time(self):
        return self.processing_time
    def get_string_processing_time(self):
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
