# linkedlistx

A Python package that provides implementations of **four types of linked lists**:

- ✅ Singly Linked List (SLL)
- ✅ Doubly Linked List (DLL)
- ✅ Circular Singly Linked List (CLL)
- ✅ Circular Doubly Linked List (DCLL)

This library is great for learning, teaching, or using classical linked list data structures in any Python project.

---

## 🧠 Features

- Insert at beginning or end
- Insert at a specific position (`append`)
- Delete by index or value
- Reverse the list
- Find elements by value
- Generate auto-filled lists (`generate(n)`)
- View list length or value at a position
- Iterable linked lists (`for node in list:`)

Each list type preserves its structural characteristics (circularity, bidirectionality, etc.)

---

## 📁 Project Structure

linkedlistx/
├── CLL.py # Circular Singly Linked List
├── DLL.py # Doubly Linked List
├── DCLL.py # Circular Doubly Linked List
├── SLL.py # Singly Linked List
├── node.py # Node classes
├── init.py # Unified imports

from linkedlistx import SingleLinkedList

sll = SingleLinkedList()
sll.insert_at_beginning(10)
sll.insert_at_end(20)
sll.display()  # Output: 10-> 20-> None

--------
from linkedlistx import DoubleLinkedList

dll = DoubleLinkedList()
dll.generate(5)
dll.reverse()
dll.display()  # Output: 5-> 4-> 3-> 2-> 1-> None

--------

from linkedlistx import CircularDoubleLinkedList

dcll = CircularDoubleLinkedList()
dcll.insert_at_beginning(5)
dcll.insert_at_end(15)
dcll.display()

✅ Common to All Lists
Method	Description
insert_at_beginning(data)	Insert node at head
insert_at_end(data)	Insert node at tail
append(data, pos)	Insert at specified position
delete(pos)	Delete node at position
remove(data)	Delete first node with value
update(pos, data)	Update value at position
show_val(pos)	Print value at position
show_len()	Print number of nodes
find(data)	Print index of data or error
generate(n)	Auto-fill list with 1 to n
del_at_start()	Delete first node
del_at_end()	Delete last node
reverse()	Reverse the list
display()	Print node values
__iter__()	Make list iterable

🔩 Node Structure
# SLL Node
class SLLNode:
    def __init__(self, data):
        self.data = data
        self.next = None

# DLL Node
class DLLNode:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

🪪 License
This project is licensed under the MIT License.

🤝 Contributing
Contributions are welcome!
Feel free to open issues or pull requests to enhance functionality, fix bugs, or suggest new features.

👤 Author
Developed by Aswath 🫡
GitHub: https://github.com/aswath-maker