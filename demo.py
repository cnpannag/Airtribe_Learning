print ("hello world")
a = 5
print(type(a))
a = "a"
print(type(a))
# PYthon is not Statically Typed programming language like java, it's a dynamically typed promgramming language
def add_num(a,b):
    print (f"The sum is:  {a+b}") 
    return a+b

add_num1 = lambda a, b: print(a + b) or (f"The sum is:  {a+b}")
# Exploit the fact that print() always returns None. 
# In Python, None or value will always evaluate to the value.

add_num(1,2)
# The sum is:  3
add_num1(2,3)
# 5
print(add_num1(2,3))
# The sum is:  5


def add_num2(a,b):
    if (a>0 and b>0): 
        print (f"The sum is:  {a+b}") 
    else:
        print(" less than 0")
    return a+b

# ## 1. The Conditional Expression (Ternary Operator)
# Python allows you to write an if-else block inside a single expression. This is perfect if you want to condense the print logic.

def add_num3(a, b):
    print(f"The sum is: {a+b}" if a > 0 and b > 0 else "less than 0")
    return a + b

# ## 2. Short-Circuit Evaluation (The and/or Hack)
# In Python, logical operators like and and or don't just return True or False; they return the actual value of the last evaluated expression.

# * A and B: If A is true, it evaluates and returns B.
# * A or B: If A is true, it short-circuits and returns A immediately without checking B.

def add_num4(a, b):
    # If the condition is True, it executes the print. If False, it moves to the 'or' branch.
    (a > 0 and b > 0) and print(f"The sum is: {a+b}") or print("less than 0")
    return a + b

# ## 3. Structural Pattern Matching (Python 3.10+)
# If you want to handle complex conditional rules cleanly, Python's match-case statement is a highly readable alternative to nested if statements. You can match against the tuple (a, b) and use guards (if).

def add_num5(a, b):
    match (a, b):
        case (x, y) if x > 0 and y > 0:
            print(f"The sum is: {a+b}")
        case _:
            print("less than 0")
    return a + b

# ## 4. Dictionary Mapping with Booleans
# Booleans in Python (True and False) are a subclass of integers (1 and 0). You can use a dictionary or a list where the keys are True and False to pick which function or string to execute.

def add_num6(a, b):
    # True maps to 1, False maps to 0
    messages = ["less than 0", f"The sum is: {a+b}"]
    print(messages[a > 0 and b > 0])
    return a + b

status = 700

match status:
    case 200:
        print("success")
    case 404:
        print("Not Found")
    case x:
        print("unknown, try something else")
# unknown, try something else
# "x" here does not mean the alphabet, it's an else.
# can also use _ instead of x

status1 = 700

match status1:
    case 200:
        print("success")
    case 404:
        print("Not Found")
    case _:
        print("unknown, try something else")
        # unknown, try something else


status2 = 100

match status2:
    case n if n <= 200:
        print("success")
    case n if n <= 404:
        print("Not Found")
    case _:
        print("unknown, try something else")
        # success


for i in range(5):
    print (i)

for i in range(0,5,2):
    print (i)

# Creates a list of numbers directly in memory
numbers = [i for i in range(5)]
print(numbers)

# Generator Expression: Memory efficient, yields items one by one on-demand
numbers_gen = (i for i in range(5))
print(numbers_gen)

# Prints: 0 1 2 3 4
print(*range(5)) 

print(range(5) == range(0, 5))
# true
print(range(5) is range(5))
# false

# range(5) == range(0, 5) returns True because their generated sequences are identical.
# range(5) is range(5) returns False. A range object is a lazy iterable. Python instantiates a new memory object each time you invoke range(), even if the arguments match. [1] 

functions = []

for i in range(5):
    functions.append(lambda: i)

print([f() for f in functions])
# It outputs [4, 4, 4, 4, 4], not [0, 1, 2, 3, 4].
# Python closures use late binding. 
# The inner lambda functions look up the value of i when they are called, 
# not when they are defined. By the time you call f(), 
# the loop has finished and i is 4.

functions1 = []

for i in range(5):
    functions.append(lambda: i)
    print(i)
    print([f() for f in functions])
# 0
# [0, 0, 0, 0, 0, 0]
# 1
# [1, 1, 1, 1, 1, 1, 1]
# 2
# [2, 2, 2, 2, 2, 2, 2, 2]
# 3
# [3, 3, 3, 3, 3, 3, 3, 3, 3]
# 4
# [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]

