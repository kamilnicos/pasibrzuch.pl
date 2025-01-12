import psycopg2
from config import DB_CONFIG


# Połączenie z bazą danych PostgreSQL
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Kwerendy SQL do tworzenia tabel
create_table_queries = [
    """
    INSERT INTO uzytkownicy (imie, nazwisko, email, nr_tel, haslo, id_dostawcy, id_restauracji, id_typ_uprawnien)
        VALUES
        ('Jan', 'Kowalski', 'jan@kowalski.pl', '123456789', 'haslo', NULL, NULL, 1),
        ('Adam', 'Nowak', 'adam@nowak.pl', '987654321', 'haslo', 1, NULL, 3),
        ('Jacek', 'Kowalski', 'jacek@kowalski.pl', '111111112', 'haslo', 2, NULL, 3),
        ('Adam', 'Nowy', 'adam@nowy.pl', '111111113', 'haslo', NULL, 1, 2),
        ('Piotr', 'Tama', 'piotr@tama.pl', '111111114', 'haslo', NULL, 2, 2);
    """,
    """
    INSERT INTO uprawnienia (id_typ_uprawnien, typ_uprawnienia)
        VALUES
        (1, 'klient'),
        (2, 'restauracja'),
        (3, 'dostawca');
    """,
    """
    INSERT INTO restauracje (id_restauracji, nazwa_restauracji)
        VALUES
        (1, 'Pizza Hut'),
        (2, 'McDonald'),
        (3, 'KFC'),
        (4, 'Burger King'),
        (5, 'Restauracja u Babci'),
        (6, 'Sushi Time'),
        (7, 'Kawiarnia Pod Platanem'),
        (8, 'Bar Mleczny');
    """,
    """
    INSERT INTO menu (rodzaj_kuchni, nazwa_dania, opis_dania, cena, dostepnosc, id_restauracji)
        VALUES
        ('włoska', 'Margherita', 'Pizza z sosem pomidorowym i mozzarellą', 15.99, true, 1),
        ('włoska', 'Pepperoni', 'Pizza z pepperoni', 17.99, true, 1),
        ('amerykańska', 'Cheeseburger', 'Burger z serem', 12.99, true, 2),
        ('amerykańska', 'Frytki', 'Porcja frytek', 5.99, true, 2),
        ('chińska', 'Kaczka po pekińsku', 'Tradycyjne danie chińskie', 25.99, true, 3),
        ('japońska', 'Sushi', 'Zestaw sushi z różnymi rodzajami ryb', 20.99, true, 6),
        ('polska', 'Kotlet schabowy', 'Kotlet schabowy z ziemniakami i surówką', 18.99, true, 8),
        ('kawa', 'Latte', 'Kawa z mlekiem', 8.99, true, 7);
    """,
    """
    INSERT INTO status_zamowienia (id_status_zamowienia, opis)
        VALUES
        (1, 'Zamówione'),
        (2, 'W przygotowaniu'),
        (3, 'Gotowe'),
        (4, 'W doręczeniu'),
        (5, 'Dostarczone');
    """,
    """
    INSERT INTO metody_platnosci (nazwa_platnosci)
        VALUES
        ('Blik'),
        ('Karta płatnicza'),
        ('Przelew bankowy');
    """,
    """
    INSERT INTO adresy (ulica, numer_budynku, kod_pocztowy, miasto, id_uzytkownika, id_restauracji)
        VALUES
        ('Główna', 12, '00-001', 'Warszawa', 1, NULL),
        ('Królewska', 78, '12-345', 'Kraków', 2, NULL),
        ('Gdyńska', 71, '54-234', 'Bytom', NULL, 1),
        ('Kolorowa', 43, '12-111', 'Wałbrzych', NULL, 2),
        ('Psina', 89, '65-645', 'Wrocław', NULL, 3),
        ('Armii Krajowej', 6, '12-345', 'Cieszynek', NULL, 4),
        ('Wolna', 10, '56-687', 'Poznań', NULL, 5),
        ('Szybka', 30, '12-568', 'Kraków', NULL, 6),
        ('Małą', 21, '34-435', 'Warszawa', NULL, 7),
        ('Duża', 24, '76-543', 'Kraków', NULL, 8);
    """,
    """
    INSERT INTO zamowienia (id_uzytkownika, id_restauracji, id_dostawcy, id_adres_dostawy, id_adres_odbioru, 
    id_status_zamowienia, id_data_zamowienia, lista_zamowienia, laczna_cena, id_metody_platnosci, ocena)
        VALUES
        (1, 1, 1, 1, 3, 1, 1, 4, 28.98, 1, 5),
        (2, 3, 1, 2, 4, 1, 2, 3, 33.97, 2, 4);
""",
]

# Wykonanie wszystkich kwerend tworzenia tabel
try:
    connection = get_db_connection()
    cursor = connection.cursor()
    for query in create_table_queries:
        cursor.execute(query)
        connection.commit()
    print("Wypelniono danymi.")
except Exception as e:
    print(f"Błąd podczas wypelniania tabel: {e}")
    connection.rollback()
finally:
    cursor.close()
    connection.close()
