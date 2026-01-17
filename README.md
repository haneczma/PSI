# Ćwiczenie pierwsze

## Układ plików

W katalogu cw1 znajduje się rozwiazanie zadania Z 1.1.

W katalogu client znajduje sie konfiguracja dla kontenera klienta w dockerze oraz program w C realizujacy część zadania 1 (klient UDP).

W katalogu serwer znajduje sie konfiguracja dla kontenera serwera w dockerze oraz program w pythonie realizujacy część zadania 1 (serwer UDP).

## Wywołanie rozwiazania

Skrypt app1.sh służy do zbudowania i włączenia klienta oraz serwera.
Należy mu nadać odpowiednie pozwolenia (chmod +x), a następnie wywołać z poziomu katalogu cw1.

# Ćwiczenie drugie

## Układ plików

W katalogu cw2 znajduje się rozwiazanie zadania Z 2.

W katalogu client znajduje sie konfiguracja dla kontenera klienta w dockerze oraz program w C realizujacy część zadania 1 (klient TCP).

W katalogu serwer znajduje sie konfiguracja dla kontenera serwera w dockerze oraz program w pythonie realizujacy część zadania 2 (serwer TCP).

## Wywołanie rozwiazania

Skrypt app2.sh służy do zbudowania i włączenia klienta oraz serwera.
Należy mu nadać odpowiednie pozwolenia (chmod +x), a następnie wywołać z poziomu katalogu cw2.

# Ćwiczenie trzecie

## Układ plików

W katalogu cw3 znajduje się rozwiazanie zadania Z1.22.

W katalogu client znajduje sie konfiguracja dla kontenera klienta w dockerze oraz program w pythonie realizujacy część zadania 1 (klient UDP).

W katalogu serwer znajduje sie konfiguracja dla kontenera serwera w dockerze oraz programy w c realizujace część zadania 2 (serwer UDP).

## Wywołanie rozwiazania

Skrypt app3-compose.sh służy do zbudowania i włączenia klienta oraz serwera.
Należy mu nadać odpowiednie pozwolenia (chmod +x), a następnie wywołać z poziomu katalogu cw3.

# Projekt

## Układ plików

W katalogu projekt znajduje się implementacja projektu.

W katalogu klient znajduje się konfiguracja dla kontenera klienta w dockerze i program w pythonie.

W katalogu serwer znajduje się konfiguracja dla kontenera serwera w dockerze, skrypt w bashu, który służy jako endpoint w dockerze i program w pythonie.

## Wywołanie rozwiazania

Skrypt app4.sh pozwala na proste przetestowanie połączenia jedynie ze strony klienta, jednak dla większej interaktywności programu najlepiej otworzyć kilka terminali. Należy mu nadać odpowiednie pozwolenia (chmod +x), a następnie wywołać z poziomu katalogu projekt.

### Wywołanie serwera

docker-compose up server

### Połączenie z terminalem serwera

docker-compose attach server

### Wywołanie klienta

docker-compose run client
