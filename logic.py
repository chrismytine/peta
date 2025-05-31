import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.colors import is_color_like

class DB_Map():
    def __init__(self, database):
        self.database = database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS users_color (
                                user_id INTEGER PRIMARY KEY,
                                color TEXT
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                              FROM users_cities  
                              JOIN cities ON users_cities.city_id = cities.id
                              WHERE users_cities.user_id = ?''', (user_id,))
            return [row[0] for row in cursor.fetchall()]

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng FROM cities WHERE city = ?''', (city_name,))
            return cursor.fetchone()

    def set_user_color(self, user_id, color):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''INSERT INTO users_color (user_id, color)
                            VALUES (?, ?)
                            ON CONFLICT(user_id) DO UPDATE SET color = excluded.color''',
                         (user_id, color))
            conn.commit()

    def get_user_color(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT color FROM users_color WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 'red'  # Default warna merah

    def create_graph(self, path, cities, user_id):
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()
        marker_color = self.get_user_color(user_id)

        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates
                ax.plot(lng, lat, color=marker_color, marker='o', markersize=5, transform=ccrs.PlateCarree())
                plt.text(lng + 3, lat + 12, city, horizontalalignment='left', transform=ccrs.Geodetic())

        plt.savefig(path)
        plt.close()

    def draw_distance(self, city1, city2):
        # Menggambar garis antara dua kota untuk menampilkan jarak
        pass


if __name__ == "__main__":
    m = DB_Map("database.db")  # Membuat objek yang akan berinteraksi dengan database
    m.create_user_table()   # Membuat tabel dengan kota pengguna, jika tidak sudah ada