# length = int(input("array length")) #  user input
# print (range(length))
# # range(0, 5)
# print (*range(length))
# 0 1 2 3 4


x = 10
y = 10

print(f"x {x} {id(x)} and y {y} {id(y)} refer to same object")
# x 10 140723996273368 and y 10 140723996273368 refer to same object
# Here both x and y refer to the same memory location
x += 1
print(f"x {x} {id(x)} and y {y} {id(y)} refer to different object")
# now x will refer to a different memory location
# y += 1x 11 140723996273400 and y 10 140723996273368 refer to different object
print(f"x {x} {id(x)} and y {y} {id(y)} refer to same object")
# now x and y will refer to a the same memory location again
# x 11 140723996273400 and y 11 140723996273400 refer to same object

x= "asdfasdfasdfhjkhjkhjkhjklhjklhjkh"
y= "asdfasdfasdfhjkhjkhjkhjklhjklhjkh"
print(f"x {x} {id(x)} and y {y} {id(y)} refer to same object")
# x asdfasdfasdfhjkhjkhjkhjklhjklhjkh 1781005151856 and y asdfasdfasdfhjkhjkhjkhjklhjklhjkh 1781005151856 refer to same object


# List / Array
# int[] arr[0]=[10,20,30] --> Java
# [][][][10][20][30][][][][][] --> In c++ or JAva it will ensure the location is next to each other on the RAM
# [][][][][][][][][][][][][][] --> Python
# lets assume [10] is in m112
# arr[0] = m112 + 0
# arr[2] = m112 + 2
# Array is always 0 refrenced
# [][][][10][20][30][A][B][][][]
# Lets say after 30 there is no emply slot
# now if you want to add one number into array then it cant be done since the next slot is not empty
# thats why array size cannot be changed



# List is a dynamic array > it can change it's size
# Python uses just List instead of array
# list l = [] (type int) // initial size 3
# [1][][][][f][g][][][][][]
#    |....| 3 memory are initially reserved
# Say the list size increases to 5
# The entire list will be moved to a new location with the available continuous slots
# [1][][][][f][g][][][][][]
#                |.........| 5 memory are newly reserved
# old data is moved to new location
# old memory location is freed up
# List can be homogenous or heterogeneous
# Pointers, not direct values: Python lists do not store the actual data (like 1, f, g) directly inline in the array. Instead, a Python list is an array of memory addresses (pointers) that point to where the actual objects live elsewhere in memory. This is why they can be heterogeneous.
# Growth Factor (Over-allocation): When a list runs out of space, Python doesn't just increase the size by the exact amount needed (e.g., from 3 to 5). It allocates extra padding space (over-allocation) so it doesn't have to resize every single time you append a new item.
# Initial Size: An empty list [] actually starts with 0 reserved slots in Python. The moment you append the first item, Python allocates a small batch of slots (typically 4 in standard CPython).
# 2. The Resizing Mechanism (Dynamic Array Over-allocation)Your note correctly states that when the list grows, it moves to a new continuous block of memory and frees the old one. However, the sizing math is highly optimized.If Python resized your array from 3 to 4, then 4 to 5, then 5 to 6, your code would become incredibly slow because moving data in memory is expensive. To solve this, Python uses an over-allocation formula.In standard Python (CPython), the growth pattern roughly follows this progression as you append items:0 ➔ 4 ➔ 8 ➔ 16 ➔ 25 ➔ 35 ➔ 46 ➔ 58...Step 1: You create l = []. Allocated capacity = 0.Step 2: You append 1. Python over-allocates. Allocated capacity = 4 (1 used, 3 empty).Step 3: You append items until you hit 4.Step 4: You try to append a 5th item. The array is full! Python allocates a brand new block of continuous memory with room for 8 items. It copies the 4 old pointers to the new block, appends the 5th, leaves 3 slots empty, and destroys the old 4-slot array.This ensures that appending an item is Amortized \(O(1)\) time complexity—meaning it is blazing fast almost all of the time, and only occasionally takes a hit when a resize occurs.


# linked list
# [a|b] = node
# a is the data, b is the memory of the next node
# myll=[]
# myll.add(10)
# myll.add(20)
# myll.add(30)
# myll.delete(20)
# [][][30, null][][10, <add of 20>][][][20, <add of 30>][][]
# ⚠️ Weakness 1: No Direct Access / Indexing (O(n))In a dynamic array, if you want list[99], the computer calculates the memory offset instantly.In a Linked List, you cannot say list[99]. The computer has no idea where the 99th node is because the slots aren't next to each other. You must start at the Head and manually step through (Node 1 ➔ Node 2 ➔ Node 3...) until you count to 99.
# ⚠️ Weakness 2: Extra Memory OverheadBecause every single node has to store both the value and the memory address of the next node, a Linked List consumes significantly more RAM than a standard array holding the exact same data.
# Python doesn't have a built-in LinkedList primitive type like it does with list.

