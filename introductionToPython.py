##### Strings #####
pattern = "*"
print(pattern * 10)

course1 = "Python for 'Beginners'"
course2 = 'Python for "Beginners"'
print(course1)
print(course2)
print(course1[0]) # returns the first character 
print(course1[1]) # returns the second character 
print(course1[-1]) # returns the first character from the end  
print(course1[-2]) # returns the second character from the end
print(course1[3:10])
print(course1[:10])
print(course1[3:])
print(course1[-6:10])
print(course1.upper())
print(course1.lower())
print(course1.find('B'))
print(course1.title())
print(course2.replace('"', "'"))
print(course2.replace('B', "P"))
print("course2 = " + course2)
print("Python" in course1)

name = input("Enter your name : ")
age =  int(input("Enter your age : "))
Annual_CTC = int(input("Enter your Annual CTC : "))
netSalary = Annual_CTC * 0.75/12
Intro = f"Hi {name}, \n\n\tHow are you? \n\tYour age is {age}. \n\tYour net monthly Salary is {netSalary} \n\nRegards, \nAnonymous "
print(Intro)

##### If...elif...else #####
print("\n\n*** if statement ***\n")
name = "Abhinav likes Python"
contains = "Python" in name
if contains:
    print("contains")
elif not contains and True:
    print("not contains")
else:
    print("else")

##### Loop #####
print("\n\n*** while loop ***\n")
i = 1;
while i <= 5:
    print("i = " + str(i))
    i = i + 1

print("\n\n*** for loop1 ***\n")
for x in range(1, 5, 2):
    print(x)

print("\n\n*** for loop2 ***\n")
for x in range(1, 5):
    print(x)

print("\n\n*** for loop3 ***\n")
for x in range(5):
    print(x)

##### List #####
print("\n\n*** Lists ***\n")
numbers = [1, 6, 3, 2, 5, 7, 8, 6, 6, 5, 7, 8, 7]
numbers.append(11)
numbers.append(13)
numbers.append(15)
numbers.append(17)
numbers.append(19)
numbers.insert(0, -1)
numbers.insert(0, -2)
numbers.insert(0, -2)
numbers.insert(0, -1)
numbers.insert(0, -3)
print(numbers)
numbers.remove(7)
print(numbers)
print(numbers.index(6))
numbers.reverse()
print(numbers)
numbers.sort()
print(numbers)
print(numbers.index(6))
numcpy = numbers
print(numcpy)
numcopy = numbers.copy()
print(numcopy)

##### Tuples #####
print("\n\n*** Tuples ***\n")
coordinates = (1, 2, 3)
x, y, z = coordinates
print(x)
print(numbers.index(2))
print(coordinates)
coordinatescopy = coordinates
print(coordinatescopy)

##### Dictionary #####
print("\n\n*** Dictionary ***\n")
customer = {
    "myName": "Abhinav",
    "age": 30,
    "isVerified": True
}
print(customer["myName"])
customer["myName"] = "New Abhinav"
print(customer["myName"])
print(customer["age"])
print(customer)


##### Functions #####
print("\n\n*** Functions ***\n")


# positional arguments
def greet_user(name):
    print(f"Hi {name}")


greet_user("Abhinav")


# Two positional arguments 
def function1(name1, name2):
    print(name1)
    print(name2)


function1("Abhinav", "Cisco")


# Our functions can return values. If we don’t use the return statement, by default None is returned.
# None is an object that represents the absence of a value.

# Keyword arguments
def totalCost(order=500, shipping=100, tax=50):
    return order + shipping + tax


total1 = totalCost(100, 50, 10)
print(total1)

total2 = totalCost()
print(total2)


def square(number):
    return number * number


result = square(2)
print(result)  # prints 4 

##### Exceptions #####
print("\n\n*** Exceptions ***\n")
try:
    my_age = int(input("Enter your age : "))
    income = 20000
    risk = income / my_age
    print(my_age)
except ValueError:
    print("Not a valid number")
except ZeroDivisionError:
    print("Age cannot be Zero")

##### OOP - Classes & Objects #####
print("\n\n*** Classes & Objects ***\n")
class Car:
    def __init__(self, cost, color):
        self.cost = cost
        self.color = color

    def printCost(self):
        print(self.cost)

    def printColor(self):
        print(self.color)


car1 = Car(10000, "Red")
car2 = Car(20000, "White")
car3 = Car(30000, "Black")
car1.printCost()
car1.printColor()
car2.printCost()
car2.printColor()
car3.printCost()
car3.printColor()


class Vehicle_Two_Wheeler:
    def __init__(self, isNew):
        print("Hi, This is a Two wheeler Vehicle Class")
        self.isNew = isNew

    def checkNew(self):
        print(self.isNew)


class Bike(Vehicle_Two_Wheeler):
    def __init__(self, company):
        super(Bike, self).__init__("True")
        print("Hi, This is a Bike Class")
        self.company = company

    def getCompanyName(self):
        print(self.company)


class Modal(Bike):
    def __init__(self, modal, power, color):
        super(Modal, self).__init__("Bajaj")
        print("Hi, This is a Modal Class")
        self.modal = modal
        self.power = power
        self.color = color

    def getDetails(self):
        print(self.modal)
        print(self.power)
        print(self.color)


modal1 = Modal("Bajaj Pulsar", "220cc", "Red")
modal2 = Modal("Apache 4V", "160cc", "Grey")
modal3 = Modal("Aprilia", "150cc", "White")
modal4 = Modal("Honda Hunk", "180cc", "Black")
modal1.checkNew()
modal1.getCompanyName()
modal1.getDetails()
modal2.checkNew()
modal2.getCompanyName()
modal2.getDetails()
modal3.checkNew()
modal3.getCompanyName()
modal3.getDetails()
modal4.checkNew()
modal4.getCompanyName()
modal4.getDetails()


class Mammal:
    def walk(self):
        print("Walk")


class Dog(Mammal):
    def bark(self):
        print("Bark")


dog = Dog()
dog.walk()  # inherited from Mammal  dog.bark() # defined in Dog


##### Standard Library & Modules #####
import random
print(random.random())
print(random.randint(1, 6))
members = ["Abhinav", "Aayush", "Shubham"]
print(members)
leader = random.choice(members)
print(leader)
