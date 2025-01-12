from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_CONFIG
import psycopg2

auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        haslo = request.form['haslo']

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = ("""SELECT uzytkownicy.id_uzytkownika, uzytkownicy.email, uzytkownicy.haslo, uprawnienia.typ_uprawnienia
                 FROM uzytkownicy, uprawnienia 
                 WHERE uzytkownicy.email = %s AND uzytkownicy.haslo = %s 
                 AND uzytkownicy.id_typ_uprawnien = uprawnienia.id_typ_uprawnien;
                 """)
        cursor.execute(query, (email, haslo))
        user = cursor.fetchone()
        # query = "SELECT * FROM uprawnienia WHERE id_uzytkownika = %s"
        # cursor.execute(query, (user['id_uzytkownika']))

        # conn.close()

        if user:
            session['user_id'] = user['id_uzytkownika']
            session['user_role'] = user['typ_uprawnienia']  # Zapisanie roli użytkownika
            return redirect(url_for(f'{session["user_role"]}.dashboard'))
        else:
            return render_template('auth/login.html', error="Nieprawidłowe dane logowania")
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    print("wysłano")
    if request.method == 'POST':
        print("odebrano")
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        account_type = request.form['account_type']  # 'klient', 'restauracja', 'dostawca'
        name = request.form['name']
        telephone = request.form['telephone']
        surname = request.form['surname']
        restaurant_name = request.form['restauration_name']

        print("poczatek")

        print(email)
        print(password)
        print(confirm_password)
        print(confirm_password)
        print(account_type)
        print(name)
        print("koniec")


        if password != confirm_password:
            flash('Hasła nie pasują do siebie.', 'danger')
            print(password, confirm_password)
            return redirect(url_for('auth.register'))

        # hashed_password = generate_password_hash(password, method='sha256')
        hashed_password = password
        conn = get_db_connection()
        cursor = conn.cursor()
        print("account_type", account_type)

        # id_restau = None
        # id_dostaw = None
        # if account_type == "restauracja":
        #     cursor.execute("SELECT nextval('seq_restauracji')")
        #     id_restau = cursor.fetchone()[0]
        # elif account_type == "dostawca":
        #     cursor.execute("SELECT nextval('seq_dostawcow')")
        #     id_dostaw = cursor.fetchone()[0]

        # id_restau = None
        # id_dostaw = None
        # if account_type == "restauracja":
        #     cursor.execute("SELECT id_restauracji FROM restauracje WHERE ")
        #     id_restau = cursor.fetchone()[0]
        # elif account_type == "dostawca":
        #     cursor.execute("SELECT nextval('seq_dostawcow')")
        #     id_dostaw = cursor.fetchone()[0]

        # try:
        #
        if account_type == 'klient':
            print("awokado1")
            # typ_uprawnienia = 1
            cursor.execute("""
                INSERT INTO uzytkownicy (imie, nazwisko, email, nr_tel, haslo, id_dostawcy, id_restauracji, id_typ_uprawnien)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                (name, surname, email, telephone, password, None, None, 1))
            print("awokado2")
            # conn.commit()
        elif account_type == 'restauracja':
            cursor.execute("""SELECT id_restauracji FROM restauracje WHERE nazwa_restauracji = %s;""", (restaurant_name,))
            id_restau = cursor.fetchone()[0]
            print("id_restau ", id_restau)
            typ_uprawnienia = 2
            cursor.execute("""
                INSERT INTO uzytkownicy (imie, nazwisko, email, nr_tel, haslo, id_dostawcy, id_restauracji, id_typ_uprawnien)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                (name, surname, email, telephone, password, None, id_restau, 2))
            # if restaurant_name:
            #     cursor.execute("""
            #         INSERT INTO restauracje (nazwa_restauracji) VALUES (?)
            #     """, (restaurant_name,))
        elif account_type == 'dostawca':
            cursor.execute("""SELECT id_dostawcy FROM uzytkownicy 
                WHERE id_dostawcy IS NOT NULL ORDER BY id_dostawcy DESC LIMIT 1;""")
            id_dostaw = cursor.fetchone()[0]
            print("id_dostaw", id_dostaw)
            id_dostaw += 1
            print("id_dostaw", id_dostaw)
            typ_uprawnienia = 3
            cursor.execute("""
                INSERT INTO uzytkownicy (imie, nazwisko, email, nr_tel, haslo, id_dostawcy, id_restauracji, id_typ_uprawnien)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                (name, surname, email, telephone, password, id_dostaw, None, 3))
        print("brawo")
        conn.commit()
        # flash('Rejestracja zakończona sukcesem! Możesz się zalogować.', 'success')
        print("sukces")
        conn.close()
        return redirect(url_for('auth.login'))
        # except Exception as e:
        # print("nie udalo sie")
        # conn.rollback()
        # flash(f'Wystąpił błąd: {e}', 'danger')
        # finally:
    return render_template('auth/register.html')
