import sqlite3
import psutil
from datetime import datetime


class SystemMonitor:
    def __init__(self, db_name='system_monitor.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = '''CREATE TABLE IF NOT EXISTS monitor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    cpu_usage REAL NOT NULL,
                    ram_usage REAL NOT NULL,
                    disk_usage REAL NOT NULL)'''
        self.conn.execute(query)
        self.conn.commit()

    def get_system_stats(self):
        cpu_percent = psutil.cpu_percent(interval=1)

        ram = psutil.virtual_memory()
        ram_percent = ram.percent

        disk = psutil.disk_usage('/')
        disk_percent = disk.percent

        return {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'cpu': cpu_percent,
            'ram': ram_percent,
            'disk': disk_percent
        }

    def save_to_db(self, data):
        query = '''INSERT INTO monitor_data 
                  (timestamp, cpu_usage, ram_usage, disk_usage)
                  VALUES (?, ?, ?, ?)'''
        self.conn.execute(query, (
            data['timestamp'],
            data['cpu'],
            data['ram'],
            data['disk']
        ))
        self.conn.commit()

    def view_history(self):
        print("\nИстория измерений:")
        print("{:<5} {:<20} {:<10} {:<10} {:<10}".format(
            "ID", "Время", "CPU (%)", "RAM (%)", "Disk (%)"
        ))

        cursor = self.conn.execute('''SELECT * FROM monitor_data 
                                    ORDER BY timestamp ASC LIMIT 20''')
        for row in cursor.fetchall():
            print("{:<5} {:<20} {:<10.1f} {:<10.1f} {:<10.1f}".format(
                row[0], row[1], row[2], row[3], row[4]
            ))

    def close(self):
        self.conn.close()


def main():
    monitor = SystemMonitor()

    while True:
        print("\nСистемный монитор:")
        print("1. Сделать замер показателей")
        print("2. Показать историю замеров")
        print("3. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            data = monitor.get_system_stats()
            monitor.save_to_db(data)
            print(f"\nЗамер сохранен: {data['timestamp']}")
            print(f"CPU: {data['cpu']}%")
            print(f"RAM: {data['ram']}%")
            print(f"Disk: {data['disk']}%")
        elif choice == '2':
            monitor.view_history()
        elif choice == '3':
            monitor.close()
            break
        else:
            print("Некорректный ввод!")


if __name__ == "__main__":
    main()