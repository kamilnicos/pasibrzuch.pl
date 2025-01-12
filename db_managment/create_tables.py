import psycopg2
from config import DB_CONFIG


# Połączenie z bazą danych PostgreSQL
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Kwerendy SQL do tworzenia tabel
create_table_queries = [
    """
    CREATE TABLE uprawnienia (
        id_typ_uprawnien SERIAL PRIMARY KEY,
        typ_uprawnienia TEXT NOT NULL 
    );
    """,
    """
    CREATE TABLE uzytkownicy (
        id_uzytkownika SERIAL PRIMARY KEY,
        id_restauracji INTEGER UNIQUE,
        id_dostawcy INTEGER UNIQUE,
        id_typ_uprawnien INTEGER NOT NULL,
        imie TEXT NOT NULL,
        nazwisko TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        nr_tel TEXT NOT NULL,
        haslo TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE restauracje (
        id_restauracji INTEGER PRIMARY KEY,
        nazwa_restauracji TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE adresy (
        id_adresu SERIAL PRIMARY KEY,
        id_uzytkownika INTEGER,
        id_restauracji INTEGER,
        ulica TEXT NOT NULL,
        numer_budynku INTEGER NOT NULL,
        kod_pocztowy TEXT NOT NULL,
        miasto TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE metody_platnosci (
        id_metody_platnosci SERIAL PRIMARY KEY,
        nazwa_platnosci TEXT NOT NULL
    );
    """,
    # pytanie czy statusy zamówienia nie mają być wartością Boolean
    """
    CREATE TABLE status_zamowienia (
        id_status_zamowienia SERIAL PRIMARY KEY,
        opis TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE zamowienia (
        id_zamowienia SERIAL PRIMARY KEY,
        id_uzytkownika INTEGER NOT NULL,
        id_restauracji INTEGER NOT NULL,
        id_dostawcy INTEGER,
        id_status_zamowienia INTEGER NOT NULL,
        id_data_zamowienia INTEGER NOT NULL,
        id_adres_dostawy INTEGER NOT NULL,
        id_adres_odbioru INTEGER NOT NULL,
        lista_zamowienia TEXT NOT NULL,
        laczna_cena FLOAT NOT NULL,
        id_metody_platnosci INTEGER NOT NULL,
        ocena INTEGER CHECK (ocena > 0 and ocena < 6)
    );
    """,
    """
    CREATE TABLE data_zmiany_statusu (
        id_data_zamowienia SERIAL PRIMARY KEY,
        data_zlozenia_zamowienia TIMESTAMP NOT NULL,
        data_przyjecia_zamowienia TIMESTAMP,
        data_gotowego_jedzenia TIMESTAMP,
        data_przyjecia_przez_kuriera TIMESTAMP,
        data_odebrania TIMESTAMP
    );
    """,
    """
    CREATE TABLE menu (
        id_menu SERIAL PRIMARY KEY,
        id_restauracji INTEGER NOT NULL,
        rodzaj_kuchni TEXT NOT NULL,
        nazwa_dania TEXT NOT NULL,
        opis_dania TEXT,
        cena FLOAT NOT NULL,
        dostepnosc BOOLEAN NOT NULL DEFAULT TRUE
    );
    """
]

# Wykonanie wszystkich kwerend tworzenia tabel
try:
    connection = get_db_connection()
    cursor = connection.cursor()
    for query in create_table_queries:
        cursor.execute(query)
        connection.commit()
    print("Tabele zostały pomyślnie utworzone.")
except Exception as e:
    print(f"Błąd podczas tworzenia tabel: {e}")
    connection.rollback()
finally:
    cursor.close()
    connection.close()
