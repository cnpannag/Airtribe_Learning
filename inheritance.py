from typing_extensions import override

class Animal:
    def __init__(self, color, name):
        self.name = name
        self.color = color

    def get_name(self):
        print("parent function")
        return self.name

# Inheritance, similar to 'extends' in Java
class Dog(Animal):
    def __init__(self, color, name):
        self.no_of_legs = 4
        super().__init__(color, name)  # Adding this means you dont need a separate child constructor, you are directly using the parent constructor
    # All the variables in parent dont need to be recreated here like self.color = color and self.name = name

    @override  # Best practice, NOT REQUIRED
    def get_name(self) -> str:  #-> str Best practice, NOT REQUIRED
        super().get_name() #Run parent function before overriding with child function
        print("child function")  # Function Overriding
        return self.name


animal = Animal("brown", "parent jimmy")
print(animal.color)


dog = Dog("brown", "child jimmy")
print(dog.no_of_legs)  # works without super
print(dog.color)       # requires super().__init__(...)
# 4
# brown

print(animal.get_name())
# parent function
# parent jimmy

print(dog.get_name())
# parent function
# child function
# child jimmy


# when we are inside a class and we want to refer to a non static member we use "self"
# when we are inside a class and we want to refer to a non static member of PARENT class we use "super"

