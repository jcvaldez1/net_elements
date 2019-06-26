class scale_object():
    
    def __init__(self, cores=2, prev_core=None, next_core=4, up_threshold=90,
                 down_threshold=None,flavor="lmao2"):
        self.cores = cores
        self.prev_core = prev_core
        self.next_core = next_core
        self.up_threshold = up_threshold
        self.down_threshold = down_threshold
        self.flavor = flavor

    def scale(self, direction, val_dict):
        if direction == 1:
            self.prev_core = self.cores
            self.cores = self.next_core
            self.next_core = self.cores + 2
        elif direction == -1:
            self.next_core = self.cores
            self.cores = self.prev_core
            self.prev_core = self.cores - 2
        self.update_vals(val_dict)

    def scale_determine(self, metric_value):
        if (self.up_threshold) and (metric_value > self.up_threshold):
                return True,1
        elif (self.down_threshold) and (metric_value < self.down_threshold):
                return True,-1
        return False,None


    def update_vals(self,val_dict):
        for key, val in val_dict.iteritems():
            if key in self.__dict__:
                self.__dict__[key] = val