# list access is 1 time complexity O(1)
# linked list is n time complexity O(n)

# IN python list store address that points to the data so we might think it's O(1 memory location +1 getting data from the location)
# but In computer science, if an operation takes a fixed number of steps (whether it's 1 step, 2 steps, or 5 steps) and that number never changes regardless of how big your list gets, it is classified as Constant Time, or \(O(1)\).
# so it is still O(1) not O(2)






myset = {1,1,2,3}
print (myset)
# {1, 2, 3}  >> Set cannot have duplicates
myset.add(4)
print(myset)

# 1. The Mathematical Definition
# In mathematics, a set is a collection of distinct elements. Python sets strictly follow this rule. The order of elements does not matter, and an item is either in the set or it isn't—it cannot exist inside the set multiple times.
# 2. How it Works Under the Hood (Hashing)
# Python sets are implemented using a data structure called a hash table (very similar to the keys of a Python dictionary).
# •	When you add an element to a set, Python calculates a unique integer for it called a hash value.
# •	It uses this hash value to determine exactly where to store the element in memory.
# •	If you try to add a duplicate item (like the second 1 in your example), Python looks up its hash value, sees that the exact same slot is already occupied by an identical value, and simply overwrites or skips it.
# 3. The Core Benefit: Blazing Fast Lookups
# Because sets use hash tables, checking if an item exists in a set (item in myset) takes a constant amount of time—\(O(1)\) time complexity—no matter how large the set is. If sets allowed duplicate items scattered everywhere, Python would have to scan the entire collection to find them, making lookups much slower.
# ________________________________________
# Quick Comparison: Set vs. List
# If you need to keep duplicate values and care about the order in which they appear, you should use a list or a tuple instead.
# Data Type	Allows Duplicates?	Ordered?	Syntax
# Set	    ❌ No               ❌ No	     {1, 2, 3}
# List	    Yes                    	Yes 	[1, 1, 2, 3]
# Tuple	    Yes	                    Yes	    (1, 1, 2, 3)


mytuple = ([1],[2],[3]) # This is a tuple of list
# mytuple[3] = 50  > Error, tuple cannot be changed
mytuple[1][0] = 4 # > ([1], [4], [3]) because we are changing the value of list inside the tuple and but the tuple itself
print (mytuple)
# ([1], [4], [3])

# 1. Fixed Allocation vs. Over-Allocation
# •	Tuples are tightly packed: When you create a tuple like (1, 2, 3), Python allocates a memory block with exactly enough room to hold the metadata and references to those 3 items. There is no leftover space.
# •	Lists over-allocate memory: When you create a list like [1, 2, 3], Python purposely allocates a larger memory block than needed (e.g., room for 6 or 8 items). This "buffer" exists so that when you use .append(), Python can instantly slot the new item into the pre-allocated extra space without crashing into neighboring data.
# 2. The Internal C Structure
# Python is written in the C programming language. Under the hood:
# •	A list points to a resizable array (PyListObject), which contains a pointer to the data and a dynamic slot tracking its allocated capacity.
# •	A tuple points to a fixed-size array (PyTupleObject). It contains a field called ob_size that is set at birth and marked as read-only. Python's interpreter simply lacks any code or mechanisms to resize a PyTupleObject.
# 3. Visualizing the Memory Layout
# Imagine RAM as a series of tight slots on a shelf:
# text
# Tuple (1, 2, 3) ->  [ Metadata ][ Item 1 ][ Item 2 ][ Item 3 ] [Neighboring Data...]
#                     ^ Closed block. No room to grow or shift.

# List [1, 2, 3]  ->  [ Metadata ][ Item 1 ][ Item 2 ][ Item 3 ] [ Empty ][ Empty ] [Neighboring Data...]
#                     ^ Open block. Extra buffer slots reserved for .append()
# Use code with caution.
# If you tried to add an item to a tuple, it would bleed directly into "Neighboring Data" belonging to other parts of your program, causing corruption. Therefore, Python blocks it entirely.
# 4. The Memory Efficiency Payoff
# Because tuples do not require a memory buffer, they are much lighter. For example, a 3-element tuple takes 64 bytes of memory, while an identical 3-element list takes 88 bytes.
# ________________________________________







