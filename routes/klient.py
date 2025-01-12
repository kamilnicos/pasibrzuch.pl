from flask import Blueprint, render_template, request, session, redirect, url_for
from config import DB_CONFIG
import psycopg2
import psycopg2.extras
from datetime import datetime

klient_bp = Blueprint('klient', __name__)

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@klient_bp.route('/dashboard')
def dashboard():
    return render_template('klient/dashboard.html')

@klient_bp.route('/moje_zamowienia')
def moje_zamowienia():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
        SELECT restauracje.nazwa_restauracji, adresy.ulica, adresy.numer_budynku, adresy.kod_pocztowy, adresy.miasto, status_zamowienia.opis, data_zmiany_statusu.data_zlozenia_zamowienia
        FROM zamowienia
        JOIN restauracje ON zamowienia.id_restauracji = restauracje.id_restauracji
        JOIN status_zamowienia ON zamowienia.id_status_zamowienia = status_zamowienia.id_status_zamowienia
        JOIN data_zmiany_statusu ON zamowienia.id_data_zamowienia = data_zmiany_statusu.id_data_zamowienia
        JOIN adresy ON zamowienia.id_adres_dostawy = adresy.id_adresu
        WHERE zamowienia.id_uzytkownika = %s
        ORDER BY zamowienia.id_data_zamowienia DESC
    """, (session['user_id'],))
    zamowienia = cursor.fetchall()
    conn.close()
    return render_template('klient/moje_zamowienia.html', zamowienia=zamowienia)


@klient_bp.route('/restauracje', methods=['GET', 'POST'])
def przeglad_restauracji():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        rodzaj_kuch = request.form['rodzaj_kuchni']
        print(rodzaj_kuch)
        cursor.execute("""SELECT DISTINCT m.rodzaj_kuchni, r.nazwa_restauracji, r.id_restauracji
            FROM menu m
            INNER JOIN restauracje r ON m.id_restauracji = r.id_restauracji
            WHERE m.rodzaj_kuchni = %s
            ORDER BY m.rodzaj_kuchni;""", (rodzaj_kuch,))
        filtrowane_restauracje = cursor.fetchall()
        print(filtrowane_restauracje)
        conn.close()
        return render_template('klient/restauracje.html', restauracje=filtrowane_restauracje)

    cursor.execute("""SELECT DISTINCT m.rodzaj_kuchni, r.nazwa_restauracji, r.id_restauracji
        FROM menu m
        INNER JOIN restauracje r ON m.id_restauracji = r.id_restauracji
        ORDER BY m.rodzaj_kuchni;
        """)
    restauracje = cursor.fetchall()
    print("pusto ")
    # rodzaj_kuch = None
    conn.close()
    return render_template('klient/restauracje.html', restauracje=restauracje)


@klient_bp.route('/zamowienie/<int:restauracja_id>', methods=['GET', 'POST'])
def zamowienie(restauracja_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        print(request.form)
        dania = request.form.getlist('dania')
        adres_klienta = request.form['adresy']
        print(adres_klienta)
        print("dania: ", dania)

        # Obliczanie łącznej ceny i adresu restauracji - musi być group by, bo użyta jest funkcja agregująca SUM()
        cursor.execute("""
            SELECT SUM(cena), restauracje.id_restauracji FROM menu 
            JOIN restauracje ON restauracje.id_restauracji = menu.id_restauracji 
            WHERE id_menu IN %s
            GROUP BY restauracje.id_restauracji
        """, (tuple(dania),))
        razem = cursor.fetchone()
        laczna_cena = razem[0]
        adres_restauracji = razem[1]
        # print(laczna_cena, adres_restauracji)
        # print("razem",razem)

        cursor.execute("""SELECT id_status_zamowienia FROM status_zamowienia WHERE opis = %s ;
        """, ('Zamówione',))
        status_id = cursor.fetchone()[0]

        # data zamówienia
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""INSERT INTO data_zmiany_statusu (data_Zlozenia_zamowienia) VALUES (%s) RETURNING id_data_zamowienia;""", (date,))
        data_zamowienia = cursor.fetchone()[0]

        dania_str = ','.join(str(x) for x in dania)

        payment_method = request.form['payment_method']
        cursor.execute("""SELECT id_metody_platnosci FROM metody_platnosci WHERE nazwa_platnosci = %s;""", (payment_method,))
        id_platnosci = cursor.fetchone()[0]

        # Dodanie zamówienia
        cursor.execute("""
            INSERT INTO zamowienia (id_uzytkownika, id_restauracji, id_status_zamowienia, id_adres_dostawy, id_adres_odbioru, id_data_zamowienia, laczna_cena, lista_zamowienia, id_metody_platnosci)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], restauracja_id, status_id, adres_klienta, adres_restauracji, data_zamowienia, laczna_cena, dania_str, id_platnosci))
        # zamowienie_id = cursor.fetchone()[0]
        conn.commit()
        return redirect(url_for('klient.moje_zamowienia'))
    else:
        # conn = get_db_connection()
        # cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT rodzaj_kuchni, nazwa_dania, opis_dania, cena, id_menu FROM menu WHERE id_restauracji = %s AND dostepnosc = TRUE
        """, (restauracja_id,))
        menu = cursor.fetchall()

        cursor.execute("""
            SELECT id_adresu, ulica, numer_budynku, kod_pocztowy, miasto FROM adresy WHERE id_uzytkownika = %s;
        """, (session['user_id'],))
        adresy = cursor.fetchall()
        print(adresy)
        print(session['user_id'])

        conn.close()
        return render_template('klient/zamowienie.html', menu=menu, adresy=adresy)

@klient_bp.route('/adresy', methods=['GET', 'POST'])
def dodaj_adres():
    if request.method == 'POST':
        ulica = request.form['ulica']
        numer_budynku = request.form['numer_budynku']
        kod_pocztowy = request.form['kod_pocztowy']
        miasto = request.form['miasto']

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            INSERT INTO adresy (id_uzytkownika, id_restauracji, ulica, numer_budynku, kod_pocztowy, miasto)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session['user_id'], None, ulica, numer_budynku, kod_pocztowy, miasto))
        conn.commit()
        conn.close()
    return render_template('klient/adresy.html')
