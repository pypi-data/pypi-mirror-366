from .node import DLLNode
class CircularDoubleLinkedList:
    __slots__ = ['head', 'tail']

    def __init__(self):
        self.head = None
        self.tail = None

    def insert_at_beginning(self, data):
        new_node = DLLNode(data)
        if not self.head:
            self.head = self.tail = new_node
            new_node.next = new_node.prev = new_node
        else:
            new_node.next = self.head
            new_node.prev = self.tail
            self.head.prev = new_node
            self.tail.next = new_node
            self.head = new_node

    def insert_at_end(self, data):
        new_node = DLLNode(data)
        if not self.head:
            self.head = self.tail = new_node
            new_node.next = new_node.prev = new_node
        else:
            new_node.prev = self.tail
            new_node.next = self.head
            self.tail.next = new_node
            self.head.prev = new_node
            self.tail = new_node

    def append(self, data, position):
        new_node = DLLNode(data)
        if not self.head or position <= 0:
            self.insert_at_beginning(data)
            return

        pos = self.head
        idx = 1
        while idx < position and pos.next != self.head:
            pos = pos.next
            idx += 1

        new_node.next = pos
        new_node.prev = pos.prev
        pos.prev.next = new_node
        pos.prev = new_node

        if pos == self.head and position == 1:
            self.head = new_node

    def remove(self, data):
        if not self.head:
            print("empty list")
            return

        pos = self.head
        while True:
            if pos.data == data:
                if pos == self.head and pos == self.tail:
                    self.head = self.tail = None
                    return

                if pos == self.head:
                    self.head = pos.next
                    self.tail.next = self.head
                    self.head.prev = self.tail
                elif pos == self.tail:
                    self.tail = pos.prev
                    self.tail.next = self.head
                    self.head.prev = self.tail
                else:
                    pos.prev.next = pos.next
                    pos.next.prev = pos.prev
                return

            pos = pos.next
            if pos == self.head:
                break

        print("node does not exist")

    def delete(self, position):
        if not self.head:
            print("empty list")
            return

        if position <= 1:
            if self.head == self.tail:
                self.head = self.tail = None
                return
            self.head = self.head.next
            self.head.prev = self.tail
            self.tail.next = self.head
            return

        pos = self.head
        idx = 1
        while idx < position and pos.next != self.head:
            pos = pos.next
            idx += 1

        if pos == self.head:
            print("invalid position")
            return

        if pos == self.tail:
            self.tail = pos.prev
            self.tail.next = self.head
            self.head.prev = self.tail
        else:
            pos.prev.next = pos.next
            pos.next.prev = pos.prev

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

    def display(self):
        if not self.head:
            print("empty list")
            return
        cur = self.head
        while True:
            print(cur.data, end=" <-> ")
            cur = cur.next
            if cur == self.head:
                break
        print("(back to head)")

    def generate(self, data):
        for i in range(1, data + 1):
            self.append(i, i)

    def del_at_start(self):
        if not self.head:
            print("empty list")
            return
        if self.head == self.tail:
            self.head = self.tail = None
            return
        self.head = self.head.next
        self.head.prev = self.tail
        self.tail.next = self.head

    def del_at_end(self):
        if not self.head:
            print("empty list")
            return
        if self.head == self.tail:
            self.head = self.tail = None
            return
        self.tail = self.tail.prev
        self.tail.next = self.head
        self.head.prev = self.tail

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

        cur = self.head
        prev_node = None

        while True:
            next_node = cur.next
            cur.next = cur.prev
            cur.prev = next_node
            prev_node = cur
            cur = next_node
            if cur == self.head:
                break

        self.head = prev_node
        self.tail = self.head.prev

    def __iter__(self):
        if not self.head:
            return
        current = self.head
        while True:
            yield current.data
            current = current.next
            if current == self.head:
                break
