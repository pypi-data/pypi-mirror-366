from .node import SLLNode
class SingleLinkedList:
    __slots__ = ['head','tail']
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_at_beginning(self,data):
        new_node = SLLNode(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
    
    def insert_at_end(self,data):
        new_node = SLLNode(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:  
            self.tail.next = new_node
            self.tail = new_node

    def append(self,data,position):
        new_node = SLLNode(data)
        if position <= 0 or not self.head:
            new_node.next = self.head
            self.head = new_node
            
            
            if not self.tail:
                self.tail = new_node
            return

            
        pos = self.head
        idx = 1
        
        while pos.next and idx < position - 1:
            pos = pos.next
            idx = idx+1
        
        new_node.next = pos.next
        pos.next = new_node

        if new_node.next is None:
            self.tail = new_node
        

    def delete(self,data): 
        if not self.head:
            print("empty list")
            return

        if data == 0 or data == 1:
            self.head = self.head.next
            return
        
        temp = self.head
        count = 1

        while temp and count < data-1:
            temp = temp.next
            count = count+1
        
        if not temp or not temp.next:
            print("invalid postion")
            return
        
        if temp.next == self.tail:
            self.tail = temp
        temp.next = temp.next.next

    def remove(self,data):
        pos = self.head
        idx=0

        if not self.head:
            print("empty SLL")
            return
  
        if self.head.data == data or data == 0:
            self.head = self.head.next
            if not self.head:
                self.tail = None
            return
        
        while pos is not None and pos.next.data != data:
            pos = pos.next
            idx=idx+1
        
        if pos.next is not None:
            pos.next = pos.next.next
            if not self.head:
                self.tail = None           
            return

        if pos.next is not None:
            if pos.next == self.tail:
                self.tail = pos
            pos.next = pos.next.next
            return
        
        if pos.next is None:
            print("invalid input")
    
    
    def display(self):
        cur = self.head
        while cur:
            print(cur.data, end = "-> ")
            cur = cur.next
        print("none")

    def show_val(self,position):
        pos = self.head
        idx = 0
        while pos and idx < position-1:
            pos = pos.next
            idx = idx+1
        
        if not pos:
            print("invalid index")
        else:
            print(pos.data)
    
    def show_len(self):
        pos = self.head
        l=0
        while pos:
            pos= pos.next
            l=l+1
       
    
        print(l)

    def find(self,data):
        pos=self.head
        idx=1
        while pos:
            if pos.data == data:
                print(idx)
                break
            pos = pos.next
            idx=idx+1
        
        if not pos:
            print("invalid input")
        
        

    def generate(self,data):
        for i in range(1,data+1):
            self.append(i,i)
    
    def del_at_end(self):
        pos = self.head
        if not self.head:
            print("empty list")
            return

        if self.head == self.tail:
            self.head = None
            self.tail = None

        while pos.next != self.tail:
            pos = pos.next
            temp = pos.next
        if pos.next:
            temp.next = None
        self.tail = temp
        return

    def del_at_start(self):
        if not self.head:
            print("empty list")
        else:
            self.head = self.head.next
        return
    
    def update(self, position, data):
        pos = self.head
        idx=0
        
        if not self.head:
            print("empty list")
            return
        

        while pos and idx < position-1:
            pos = pos.next
            idx=idx+1
        
        if pos:
            pos.data = data
            return
        
        if pos is None:
            print("invalid position")
            return
        
    def reverse(self):
        prev = None
        cur = self.head
        self.tail = self.head
        
        if not self.head:
            print("empty list")
            return


        while cur:
            next_node = cur.next
            cur.next = prev
            prev = cur
            cur = next_node
        self.head = prev
        return
    
    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next
