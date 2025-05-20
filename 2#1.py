import sqlite3

class Student:
    def __init__(self, name, surname, patronymic, group, grades):
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.group = group

        if len(grades) != 4:
            raise ValueError("Должно быть 4 оценки")
        self.grades = grades

    def average_grade(self):
        return sum(self.grades) / len(self.grades)

class StudentDB:
    def __init__(self, db_name="students.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = """CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    patronymic TEXT,
                    group_name TEXT NOT NULL,
                    grades TEXT NOT NULL);"""
        self.conn.execute(query)
        self.conn.commit()

    def add_student(self, student):
        grades_str = ','.join(map(str, student.grades))
        query = """INSERT INTO students 
                   (name, surname, patronymic, group_name, grades)
                   VALUES (?, ?, ?, ?, ?)"""
        cur = self.conn.cursor()
        cur.execute(query, (student.name,
                            student.surname,
                            student.patronymic,
                            student.group,
                            grades_str))
        self.conn.commit()
        return cur.lastrowid

    def get_all_students(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM students")
        return cur.fetchall()

    def get_student(self, student_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM students WHERE id=?", (student_id,))
        return cur.fetchone()

    def update_student(self, student_id, student):
        grades_str = ','.join(map(str, student.grades))
        query = """UPDATE students SET
                   name = ?,
                   surname = ?,
                   patronymic = ?,
                   group_name = ?,
                   grades = ?
                   WHERE id = ?"""
        cur = self.conn.cursor()
        cur.execute(query, (student.name,
                            student.surname,
                            student.patronymic,
                            student.group,
                            grades_str,
                            student_id))
        self.conn.commit()

    def delete_student(self, student_id):
        query = "DELETE FROM students WHERE id=?"
        cur = self.conn.cursor()
        cur.execute(query, (student_id,))
        self.conn.commit()

    def get_group_average(self, group_name):
        cur = self.conn.cursor()
        cur.execute("SELECT grades FROM students WHERE group_name=?", (group_name,))
        records = cur.fetchall()

        if not records:
            return 0

        total = 0
        count = 0
        for record in records:
            grades = list(map(int, record[0].split(',')))
            total += sum(grades)
            count += len(grades)

        return total / count if count != 0 else 0

    def get_all_groups(self):
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT group_name FROM students")
        return [row[0] for row in cur.fetchall()]

def print_menu():
    print("\n1. Добавить нового студента")
    print("2. Просмотреть всех добавленных студентов")
    print("3. Просмотр студента по номеру")
    print("4. Редактировать студента")
    print("5. Удалить студента")
    print("6. Средний балл группы")
    print("0. Выход")

def main():
    db = StudentDB()

    while True:
        print_menu()
        choice = input("Выберите действие: ")

        if choice == "1":
            name = input("Имя: ")
            surname = input("Фамилия: ")
            patron = input("Отчество: ")
            group = input("Группа: ")
            grades = list(map(int, input("4 оценки через пробел: ").split()))

            student = Student(name, surname, patron, group, grades)
            db.add_student(student)
            print("Студент успешно добавлен!")

        elif choice == "2":
            students = db.get_all_students()
            print("\nСписок студентов:")
            for student in students:
                print(f"{student[0]}. {student[2]} {student[1]} {student[3]} - {student[4]}")

        elif choice == "3":
            print("\nСписок всех студентов:")
            students = db.get_all_students()
            for student in students:
                print(f"{student[0]}. {student[2]} {student[1]} {student[3]} - Группа: {student[4]}")

            student_id = int(input("\nВведите номер студента из списка: "))
            student = db.get_student(student_id)
            if student:
                grades = list(map(int, student[5].split(',')))
                avg = sum(grades) / len(grades)
                print(f"\nПодробная информация:")
                print(f"Номер: {student[0]}")
                print(f"ФИО: {student[2]} {student[1]} {student[3]}")
                print(f"Группа: {student[4]}")
                print(f"Оценки: {grades}")
                print(f"Средний балл: {avg:.2f}")
            else:
                print("Студент не найден")

        elif choice == "4":
            student_id = int(input("Введите номер студента для редактирования: "))
            name = input("Новое имя: ")
            surname = input("Новая фамилия: ")
            patron = input("Новое отчество: ")
            group = input("Новая группа: ")
            grades = list(map(int, input("Новые оценки через пробел: ").split()))

            student = Student(name, surname, patron, group, grades)
            db.update_student(student_id, student)
            print("Данные студента обновлены!")

        elif choice == "5":
            print("\nСписок всех студентов:")
            students = db.get_all_students()
            if not students:
                print("Нет студентов в базе")
                continue

            for student in students:
                print(f"{student[0]}. {student[2]} {student[1]} {student[3]} - Группа: {student[4]}")

            student_id = int(input("\nВведите номер студента для удаления: "))
            if db.get_student(student_id):
                db.delete_student(student_id)
                print("Студент успешно удален")
            else:
                print("Студент с таким номером не найден")

        elif choice == "6":
            groups = db.get_all_groups()
            if not groups:
                print("\nВ базе нет ни одной группы")
                continue

            print("\nДоступные группы:")
            for group in groups:
                print(f"- {group}")

            group = input("\nВведите группу из списка: ")
            average = db.get_group_average(group)

            if group not in groups:
                print("Такой группы не существует")
            else:
                print(f"\nСредний балл группы {group}: {average:.2f}")

        elif choice == "0":
            db.conn.close()
            print("Работа завершена")
            break

        else:
            print("Некорректный выбор")

if __name__ == "__main__":
    main()