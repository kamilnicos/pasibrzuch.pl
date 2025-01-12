from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from config import DB_CONFIG
import psycopg2
import psycopg2.extras

restauracja_bp = Blueprint('restauracja', __name__)

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@restauracja_bp.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""SELECT id_restauracji FROM uzytkownicy WHERE id_uzytkownika = %s""", (session['user_id'],))
    session['id_restauracji'] = cursor.fetchone()[0]
    return render_template('restauracja/dashboard.html')

@restauracja_bp.route('/menu', methods=['GET', 'POST'])
def zarzadzanie_menu():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""SELECT id_restauracji FROM uzytkownicy WHERE id_uzytkownika = %s""", (session['user_id'],))
    id_restaur = cursor.fetchone()[0]
    # Pobierz menu restauracji
    cursor.execute("""
        SELECT id_menu, nazwa_dania, rodzaj_kuchni, opis_dania, cena, dostepnosc FROM Menu WHERE id_restauracji = %s;
    """, (id_restaur,))
    menu = cursor.fetchall()

    # if request.method == 'POST':
    #     nazwa = request.form['nazwa']
    #     rodzaj = request.form['rodzaj']
    #     opis = request.form['opis']
    #     cena = request.form['cena']
    #     dostepnosc = request.form.get('dostepnosc')
    #     print("dostepnosc", dostepnosc)
    #     if dostepnosc != 'on':
    #         dostepnosc = 'off'
    #
    #     cursor.execute("""
    #         INSERT INTO menu (id_restauracji, rodzaj_kuchni, nazwa_dania, opis_dania, cena, dostepnosc)
    #         VALUES (%s, %s, %s, %s, %s, %s)
    #         ;
    #     """, (id_restaur, rodzaj, nazwa, opis, cena, dostepnosc))
    #     conn.commit()
    #     conn.close()
    #     return render_template('restauracja/menu.html', menu=menu)
    conn.close()
    return render_template('restauracja/menu.html', menu=menu)

@restauracja_bp.route('/dodaj_pozycje', methods=['GET', 'POST'])
def dodaj_pozycje():
    if request.method == 'POST':
        nazwa = request.form['nazwa']
        rodzaj = request.form['rodzaj']
        opis = request.form['opis']
        cena = request.form['cena']
        dostepnosc = request.form.get('dostepnosc')
        print("dostepnosc", dostepnosc)
        if dostepnosc != 'on':
            dostepnosc = 'off'

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO menu (id_restauracji, rodzaj_kuchni, nazwa_dania, opis_dania, cena, dostepnosc) 
            VALUES (%s, %s, %s, %s, %s, %s) 
            ;
        """, (session['id_restauracji'], rodzaj, nazwa, opis, cena, dostepnosc))
        conn.commit()
        conn.close()
        return redirect(url_for('restauracja.zarzadzanie_menu'))
    return redirect(url_for('restauracja.zarzadzanie_menu'))

@restauracja_bp.route('/menu/edytuj/<int:id_menu>', methods=['GET', 'POST'])
def edytuj_pozycje(id_menu):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Pobierz dane pozycji do edycji
    cursor.execute("""
        SELECT * FROM Menu WHERE id_menu = %s AND id_restauracji = %s
    """, (id_menu, session['id_restauracji']))
    pozycja = cursor.fetchone()

    if not pozycja:
        conn.close()
        flash('Pozycja nie istnieje lub nie masz do niej dostępu.', 'danger')
        return redirect(url_for('restauracja.zarzadzanie_menu'))

    if request.method == 'POST':
        nazwa = request.form['nazwa']
        opis = request.form['opis']
        cena = request.form['cena']
        rodzaj_kuchni = request.form['rodzaj_kuchni']
        dostepnosc = request.form.get('dostepnosc') == 'on'

        cursor.execute("""
            UPDATE Menu
            SET nazwa_dania = %s, opis = %s, cena = %s, rodzaj_kuchni = %s, dostepnosc = %s
            WHERE id_menu = %s AND id_restauracji = %s
        """, (nazwa, opis, cena, rodzaj_kuchni, dostepnosc, id_menu, session['id_restauracji']))
        conn.commit()
        conn.close()

        flash('Zaktualizowano pozycję w menu!', 'success')
        return redirect(url_for('restauracja.zarzadzanie_menu'))

    conn.close()
    return render_template('restauracja/edytuj_pozycje.html', pozycja=pozycja)

@restauracja_bp.route('/usun_pozycje', methods=['GET','POST'])
def usun_pozycje():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Pobierz ID pozycji do usunięcia
    id_menu = request.form.get('id')  # Poprawione z "id_menu" na "id"

    if not id_menu:
        flash('Nie podano ID pozycji do usunięcia.', 'danger')
        return redirect(url_for('restauracja.zarzadzanie_menu'))

    # Usuń pozycję z menu
    cursor.execute("""
        DELETE FROM menu WHERE id_menu = %s AND id_restauracji = (SELECT id_restauracji FROM uzytkownicy WHERE id_uzytkownika = %s);
    """, (id_menu, session['user_id']))
    conn.commit()
    conn.close()

    flash('Usunięto pozycję z menu!', 'success')
    return redirect(url_for('restauracja.zarzadzanie_menu'))

@restauracja_bp.route('/zamowienia')
def zamowienia():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
        SELECT zamowienia.id_zamowienia, uzytkownicy.imie, uzytkownicy.nazwisko, adresy.ulica, adresy.numer_budynku, adresy.kod_pocztowy, adresy.miasto, status_zamowienia.opis, data_zmiany_statusu.data_zlozenia_zamowienia
        FROM zamowienia
        JOIN uzytkownicy ON zamowienia.id_uzytkownika = uzytkownicy.id_uzytkownika
        JOIN status_zamowienia ON zamowienia.id_status_zamowienia = status_zamowienia.id_status_zamowienia
        JOIN data_zmiany_statusu ON zamowienia.id_data_zamowienia = data_zmiany_statusu.id_data_zamowienia
        JOIN adresy ON zamowienia.id_adres_dostawy = adresy.id_adresu
        WHERE zamowienia.id_restauracji = %s
        ORDER BY zamowienia.id_data_zamowienia DESC
    """, (session['id_restauracji'],))
    zamowienia = cursor.fetchall()
    conn.close()
    return render_template('restauracja/zamowienia.html', zamowienia=zamowienia)

@restauracja_bp.route('/zamowienia/<int:zamowienie_id>/status', methods=['GET', 'POST'])
def aktualizuj_status_zamowienia(zamowienie_id):
    # print("awokado")
    if request.method == 'POST':
        # Pobranie nowego id_status_zamowienia z formularza
        id_status_zamowienia = request.form.get('id_status_zamowienia')
        # allowed_statuses = [1, 2, 3]
        print("id_status", id_status_zamowienia)

        id_status_zamowienia = int(id_status_zamowienia)


        # Połączenie z bazą danych i aktualizacja statusu
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE zamowienia
            SET id_status_zamowienia = %s
            WHERE id_zamowienia = %s
        """, (id_status_zamowienia, zamowienie_id))
        conn.commit()
        conn.close()
        return redirect(url_for('restauracja.zamowienia'))
    return redirect(url_for('restauracja.zamowienia'))


