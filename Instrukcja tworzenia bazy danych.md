# Stworzenie bazy danych dla aplikacji Pasibrzuch.pl

Wszystko wykonuje się z poziomu użytkownika postgres.

1. Utworzyć użytkownika *admin*.
```postgresql
CREATE USER admin WITH PASSWORD 'admin123';
```
2. Utworzyć bazę danych.
```postgresql
CREATE DATABASE app_db;
```
3. Utworzyć grupę dla ról, którzy będą mieć uprawienia do bazy danych (na razie tylko administrator).
```postgresql
CREATE GROUP admins;
```
4. Zmienić uprawnienia dla utworzonej grupy administratorów.
```postgresql
REVOKE ALL ON DATABASE app_db FROM public;
GRANT CONNECT ON DATABASE app_db TO admins;

GRANT USAGE ON SCHEMA public TO admins;
```
5. Nadać uprawnienia do zmian wszystkich tabel dla grupy.
```postgresql
GRANT ALL ON ALL TABLES IN SCHEMA public TO admins;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO admins;
```
6. Dodać uprawnienia do tworzenia tabel dla grupy administratorów.

<!---
tutaj jeszcze może być inne polecenie, ale nie wiem
GRANT USAGE, CREATE ON SCHEMA public TO admins;    
-->

```postgresql
GRANT CREATE ON SCHEMA public TO admins;
```
7. Przypisanie stworzonego administratora do grupy z uprawnieniami administratorów.
```postgresql
GRANT admins TO admin;
```