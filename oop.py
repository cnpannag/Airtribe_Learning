class biryani:

    def __init__(self, protien_type, no_plates,is_spicy) -> None:
        self.protien_type = protien_type
        self.no_plates = no_plates
        self.is_spicy = is_spicy

my_biryani = biryani("paneer", 1, True)
print(my_biryani)
print(my_biryani.is_spicy)

class Animal:
    type = "Dog" # This is a class level object
    # if call is Animal.type 
        # This is a class level object 
        # WE can directly call this as Animal.type
    # if call is from an object animal.type
        # This is object level, 
        # It is called after an object for Animal is created
    type1 = "Dog"

    def __init__(self, name):
        self.name = name

animal = Animal("Jimmy")

print(animal.type) # Dog
animal.type = "cat"
print(animal.type) # cat
print(Animal.type) # Dog
# print(Animal.name)  # This will give an error since it is not called by an object
print (animal.name) # Jimmy

"""
whatever we write inside the class is member of the class includes 
variables
functions

members are of 2 types?
1. Class level members are static like Type=Dog written above.
    We should generally not do this

2. object level members are non static like creating an object called "animal" and calling animal.type

in java you need to explicitly write "Static String type = "Dog" "
while in python just "type = "Dog" " wil be enough


object-level (Non-static)
[][][][       m1        ][][][][][][ Jimmy ][][][]
        animal.name                     m1
Object level only exists when the object is created
        
class-level (static)
[][][][][][][][][ Dog ][][][][][][]
                  type
Weather you create an object or not, it will already have the value Dog, 
thats why it can be accessed without object creation

In Python (only, not java) what happens in our program
[][][][      m1,m2       ][][][Jimmy][Dog --> Cat][][][][     Dog     ][][][][]
       animal(name,type)        m1      m2                Animal.Type
Python has different memory for its objects and different for the variable
SO one object level copy per object and one class level copy
"""

# But If we change on a class level, it will reflect on object level too

Animal.type="rat"
print(Animal.type, animal.type) # rat cat

Animal.type1="mouse"
print(Animal.type1, animal.type1) #mouse mouse
"""
in the above example we see rat cat in one place but mouse mouse in the other.
The reason here is because we had previously called "animal.type = "cat""

when animal.type = "cat" was called, it created a new memory location 
but since animal.type1 = "cat" was never called, both the class level and object level was pointing to the same memory


[][][][      m1,m2,Animal.type1       ][][][Jimmy][Dog --> Cat][][][][     Dog     ][][][ Dog --> mouse][]
            animal(name,type,type1)          m1      m2                Animal.type        Animal.type1
This is as per python's principle of saving memory. 
The same thing happens when we have 2 variables with same value

if i=10, j=10, k=20
[][][][ 10 ][][][20][][]
       i,j        k

Now if we change j
j=15
[][][10][15][][][20][][]
      i   j      k
"""

animal.legs = 4
print( animal.legs) #4
# print(Animal.legs) # Error because the class does not have this value
Animal.legs = 3
print(Animal.legs) #3

Animal.tail = 1
print(animal.tail) #1 
# Since we have already created this on class level, it can be used on Object level
# use https://www.programiz.com/python-programming/online-compiler/ to visualize

