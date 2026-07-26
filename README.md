# Timefold-training

> **Status:** Repozytorium szkoleniowe z rozwijanym przypadkiem domenowym.

## Cel i rzeczywista zawartość

Zbiór zaczyna się od przykładów Timefold Solver, a następnie rozwija problem przydziału zadań kalibracyjnych do techników i stanowisk. Zawiera ograniczenia, modele domenowe, kolejne warianty kalibracji oraz narzędzia importu danych DBF/ODBC.

## Zakres potwierdzony w repozytorium

- przykłady hello world i knapsack
- wiele wersji domeny kalibracji z rosnącym zestawem ograniczeń
- moduł `rbh_solver` oraz narzędzia przygotowujące dane organizacyjne
- eksperymenty porównawcze z OR-Tools i RL

## Gdzie leży wartość merytoryczna

- konkretna adaptacja constraint solvera do realnego planowania laboratoryjnego
- kolejne wersje pokazują dojrzewanie modelu domeny i ograniczeń
- wartość leży w formalizacji konfliktów, kompetencji i zasobów, nie w samym użyciu biblioteki

## Ograniczenia rzetelnej oceny

- brak jednego wspieranego wariantu, diagramu danych i zestawu kryteriów akceptacji planu
- część danych i ścieżek jest związana z lokalnym systemem LOGIS
- brak benchmarku jakości harmonogramu, czasu rozwiązania i stabilności względem zmian wejścia

## Jak zweryfikować wartość projektu

- utworzyć mały publiczny lub syntetyczny przypadek referencyjny
- dla każdego constraintu opisać wagę, uzasadnienie i test naruszenia
- porównać wynik z planem ręcznym oraz prostą heurystyką zachłanną

## Uwagi

Opis sporządzono na podstawie plików obecnych na domyślnej gałęzi repozytorium. Nie zakłada on funkcji, wyników ani gotowości produkcyjnej, których nie da się potwierdzić z zawartości.

Obecność kodu lub danych nie oznacza automatycznie gotowości produkcyjnej, poprawności naukowej ani prawa do redystrybucji materiałów zewnętrznych. Licencję i pochodzenie danych należy oceniać na podstawie odpowiednich plików źródłowych oraz warunków ich dostawców.
