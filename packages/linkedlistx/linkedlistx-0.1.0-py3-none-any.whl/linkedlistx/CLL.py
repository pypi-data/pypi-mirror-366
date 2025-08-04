from .node import SLLNode
class CircularLinkedList:
    __slots__ = ['head','tail']
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_at_beginning(self,data):
        new_node = SLLNode(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            self.tail.next = self.head
        else:
            new_node.next = self.head
            self.head = new_node
            self.tail.next = self.head
    
    
    def insert_at_end(self,data):
        new_node = SLLNode(data)
        if not self.tail:
            self.head = new_node
            self.tail = new_node
            self.tail.next = self.head
        else:
            self.tail.next = new_node
            self.tail = new_node
            self.tail.next = self.head
    
    
    def append(self,data,position):
        new_node = SLLNode(data)
        if position < 0 and not self.head:
            self.head = new_node
            self.tail = new_node
            self.tail.next = self.head

            if not self.tail:
                self.tail = new_node
                self.tail.next = self.head
            return
        
        if position == 0:
            self.insert_at_beginning(data)
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
            self.tail.next = self.head



    def delete(self,position):
        if not self.head:
            print("empty list")
            return
        
        if position <= 1:
            self.head = self.head.next
            self.tail.next = self.head
            return
        
        pos = self.head
        idx=1

        while pos and idx< position-1:
            pos=pos.next
            idx=idx+1
        
        next_node = pos.next
        pos.next = next_node.next
        self.tail.next = self.head
        self.tail = pos

            
    def remove(self, data):
        if not self.head:
            print("Empty CLL")
            return

        current = self.head
        prev = self.tail
        found = False

        while True:
            if current.data == data:
                found = True
                break
            prev = current
            current = current.next
            if current == self.head:
                break  # Came full circle without finding

        if not found:
            print("Data not found in CLL")
            return

        # If it's the only node in the list
        if self.head == self.tail and self.head.data == data:
            self.head = None
            self.tail = None
            return

        # If removing the head
        if current == self.head:
            self.head = self.head.next
            self.tail.next = self.head
            return

        # If removing the tail
        if current == self.tail:
            self.tail = prev

        # General case
        prev.next = current.next

    def show_val(self, position):
        if not self.head:
            print("invalid index")
            return

        pos = self.head
        idx = 1
        while idx < position:
            pos = pos.next
            if pos == self.head:
                print("invalid index")
                return
            idx += 1

        print(pos.data)

    def show_len(self):
        if not self.head:
            print(0)
            return

        pos = self.head
        l = 1
        while pos.next != self.head:
            pos = pos.next
            l += 1

        print(l)
    
    def find(self, data):
        if not self.head:
            print("invalid input")
            return

        pos = self.head
        idx = 1
        while True:
            if pos.data == data:
                print(idx)
                return
            pos = pos.next
            idx += 1
            if pos == self.head:
                break

        print("invalid input")

    def generate(self, data):
        for i in range(1, data + 1):
            self.append(i, i)


    def del_at_end(self):
        if not self.head:
            print("empty list")
            return

        if self.head == self.tail:
            self.head = None
            self.tail = None
            return

        pos = self.head
        while pos.next != self.tail:
            pos = pos.next

        pos.next = self.head
        self.tail = pos

    def del_at_start(self):
        if not self.head:
            print("empty list")
            return

        if self.head == self.tail:
            self.head = None
            self.tail = None
            return

        self.head = self.head.next
        self.tail.next = self.head

    def update(self, position, data):
        if not self.head:
            print("empty list")
            return

        pos = self.head
        idx = 1
        while idx < position:
            pos = pos.next
            if pos == self.head:
                print("invalid position")
                return
            idx += 1

        pos.data = data

    def reverse(self):
        if not self.head:
            print("empty list")
            return

        prev = self.tail
        cur = self.head
        self.tail = self.head

        while True:
            next_node = cur.next
            cur.next = prev
            prev = cur
            cur = next_node
            if cur == self.head:
                break

        self.head = prev
        self.tail.next = self.head

    def display(self):
        cur = self.head
        if not self.head:
            print("empty list")
            return
        while True:
            print(cur.data, end="-> ")
            cur = cur.next
            if cur == self.head:
                break
        
        print("back to head")




            