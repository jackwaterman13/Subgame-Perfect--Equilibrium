class MyClass:
    def __init__(self, itr):
        self.itr = itr

    def modify_itr(self):

        print("Inside the method:", self.itr + 1)

obj = MyClass(5)
print("Before method call:", obj.itr)
obj.modify_itr()
print("After method call:", obj.itr)
