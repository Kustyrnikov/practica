class Student:
    def __init__(self, surname, birth_date, group_number, progress):
        self.surname = surname
        self.birth_date = birth_date
        self.group_number = group_number
        self.progress = progress

    def info(self):
        print(f"{self.surname} {self.birth_date} {self.group_number} {', '.join(map(str, self.progress))}")

if __name__ == "__main__":
    student1 = Student("Огурцов", "31.01.2008", "434", [4, 5, 3, 4, 3])
    student1.info()
    student2 = Student("Петрушкин", "11.05.2006", "638", [3, 4, 2, 5, 3])

    student2.surname = "Сидоров"
    student2.birth_date = "05.06.2005"
    student2.group_number = "643"
    student2.info()

    search_surname = input("Введите фамилию для вывода информации: ")
    search_date = input("Введите дату рождения (ДД.ММ.ГГГГ): ")

    found = None
    for student in [student1, student2]:
        if student.surname == search_surname and student.birth_date == search_date:
            found = student
            break

    if found:
        print("\nИнформация о студенте:")
        found.info()
    else:
        print("\nСтудент не найден.")