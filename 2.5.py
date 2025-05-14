class Class:
    def __init__(self, a=3, b=5):
        self.a = a
        self.b = b
        print(f"{a}, {b}")

    def __del__(self):
        print(f"Удалены: {self.a}, {self.b}")

object1 = Class()
object2 = Class(15, 22)

del object1
del object2