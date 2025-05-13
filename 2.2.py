class Train:
    def __init__(self, destination, number, departure_time):
        self.destination = destination
        self.number = number
        self.departure_time = departure_time

    def info(self):
        print(f"{self.number} {self.destination} {self.departure_time}")

trains = [
    Train("Москва", "100500", "13:30"),
    Train("Новосибирск", "234048", "17:20"),
    Train("Томск", "634045", "04:30")
]

print("Список поездов:")
for i in trains:
    i.info()

search = input("Введите номер поезда: ")
found = None

for i in trains:
    if i.number == search:
        found = i
        break

if found:
    print("\nИнформация о поезде:")
    found.info()
else:
    print("\nПоезд с таким номером не найден")