# In Python, the difference between a shallow copy and a deep copy only matters when you are copying nested collections (like a list inside a list).
# The core difference is how deep the copy goes: a shallow copy constructs a new collection but fills it with references to the original child objects, while a deep copy recursively duplicates everything, creating a completely independent clone.
# ________________________________________
# 🧱 1. Shallow Copy
# A shallow copy creates a new outer object, but it does not copy the objects inside it. Instead, it just copies the memory addresses (references) of the inner objects.
# •	How to do it: copy.copy(object) or using .copy() on lists/dicts.
# •	The Danger: If you modify a nested (inner) item in the copy, the change will also appear in the original object because they both point to the exact same memory slot.
import copy

original = [[1, 2], [3, 4]]
shallow_clone = copy.copy(original)

# Modify a nested item in the clone
shallow_clone[0][0] = 99

print(original)       # Output: [[99, 2], [3, 4]] -> ❌ Original CHANGED!
print(shallow_clone)  # Output: [[99, 2], [3, 4]]
# ________________________________________
# 🧬 2. Deep Copy
# A deep copy creates a new outer object and then recursively copies all objects found inside it. It walks down the entire tree of data and duplicates every single layer.
# •	How to do it: copy.deepcopy(object)
# •	The Benefit: The original and the clone are 100% disconnected. Changing anything inside the clone will never affect the original.
import copy

original = [[1, 2], [3, 4]]
deep_clone = copy.deepcopy(original)

# Modify a nested item in the clone
deep_clone[0][0] = 99

print(original)    # Output: [[1, 2], [3, 4]]   ->  Original stays safe!
print(deep_clone)  # Output: [[99, 2], [3, 4]]
# ________________________________________
# 📊 Direct Comparison
# Feature	🌊 Shallow Copy (copy.copy())	🧬 Deep Copy (copy.deepcopy())
# Outer Structure	Duplicated (New memory address)	Duplicated (New memory address)
# Inner/Nested Objects	Shared (Same memory addresses)	Duplicated (New memory addresses)
# Performance	Very fast and memory efficient	Slower and uses more memory
# Best Used For	Flat lists or when sharing internal state is fine	Complex, deeply nested configurations or data models
# ________________________________________
# Are you encountering a bug where modifying one variable is unexpectedly changing another in your code? If you paste the snippet you are working on, I can point out exactly where the reference link is happening and show you how to fix it!




# Keys in dict have to be unique
mydict = {1:"a", 2:"a", 3:"b", 1:"d"}  # -> 1: "a" is lost because keys cannot be duplicate, it will only store 1:"d" given in the end
print(mydict) # {1: 'd', 2: 'a', 3: 'b'}
mydict[4]="c"
del mydict[2]
print(mydict) # {1: 'd', 3: 'b', 4: 'c'}

# 1. The Core Architecture in Memory
# Instead of storing everything in one giant, mostly empty array, a dictionary splits its memory structure into two separate tables:
# 1.	The Index Array (The Hash Table): A small, dense array consisting purely of integers (indices). It acts as a routing table.
# 2.	The Entries Array: A tightly packed array where each slot contains the actual data: [Hash Code, Pointer to Key, Pointer to Value]. [1, 2]
# text
# INDEX ARRAY (Sparse & Small)
# [ -1 |  0 | -1 |  1 | -1 | -1 | -1 | -1 ]  <-- (Indices point to the Entries Array)

