import psycopg2

from config import DB_CONFIG


# Połączenie z bazą danych PostgreSQL
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Kwerendy SQL do ustawiania kluczy obcych
set_foreign_keys_queries = [
    """
    ALTER TABLE uprawnienia
    ADD CONSTRAINT fk_uprawnienia_uzytkownicy
    FOREIGN KEY (id_typ_uprawnien) REFERENCES uzytkownicy(id_typ_uprawnien)
    ON DELETE SET NULL ON UPDATE CASCADE;
    """,
    """
    ALTER TABLE uzytkownicy
    ADD CONSTRAINT fk_uzytkownicy_restauracje
    FOREIGN KEY (id_restauracji) REFERENCES restauracje(id_restauracji)
    ON DELETE SET NULL ON UPDATE CASCADE;
    """,
    """
    ALTER TABLE adresy
    ADD CONSTRAINT fk_adresy_uzytkownicy
    FOREIGN KEY (id_uzytkownika) REFERENCES uzytkownicy(id_uzytkownika)
    ON DELETE CASCADE ON UPDATE CASCADE;
    """,
    """
    ALTER TABLE adresy
    ADD CONSTRAINT fk_adresy_restauracje
    FOREIGN KEY (id_restauracji) REFERENCES restauracje(id_restauracji)
    ON DELETE CASCADE ON UPDATE CASCADE;
    """,
    """
    ALTER TABLE zamowienia
    ADD CONSTRAINT fk_zamowienia_uzytkownicy
    FOREIGN KEY (id_uzytkownika) REFERENCES uzytkownicy(id_uzytkownika)
    ON DELETE CASCADE ON UPDATE CASCADE;
    """,
    """
    ALTER TABLE zamowienia
    ADD CONSTRAINT fk_zamowienia_restauracje
    FOREIGN KEY (id_restauracji) REFERENCES restauracje(id_restauracji)
    ON DELETE CASCADE ON UPDATE CASCADE;
    """,
    """
    ALTER TABLE zamowienia
    ADD CONSTRAINT fk_zamowienia_dostawcy
    FOREIGN KEY (id_dostawcy) REFERENCES uzytkownicy(id_dostawcy)
    ON DELETE SET NULL ON UPDATE CASCADE;
    """,
    """
    ALTER TABLE zamowienia
    ADD CONSTRAINT fk_zamowienia_status
    FOREIGN KEY (id_status_zamowienia) REFERENCES status_zamowienia(id_status_zamowienia)
    ON DELETE SET NULL ON UPDATE CASCADE;
    """,
    """
    ALTER TABLE zamowienia
    ADD CONSTRAINT fk_zamowienia_platnosci
    FOREIGN KEY (id_metody_platnosci) REFERENCES metody_platnosci(id_metody_platnosci)
    ON DELETE SET NULL ON UPDATE CASCADE;
    """,
    """
    ALTER TABLE zamowienia
    ADD CONSTRAINT fk_zamowienia_data
    FOREIGN KEY (id_data_zamowienia) REFERENCES Data_zmiany_statusu(id_data_zamowienia)
    ON DELETE SET NULL ON UPDATE CASCADE;
    """,
    """
    ALTER TABLE menu
    ADD CONSTRAINT fk_menu_restauracje
    FOREIGN KEY (id_restauracji) REFERENCES restauracje(id_restauracji)
    ON DELETE CASCADE ON UPDATE CASCADE;
    """
]

# Wykonanie kwerend do ustawiania relacji
try:
    connection = get_db_connection()
    cursor = connection.cursor()
    for query in set_foreign_keys_queries:
        cursor.execute(query)
        connection.commit()
    print("Relacje zostały pomyślnie ustawione.")
except Exception as e:
    print(f"Błąd podczas ustawiania relacji: {e}")
    connection.rollback()
finally:
    cursor.close()
    connection.close()
