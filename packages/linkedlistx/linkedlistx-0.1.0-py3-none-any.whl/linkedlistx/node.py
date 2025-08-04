class SLLNode:
    __slots__ = ['data','next']
    def __init__(self,data):
        self.data = data
        self.next = None

class DLLNode:
    __slots__ = ['prev', 'data', 'next']
    def __init__(self,data):
        self.data = data
        self.prev = None
        self.next = None