#         |       |
#         v       v
# ENTRIES ARRAY (Tightly Packed)
# Idx 0: [ HashA, Pointer to KeyA, Pointer to ValueA ]
# Idx 1: [ HashB, Pointer to KeyB, Pointer to ValueB ]
# Use code with caution.
# ________________________________________
# 2. How Writing Data Works (Insertion)
# When you run a command like my_dict["age"] = 25, the computer performs the following memory actions:
# •	Step 1: Hashing the Key
# The computer takes the key ("age") and passes it through a deterministic hash function to generate a giant, unique integer (e.g., -482910384). Because this integer must be deterministic, dictionary keys must be immutable (like strings or integers) so their hash value never alters. [1, 2]
# •	Step 2: Finding a Slot via Modulo
# The computer needs to map that giant integer to the size of the Index Array. If the Index Array has 8 slots, it performs a modulo operation: hash_code % 8. Let's say the result is 3. [1]
# •	Step 3: Storing the Data
# The raw data [Hash, Pointer to "age", Pointer to 25] is appended to the next available slot in the Entries Array (let's say it goes into index 0).
# The computer then updates slot 3 of the Index Array to point to index 0 of the Entries Array.
# ________________________________________
# 3. How Reading Data Works (Lookup)
# When you request a value via my_dict["age"], the process runs in reverse: [1]
# 1.	The computer hashes "age" and applies the modulo to get the index 3.
# 2.	It jumps directly to slot 3 of the Index Array and reads the value (0).
# 3.	It uses that value to jump directly to index 0 of the Entries Array.
# 4.	It compares the requested key ("age") with the key stored at that memory address. If they match, it instantly returns 25. [1, 2]
# Because it calculates the memory location mathematically, it doesn't need to loop through every item, resulting in constant-time O(1) operations. [1, 2]
# ________________________________________
# 4. Handling Memory Conflicts (Collisions)
# What happens if two entirely different keys (e.g., "age" and "height") result in the exact same modulo index? This is a hash collision. [1]
# •	Resolution (Open Addressing / Linear Probing): If the computer checks the Index Array at the calculated slot and finds it's already occupied by another key, it uses a deterministic algorithm to probe for the next available slot (e.g., checking slot 4, then 5). [1]
# •	Verification: This is why the Entries Array stores the original hash and key. When looking up a value, the computer doesn't just trust the slot; it checks to see if the key matches. If it doesn't, it knows a collision occurred and follows the exact same probing path to find the correct data. [1, 2]
# ________________________________________
# 5. Dynamic Resizing
# Dictionaries start out by allocating a small block of memory (typically 8 slots). As you add items, the table fills up. [1, 2]
# If a hash table becomes too crowded, collisions skyrocket, and performance drops. To prevent this, once the dictionary gets roughly two-thirds full, the system triggers a resize. It allocates a brand new, significantly larger Index Array (usually doubling in size), recalculates the modulos for all existing keys, and remaps the old entries to the new index layout. [1, 2]
# If you are trying to optimize code or fix an issue involving dictionaries, let me know what programming language you are using or share the code snippet you're working on so we can look at it directly!

# tuple and list are same but tuple is IMMUTABLE


add = lambda x,y: x+y
print(add(1,2))
print ((lambda x,y: x+y)(2,2))

# A single-line grading system
get_grade = lambda score: "A" if score >= 90 else ("B" if score >= 80 else ("C" if score >= 70 else "F"))

print(get_grade(85))  # Output: B
print(get_grade(62))  # Output: F


# THE TRAP: All lambdas look up 'x' at the end of the loop (where x is 2)
broken_multipliers = [lambda y: x * y for x in range(3)]
print([f(10) for f in broken_multipliers])  # Output: [20, 20, 20]

# THE TRICK: Use a default argument (arg=x) to bind the value instantly
working_multipliers = [lambda y, arg=x: arg * y for x in range(3)]
print([f(10) for f in working_multipliers])  # Output: [0, 10, 20]

# If you build a list of lambdas inside a loop, Python uses lexical scoping—meaning all functions will look up the variable x at execution time, resulting in all of them using the final loop value. To trick Python into freezing the value at creation time, you use a default argument. [1] (https://www.geeksforgeeks.org/python/python-lambda-anonymous-functions-filter-map-reduce/)


# Side effect (print) and calculation inside a single expression
spool_data = lambda name, value: (print(f"Processing {name}..."), value * 2)[1]

# It will print the log to the console, but assign only the calculation result
final_score = spool_data("Alpha_Team", 50)
print(f"Final Score: {final_score}")

# Console Output:
# Processing Alpha_Team...
# Final Score: 100
# [1] extract the second element from the tuple created inside the lambda function.
# In Python, index tracking starts at 0. By appending [1] to the end of the tuple, you are telling Python: "Execute everything inside the parentheses, but only return the item at index 1."
# Here is exactly how Python processes it step-by-step:
# 1.	Creates a Tuple: The expression evaluates to a two-item tuple: (print(...), value * 2).
# 2.	Executes Index 0: Python runs print(f"Processing {name}..."), which outputs the text to your console. Since print() doesn't return anything, its position in the tuple is filled by None. The tuple now looks like (None, 100).
# 3.	Executes Index 1: Python calculates value * 2, which results in 100.
# 4.	Applies the Slicing: The [1] at the end grabs the element at index 1 (100) and discards the None.
# Without that [1], the lambda would return the entire tuple (None, 100). Adding [1] acts as a filter so your variable only catches the actual math result!



