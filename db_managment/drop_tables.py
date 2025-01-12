import psycopg2
from config import DB_CONFIG


# Połączenie z bazą danych PostgreSQL
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

try:
    connection = get_db_connection()
    cursor = connection.cursor()
    query = """DROP TABLE IF EXISTS uzytkownicy, adresy, uprawnienia, data_zmiany_statusu, 
    menu, metody_platnosci, restauracje, status_zamowienia, zamowienia CASCADE;"""
    cursor.execute(query)
    connection.commit()
    print("Tabele zostały pomyślnie usuniete.")
except Exception as e:
    print(f"Błąd podczas tworzenia tabel: {e}")
    connection.rollback()
finally:
    cursor.close()
    connection.close()
