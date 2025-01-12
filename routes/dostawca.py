from flask import Blueprint, render_template, request, session, redirect, url_for
from config import DB_CONFIG
import psycopg2
import psycopg2.extras

dostawca_bp = Blueprint('dostawca', __name__)

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@dostawca_bp.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""SELECT id_dostawcy FROM uzytkownicy WHERE id_uzytkownika = %s""", (session['user_id'],))
    session['id_dostawcy'] = cursor.fetchone()[0]
    return render_template('dostawca/dashboard.html')

@dostawca_bp.route('/zamowienia')
def zamowienia():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
        SELECT zamowienia.id_zamowienia, restauracje.nazwa_restauracji, uzytkownicy.imie, 
        uzytkownicy.nazwisko, 
        adres_dostawy.ulica AS ulica_dostawy,
        adres_dostawy.numer_budynku AS numer_budynku_dostawy,
        adres_dostawy.kod_pocztowy AS kod_pocztowy_dostawy,
        adres_dostawy.miasto AS miasto_dostawy,
        adres_odbioru.ulica AS ulica_odbioru,
        adres_odbioru.numer_budynku AS numer_budynku_odbioru,
        adres_odbioru.kod_pocztowy AS kod_pocztowy_odbioru,
        adres_odbioru.miasto AS miasto_odbioru,
        status_zamowienia.opis, data_zmiany_statusu.data_zlozenia_zamowienia
        FROM zamowienia
        JOIN restauracje ON zamowienia.id_restauracji = restauracje.id_restauracji
        JOIN uzytkownicy ON zamowienia.id_uzytkownika = uzytkownicy.id_uzytkownika
        JOIN status_zamowienia ON zamowienia.id_status_zamowienia = status_zamowienia.id_status_zamowienia
        JOIN data_zmiany_statusu ON zamowienia.id_data_zamowienia = data_zmiany_statusu.id_data_zamowienia
        JOIN adresy as adres_dostawy ON zamowienia.id_adres_dostawy = adres_dostawy.id_adresu
        JOIN adresy as adres_odbioru ON zamowienia.id_adres_odbioru = adres_odbioru.id_restauracji
        WHERE (zamowienia.id_status_zamowienia = 3 OR zamowienia.id_status_zamowienia = 4 OR zamowienia.id_status_zamowienia = 5)
        OR (zamowienia.id_dostawcy = %s OR zamowienia.id_dostawcy = %s)
        ORDER BY zamowienia.id_data_zamowienia DESC;
    """, (session['id_dostawcy'], None))
    zamowienia = cursor.fetchall()
    # print(zamowienia)
    # print(session['id_dostawcy'])
    conn.close()
    return render_template('dostawca/zamowienia.html', zamowienia=zamowienia)

@dostawca_bp.route('/zamowienia/<int:zamowienie_id>/akceptuj', methods=['POST'])
def akceptuj_zamowienie(zamowienie_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE zamowienia SET id_dostawcy = %s, id_status_zamowienia = 4 WHERE id_zamowienia = %s
    """, (session['id_dostawcy'], zamowienie_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dostawca.zamowienia'))

@dostawca_bp.route('/zamowienia/<int:zamowienie_id>/status', methods=['POST'])
def aktualizuj_status_zamowienia(zamowienie_id):
    status = request.form['status']
    print(status)
    conn = get_db_connection()
    cursor = conn.cursor()
    # cursor.execute("""
    #     SELECT status_zamowienia.id_status_zamowienia FROM status_zamowienia
    #     WHERE status_zamowienia.opis = %s
    # """, (status))
    # status_zamowienia = cursor.fetchone()

    cursor.execute("""
        UPDATE zamowienia SET id_status_zamowienia = %s WHERE id_zamowienia = %s
    """, (status, zamowienie_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dostawca.zamowienia'))
