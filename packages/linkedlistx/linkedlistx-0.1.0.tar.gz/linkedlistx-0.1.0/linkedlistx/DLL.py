from .node import DLLNode
class DoubleLinkedList:
    __slots__ = ['tail','head']
    def __init__(self):
        self.head = None
        self.tail = None
        
    def insert_at_beginning(self,data):
        new_node = DLLNode(data)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
    
    def insert_at_end(self,data):
        new_node = DLLNode(data)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
            
    def append(self,data,position):
        new_node = DLLNode(data)
        if position <= 0 and not self.head:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        
        if not self.tail:
            self.head = self.tail = new_node
            return
        
        
        pos=self.head
        idx=0

        while pos and idx < position-1:
            pos = pos.next
            idx = idx+1
        
        if pos is None:
            self.insert_at_end(data)
            return
    
        prev_node =pos.prev

        new_node.next = pos
        new_node.prev = prev_node
        pos.prev = new_node
    

        if prev_node:
            prev_node.next = new_node
        else:
            self.head = new_node
        
    
        




    def remove(self,data):
        pos =self.head
        
        while pos is not None:

            if pos.data == data:
                if pos.prev is None:
                    self.head = pos.next
                    if self.head:
                        self.head.prev = None
                else:
                    pos.prev.next = pos.next
                    if pos.next:
                        pos.next.prev = pos.prev

                if pos.next is None:
                    if pos.prev:
                        pos.prev.next = None
                    self.tail=pos.prev
                    return
            
            pos=pos.next
        print("node does not exist")



    def delete(self,data):
        pos=self.head
        idx=0
        prev_node = pos.prev

        if not self.head:
            print("empty list")
            return

        if data == 1 or data == 0:
            temp = self.head
            self.head = temp.next
            if self.head:
                self.head.prev = None
            return            
        
        while pos is not None and idx< data-1:
            pos=pos.next
            idx=idx+1


        
        if pos is None:
            print("invalid postion")
            return
        
        
        if pos.next is None:
            if pos.prev:
                pos.prev.next = None
            self.tail = pos
            return
        
        if pos.next:
            pos.next.prev = pos.prev
        
        if pos.prev:
            pos.prev.next = pos.next
        return

      
        
          

    
    def show_val(self,postion):
        pos=self.head
        idx=0
        while pos and idx<postion:
            pos=pos.next
            idx=idx+1
        
        if pos:
            print(idx)
        else:
            print("invalid index")
    
    def show_len(self):
        pos=self.head
        l=0
        while pos:
            pos=pos.next
            l=l+1
        
        if not pos:
            print(l)
        return
      

    
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
        
        

       
    def display(self):
        cur = self.head
        while cur:
            print(cur.data, end=" <-> ")
            cur = cur.next
        print("none")
        return


    def generate(self,data):
        for i in range(1,data+1):
            self.append(i,i)
        return

    def del_at_start(self):
        pos = self.head
        self.head = pos.next
        if self.head:
            self.head.prev = None
        return


    def del_at_end(self):
        pos = self.tail
        self.tail = pos.prev
        if not self.tail:
            print("empty list")
            return
        
        if self.head == self.tail:
            self.head = self.tail = None
            return

        if self.tail:
            self.tail.next = None
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
        
        if pos is None:
            print("invalid position")
            return
    
    def reverse(self):
        current = self.head
        prev_node = None

        while current:
            next_node = current.next
            current.next = prev_node
            current.prev = next_node

            prev_node = current
            current = next_node
        
        self.tail = self.head
        self.head = prev_node
    
    
    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next