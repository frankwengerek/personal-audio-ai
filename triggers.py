class Triggers:
    def __init__(self):
        self.triggers = []
    
    def add_trigger(self, new_trigger):
        self.triggers.append(new_trigger)
        
    def detect_trigger(self, text):                                         
        res = None
        
        i = 0
        found = False
                        
        while i < len(self.triggers) and not found:
            t = self.triggers[i]
            found = t.keyword in text.lower()
            if found:
                res = t
            else:
                i += 1
        
        return res