# Create your models here.
from django.db import models
from django.db.models import Case, When, F, Value
from django.db.models.functions import Length
from django.db import models
from django.apps import apps
from django.db.models import OuterRef, Subquery
import pandas as pd
import re

class Osrodek_pr(models.Model):
    pr_id = models.CharField(max_length=10, unique=True)  # Main center ID
    pr_nazwa_p = models.CharField(max_length=62)  # Full name of the center
    pr_nazwa_s = models.CharField(max_length=12)  # Short name of the center
    pr_kod = models.CharField(max_length=6)  # Postal code
    pr_miasto = models.CharField(max_length=30)  # City
    pr_ulica = models.CharField(max_length=40)  # Street
    pr_fax = models.CharField(max_length=35)  # Fax number
    ind_rek = models.CharField(max_length=17)  # Record index
    ind_poczta = models.BooleanField()  # Boolean field (Post related)

    class Meta:
        ordering = ('pr_id',)

class Pers_st(models.Model):
    l_pesel = models.CharField(max_length=11, unique=True)  # PESEL number
    l_nazwisko = models.CharField(max_length=30)  # Last name
    l_imie = models.CharField(max_length=15)  # First name
    l_nazw_im = models.CharField(max_length=45)  # Full name (Last name + First name)
    l_login = models.CharField(max_length=45)  # Login ID
    sp_id = models.CharField(max_length=3)  # ID related to a specific group or section
    sw_id = models.CharField(max_length=3)  # Additional ID
    sw2_id = models.CharField(max_length=3)  # Secondary additional ID
    l_grupa = models.IntegerField()  # Numeric, 1 digit, no decimals
    l_kl3 = models.DateField(null=True, blank=True)  # Date format, related to specific classification or rank
    swk3_id = models.CharField(max_length=3)  # ID related to l_kl3
    l_kl3_rozk = models.CharField(max_length=40)  # Additional classification/rank information
    l_kl2 = models.DateField(null=True, blank=True)  # Date format, related to specific classification or rank
    swk2_id = models.CharField(max_length=3)  # ID related to l_kl2
    l_kl2_rozk = models.CharField(max_length=40)  # Additional classification/rank information
    l_kl1 = models.DateField(null=True, blank=True)  # Date format, related to specific classification or rank
    swk1_id = models.CharField(max_length=3)  # ID related to l_kl1
    l_kl1_rozk = models.CharField(max_length=40)  # Additional classification/rank information
    l_klm = models.DateField(null=True, blank=True)  # Date format, related to specific classification or rank
    swkm_id = models.CharField(max_length=3)  # ID related to l_klm
    l_klm_rozk = models.CharField(max_length=40)  # Additional classification/rank information
    st_id = models.CharField(max_length=19)  # Station ID
    tyn_id = models.CharField(max_length=3)  # Type ID
    l_z_pcw = models.BooleanField()  # Boolean field indicating a specific status
    l_stopien = models.CharField(max_length=2)  # Rank or degree
    l_2imie = models.CharField(max_length=15)  # Second name (if applicable)
    l_imie_o = models.CharField(max_length=15)  # Father's name
    l_imie_m = models.CharField(max_length=15)  # Mother's name
    l_ur = models.DateField(null=True, blank=True)  # Date of birth
    l_m_ur = models.CharField(max_length=20)  # Place of birth
    l_nip = models.CharField(max_length=13)  # NIP (Tax Identification Number)
    l_miasto = models.CharField(max_length=20)  # City
    l_kod_p = models.CharField(max_length=6)  # Postal code
    l_ulica = models.CharField(max_length=30)  # Street address
    l_fax = models.CharField(max_length=20)  # Fax number
    l_tel_s = models.CharField(max_length=40)  # Phone number
    l_tel_d = models.CharField(max_length=40)  # Secondary phone number
    l_kat_zasz = models.CharField(max_length=2)  # Category of insurance
    l_wz = models.DecimalField(max_digits=10, decimal_places=2)  # WZ (Warehouse) or another numeric value
    l_pzu = models.DecimalField(max_digits=3, decimal_places=0)  # PZU (insurance related)
    l_premia = models.DecimalField(max_digits=3, decimal_places=0)  # Premium
    l_pin = models.CharField(max_length=4)  # PIN code
    l_foto = models.CharField(max_length=70)  # Path to photo
    l_podpis = models.CharField(max_length=70)  # Path to signature
    l_opinia = models.TextField()  # Opinion or remarks
    l_pr_thn = models.DecimalField(max_digits=4, decimal_places=1)  # Standard working time in hours
    l_pr_1 = models.BooleanField()  # Boolean field indicating a specific status (e.g., part-time)
    l_pr_1od = models.DecimalField(max_digits=2, decimal_places=0)  # Start time (hours)
    l_pr_1odm = models.DecimalField(max_digits=2, decimal_places=0)  # Start time (minutes)
    l_pr_1do = models.DecimalField(max_digits=2, decimal_places=0)  # End time (hours)
    l_pr_1dom = models.DecimalField(max_digits=2, decimal_places=0)  # End time (minutes)
    l_pr_2 = models.BooleanField()  # Boolean field indicating a specific status
    l_pr_2od = models.DecimalField(max_digits=2, decimal_places=0)  # Start time (hours)
    l_pr_2odm = models.DecimalField(max_digits=2, decimal_places=0)  # Start time (minutes)
    l_pr_2do = models.DecimalField(max_digits=2, decimal_places=0)  # End time (hours)
    l_pr_2dom = models.DecimalField(max_digits=2, decimal_places=0)  # End time (minutes)
    l_pr_3 = models.BooleanField()  # Boolean field indicating a specific status
    l_pr_3od = models.DecimalField(max_digits=2, decimal_places=0)  # Start time (hours)
    l_pr_3odm = models.DecimalField(max_digits=2, decimal_places=0)  # Start time (minutes)
    l_pr_3do = models.DecimalField(max_digits=2, decimal_places=0)  # End time (hours)
    l_pr_3dom = models.DecimalField(max_digits=2, decimal_places=0)  # End time (minutes)
    l_pr_4 = models.BooleanField()  # Boolean field indicating a specific status
    l_pr_4od = models.DecimalField(max_digits=2, decimal_places=0)  # Start time (hours)
    l_pr_4odm = models.DecimalField(max_digits=2, decimal_places=0)  # Start time (minutes)
    l_pr_4do = models.DecimalField(max_digits=2, decimal_places=0)  # End time (hours)
    l_pr_4dom = models.DecimalField(max_digits=2, decimal_places=0)  # End time (minutes)
    l_pr_5 = models.BooleanField()  # Boolean field indicating a specific status
    l_pr_5od = models.DecimalField(max_digits=2, decimal_places=0)  # Start time (hours)
    l_pr_5odm = models.DecimalField(max_digits=2, decimal_places=0)  # Start time (minutes)
    l_pr_5do = models.DecimalField(max_digits=2, decimal_places=0)  # End time (hours)
    l_pr_5dom = models.DecimalField(max_digits=2, decimal_places=0)  # End time (minutes)
    l_pr_m = models.BooleanField()  # Boolean field indicating a specific status
    l_pr_mod = models.DecimalField(max_digits=2, decimal_places=0)  # Start time (hours)
    l_pr_modm = models.DecimalField(max_digits=2, decimal_places=0)  # Start time (minutes)
    l_pr_mdo = models.DecimalField(max_digits=2, decimal_places=0)  # End time (hours)
    l_pr_mdom = models.DecimalField(max_digits=2, decimal_places=0)  # End time (minutes)
    l_norma_p = models.DecimalField(max_digits=4, decimal_places=0)  # Norms or standards
    l_status_p = models.DecimalField(max_digits=1, decimal_places=0)  # Status (1 digit)
    l_pr_th = models.CharField(max_length=15)  # Working time description
    pr_id = models.ForeignKey(Osrodek_pr, related_name='pers_st', on_delete=models.SET_NULL,null=True)  # ID related to the processing center

    class Meta:
        ordering = ('l_pesel',)


class Pers_gr(models.Model):
    l_pesel = models.ForeignKey(Pers_st, related_name='pers_gr_iums',
                                on_delete=models.CASCADE)  # Foreign key to Pers_st
    ium = models.CharField(max_length=6)  # IUM code
    nr_sw = models.CharField(max_length=12)  # SW number
    data_nad = models.DateField()  # Date of assignment
    zaw = models.BooleanField()  # Boolean field (IUM hanged)
    cof = models.BooleanField()  # Boolean field (IUM canceled)
    ost_sp = models.DateField(null=True, blank=True)  # Date of last calibration

    class Meta:
        ordering = ('l_pesel',)

    def __str__(self):
        return f"{self.l_pesel.l_nazw_im},IUM: {self.ium}, SW Number: {self.nr_sw}, Date of Assignment: {self.data_nad}, Hanged: {self.zaw}, Canceled: {self.cof}, Last Calibration Date: {self.ost_sp}"



class Indexy_4(models.Model):
    indeks = models.CharField(max_length=11, unique=True)  # Unique index code
    nazwa = models.CharField(max_length=70)  # Name of the item
    nsn = models.CharField(max_length=13)  # NSN (National Stock Number)
    p_jm = models.CharField(max_length=10)  # Unit of measure
    p_prod = models.CharField(max_length=10)  # Producer code
    p_komplet = models.TextField()  # Completion information (Memo field)
    p_tech = models.TextField()  # Technical description (Memo field)
    p_wymagani = models.TextField()  # Requirements (Memo field)
    ind_rek = models.CharField(max_length=17)  # Record index
    p_pwaz_k = models.DecimalField(max_digits=5, decimal_places=2)  # Precision weight K
    p_pwaz_u = models.DecimalField(max_digits=5, decimal_places=2)  # Precision weight U
    p_norma_k = models.DecimalField(max_digits=6, decimal_places=2)  # Standard K
    p_norma_u = models.DecimalField(max_digits=6, decimal_places=2)  # Standard U

    class Meta:
        ordering = ('indeks',)

    def __str__(self):
        return f'{self.indeks}, {self.nazwa}, {self.p_pwaz_k}, {self.p_norma_k}'

class Osrodek_met(models.Model):
    om_id = models.CharField(max_length=7, unique=True, null=False)  # Unique ID of the metrological center
    om_nazwa_p = models.CharField(max_length=50)  # Full name of the metrological center
    om_nazwa_s = models.CharField(max_length=6)  # Short name of the metrological center
    om_kod = models.CharField(max_length=6)  # Code
    om_miasto = models.CharField(max_length=30)  # City
    om_ulica = models.CharField(max_length=40)  # Street
    om_fax = models.CharField(max_length=35)  # Fax number
    ind_rek = models.CharField(max_length=17)  # Record index
    ind_poczta = models.BooleanField()  # Boolean field (Post related)
    om_is_wom = models.BooleanField()  # Boolean field (WOM related)
    om_tel = models.CharField(max_length=11)  # Telephone number
    om_email = models.CharField(max_length=16)  # Email address
    om_www = models.CharField(max_length=35)  # Website

    class Meta:
        ordering = ('om_id',)

class Ind4_om(models.Model):
    indeks = indeks = models.CharField(max_length=11, unique=True)
    om_id = models.CharField(max_length=7)
    p_pwaz_k = models.DecimalField(max_digits=5, decimal_places=2)  # Precision weight K
    p_pwaz_u = models.DecimalField(max_digits=5, decimal_places=2)  # Precision weight U
    p_norma_k = models.DecimalField(max_digits=6, decimal_places=2)  # Standard K
    p_norma_u = models.DecimalField(max_digits=6, decimal_places=2)  # Standard U
    p_norma_w = models.DecimalField(max_digits=6, decimal_places=2)  # Standard W
    p_metoda = models.TextField()  # Method description
    p_metodyka = models.TextField()  # Methodology
    p_excel = models.TextField()  # Excel data (Memo field)
    ind_rek = models.CharField(max_length=17)  # Record index

    class Meta:
        ordering = ('indeks',)

        def __str__(self):
            return f'{self.indeks},{self.p_pwaz_k},{self.p_norma_k}'
class Indexy_4_updated(models.Model):
    indeks = models.CharField(max_length=11, unique=True)  # Unique index code
    nazwa = models.CharField(max_length=70)  # Name of the item
    nsn = models.CharField(max_length=13)  # NSN (National Stock Number)
    p_jm = models.CharField(max_length=10)  # Unit of measure
    p_prod = models.CharField(max_length=10)  # Producer code
    p_komplet = models.TextField()  # Completion information (Memo field)
    p_tech = models.TextField()  # Technical description (Memo field)
    p_wymagani = models.TextField()  # Requirements (Memo field)
    ind_rek = models.CharField(max_length=17)  # Record index
    p_pwaz_k = models.DecimalField(max_digits=5, decimal_places=2)  # Precision weight K
    p_pwaz_u = models.DecimalField(max_digits=5, decimal_places=2)  # Precision weight U
    p_norma_k = models.DecimalField(max_digits=6, decimal_places=2)  # Standard K
    p_norma_u = models.DecimalField(max_digits=6, decimal_places=2)  # Standard U

    class Meta:
        ordering = ('indeks',)
    def __str__(self):
        return f'{self.indeks}, {self.nazwa},{self.p_pwaz_k},{self.p_norma_k}'
class Uzytkownik(models.Model):
    sz_ind = models.CharField(max_length=8)  # Index (likely not unique)
    u_id = models.CharField(max_length=7, unique=True)  # User ID, primary key
    u_nazwa_s = models.CharField(max_length=12)  # Short name of the user
    u_nazwa_p = models.CharField(max_length=48)  # Full name of the user
    u_kod_p = models.CharField(max_length=6)  # Postal code
    u_miasto = models.CharField(max_length=30)  # City
    u_ulica = models.CharField(max_length=40)  # Street
    u_krypt = models.CharField(max_length=20)  # Cryptonym
    u_fax = models.CharField(max_length=20)  # Fax number
    u_metro = models.CharField(max_length=30)  # Metrology-related field
    u_metro_te = models.CharField(max_length=20)  # Technical metrology field
    u_szef = models.CharField(max_length=30)  # Manager
    u_szef_t = models.CharField(max_length=20)  # Manager's title
    u_techn = models.CharField(max_length=30)  # Technical contact
    u_techn_t = models.CharField(max_length=20)  # Technical contact's title
    ind_rek = models.CharField(max_length=17)  # Record index
    om_id = models.ForeignKey(Osrodek_met, related_name='om_users', on_delete=models.CASCADE)  # Center ID
    u_adresat = models.CharField(max_length=48)  # Addressee
    u_metro_et = models.BooleanField()  # Metrology label (Boolean)
    u_met_up_n = models.CharField(max_length=15)  # Additional metrology field

    class Meta:
        ordering = ('u_id',)





class Przyrzad_zmcbd(models.Model):
    indeks = models.ForeignKey(Indexy_4, related_name='przyrzady', on_delete=models.SET_NULL, null=True)  # Klucz obcy do modelu Indexy_4
    p_nr_fab = models.CharField(max_length=20)  # Numer fabryczny przyrządu
    u_id = models.ForeignKey(Uzytkownik, related_name='przyrzady', on_delete=models.SET_NULL,null=True)  # Klucz obcy do modelu Uzytkownik
    om_id = models.ForeignKey(Osrodek_met, related_name='przyrzady', on_delete=models.SET_NULL, null=True)  # Klucz obcy do modelu Osrodek_met
    pr_id = models.ForeignKey(Osrodek_pr, related_name='przyrzady', on_delete=models.SET_NULL,null=True)  # Klucz obcy do modelu Osrodek_pr
    u_data_pl = models.DateField(null=True, blank=True)  # Data planowanego przyjęcia, pole DateField
    k_data_wa = models.DateField(null=True, blank=True)  # Data ważności, pole DateField
    k_stan_tk = models.BooleanField(default=False)  # Stan techniczny (prawdopodobnie boolean, 'F' = False)
    p_zm_id = models.ForeignKey(Uzytkownik, related_name='przyrzady_poprzedni_uzytkownik', on_delete=models.SET_NULL,null=True)
    kod_ean8 = models.CharField(max_length=8)  # Kod EAN8
    ind_rek = models.CharField(max_length=17, unique=True)  # Indeks rekordu, teraz unikatowy
    akcept = models.BooleanField(default=False)  # Akceptacja (prawdopodobnie boolean, 'F' = False)
    p_kal_nt = models.BooleanField(default=False)  # Kalibracja nieaktualna (prawdopodobnie boolean, 'F' = False)

    class Meta:
        ordering = ('ind_rek',)
class Bok(models.Model):
    bk_id = models.CharField(max_length=15,unique=True)  # Identyfikator rekordu
    pr_id = models.ForeignKey('Osrodek_pr', related_name='boks', on_delete=models.SET_NULL, null=True)  # Klucz obcy do modelu Osrodek_pr
    p_nr_fab = models.CharField(max_length=20)  # Numer fabryczny
    u_id = models.ForeignKey('Uzytkownik', related_name='boks', on_delete=models.SET_NULL, null=True)  # Klucz obcy do modelu Uzytkownik
    u_data_p = models.DateField(null=True, blank=True)  # Data przyjęcia
    u_nr_potp = models.CharField(max_length=20)  # Numer potwierdzenia przyjęcia
    u_dost = models.CharField(max_length=50)  # Dostawca
    u_cecha_p = models.CharField(max_length=1)  # Cechowanie przyjęcia
    u_stan_tp = models.CharField(max_length=1)  # Stan techniczny przyjęcia
    u_podstawa = models.CharField(max_length=2)  # Podstawa przyjęcia
    p_komplet = models.CharField(max_length=255)  # Informacja o komplecie
    k_do_k_n = models.CharField(max_length=1)  # Kalibracja decyzja numer
    k_do_data = models.DateField(null=True, blank=True)  # Data kalibracji
    k_do_pesel = models.ForeignKey('Pers_st', related_name='bok_kalibracje', on_delete=models.SET_NULL, null=True)  # Klucz obcy do modelu Pers_st (kalibracja)
    k_do_pin = models.CharField(max_length=4)  # PIN do kalibracji
    k_do_datap = models.DateField(null=True, blank=True)  # Data pobrania do kalibracji
    k_pr_sp_nr = models.CharField(max_length=15)  # Numer sprawdzenia kalibracji
    k_sk_do = models.CharField(max_length=1)  # Kalibracja zakończona
    k_bk_data = models.DateField(null=True, blank=True)  # Data zwrotu po kalibracji
    k_bk_pesel = models.ForeignKey('Pers_st', related_name='bok_odbior', on_delete=models.SET_NULL, null=True)  # Klucz obcy do modelu Pers_st (osoba odbierająca)
    k_bk_pin = models.CharField(max_length=4)  # PIN osoby przyjmującej po kalibracji
    k_pr_sp = models.TextField()  # Opis procesu kalibracji
    k_form = models.CharField(max_length=255)  # Formularz kalibracji
    bk_uwagi = models.CharField(max_length=1)  # Uwagi BOK
    u_data_w = models.DateField(null=True, blank=True)  # Data wydania
    u_nr_potw = models.CharField(max_length=20)  # Numer potwierdzenia wydania
    u_odbior = models.CharField(max_length=50)  # Odbiorca
    u_nr_up = models.CharField(max_length=10)  # Numer użytkownika
    bk_kbok = models.CharField(max_length=50)  # Kategoria BOK
    om_pracow = models.ForeignKey('Osrodek_met', related_name='boks', on_delete=models.SET_NULL, null=True)  # Klucz obcy do modelu Osrodek_met
    p_ind_rek = models.ForeignKey('Przyrzad_zmcbd', related_name='boks', on_delete=models.SET_NULL, null=True)  # Klucz obcy do modelu Przyrzad_zmcbd
    p_typ = models.CharField(max_length=50)  # Typ przyrządu
    u_nazwa_s = models.CharField(max_length=12)  # Nazwa skrócona użytkownika
    kod_ean8 = models.CharField(max_length=8)  # Kod EAN8
    u_kal = models.BooleanField(default=False)  # Kalibracja (True/False)
    gwar = models.BooleanField(default=False)  # Gwarancja (True/False)
    indeks = models.ForeignKey('Indexy_4', related_name='boks', on_delete=models.SET_NULL, null=True)  # Klucz obcy do modelu Indexy_4
    denp = models.CharField(max_length=1)  # Cechowanie denp
    cecha_br = models.CharField(max_length=1)  # Cecha braku
    paczka = models.CharField(max_length=1)  # Paczka

    class Meta:
        ordering = ('bk_id',)
    def get_udost_lastname(self):
        return self.u_dost.split()[-1]
    def __str__(self):
        return f'{self.bk_id}-{self.u_dost}-{self.k_bk_pesel.l_imie}-{self.k_bk_pesel.pr_id.pr_nazwa_p}'

class Ksiazka_k(models.Model):
    k_pr_sp_nr = models.CharField(max_length=15, unique=True)  # Calibration process number
    bk_id = models.ForeignKey(Bok, related_name='ksiazki_k', on_delete=models.SET_NULL,null=True)  # Klucz obcy do modelu Bok
    kp_nr = models.CharField(max_length=16)  # Protocol number
    pr_id = models.ForeignKey(Osrodek_pr, related_name='ksiazka_k', on_delete=models.SET_NULL,
                              null=True)  # Foreign key to Osrodek_pr
    p_nr_fab = models.CharField(max_length=20)  # Serial number of the instrument
    p_typ = models.CharField(max_length=50)  # Type of the instrument
    u_nazwa_s = models.CharField(max_length=12)  # Short name of the user
    k_do_k_n = models.CharField(max_length=1)  # Calibration decision number
    k_do_data = models.DateTimeField(null=True,
                                     blank=True)  # Date and time when the instrument was sent for calibration
    k_do_pesel = models.ForeignKey(Pers_st, related_name='ksiazka_k_kalibracje', on_delete=models.SET_NULL,
                                   null=True)  # PESEL of the person responsible for calibration
    k_bk_pesel = models.ForeignKey(Pers_st, related_name='ksiazka_k_k_bk_pesel', on_delete=models.SET_NULL,
                                   null=True)  # PESEL of the person who took over the instrument
    k_do_nazw = models.CharField(max_length=40)  # Last name of the person who took over the instrument
    k_do_datap = models.DateTimeField(null=True, blank=True)  # Date and time when the instrument was taken over
    k_do_dec = models.CharField(max_length=40)  # Decision related to the calibration
    k_do_ddata = models.DateTimeField(null=True, blank=True)  # Date and time of the decision
    k_sk_do = models.CharField(max_length=1)  # Additional decision information
    k_bk_data = models.DateTimeField(null=True, blank=True)  # Date and time when the instrument was returned
    k_bk_dec = models.CharField(max_length=40)  # Decision made after the instrument was returned
    k_bk_ddata = models.DateTimeField(null=True, blank=True)  # Date and time of the return decision
    kp_rbh_p = models.DecimalField(max_digits=10, decimal_places=2)  # Work hours for preparation
    kp_rbh_n = models.DecimalField(max_digits=10, decimal_places=2)  # Work hours for the finalization
    k_data_sp = models.DateField(null=True, blank=True)  # Date of inspection
    k_data_wa = models.DateField(null=True, blank=True)  # Expiration date of the instrument after calibration
    k_pin_sp = models.CharField(max_length=4)  # PIN for the inspection
    k_nazw_kp = models.CharField(max_length=40)  # Last name of the workshop manager
    k_data_kp = models.DateField(null=True, blank=True)  # Date of protocol signing by the workshop manager
    k_pin_kp = models.CharField(max_length=4)  # PIN for the protocol
    k_stan_tk = models.BooleanField()  # Technical condition (True/False)
    k_temp = models.DecimalField(max_digits=6, decimal_places=1)  # Temperature at the time of calibration
    k_wilgoc = models.DecimalField(max_digits=7, decimal_places=1)  # Humidity at the time of calibration
    k_cisn = models.DecimalField(max_digits=10, decimal_places=1)  # Pressure at the time of calibration
    k_nap_zas = models.DecimalField(max_digits=7, decimal_places=2)  # Voltage supplied during calibration
    k_czes_zas = models.DecimalField(max_digits=6, decimal_places=2)  # Frequency supplied during calibration
    k_pr_stron = models.DecimalField(max_digits=2, decimal_places=0)  # Number of pages in the protocol
    kp_prace = models.TextField()  # Detailed description of the work performed
    ostatni = models.DateTimeField(null=True, blank=True)  # Last modification date
    k_pr_sp_po = models.CharField(max_length=60)  # Additional information on the calibration process
    k_pr_sp_wg = models.CharField(max_length=40)  # Additional information on the calibration process
    k_nazw_kj = models.CharField(max_length=40)  # Last name of the quality specialist
    k_data_kj = models.DateField(null=True, blank=True)  # Date of protocol signing by the quality specialist
    k_pin_kj = models.CharField(max_length=4)  # PIN for the quality specialist
    k_nazw_kz = models.CharField(max_length=40)  # Last name of the plant manager
    k_data_kz = models.DateField(null=True, blank=True)  # Date of protocol signing by the plant manager
    k_pin_kz = models.CharField(max_length=4)  # PIN for the plant manager
    k_pr_sp_op = models.CharField(max_length=60)  # Additional information on the calibration process
    k_pr_sp_np = models.BooleanField()  # Boolean field for specific conditions
    k_pilne = models.BooleanField()  # Urgent (True/False)
    k_uwagi = models.CharField(max_length=100)  # Remarks
    k_zaznacz = models.BooleanField()  # Marked (True/False)
    p_excel = models.CharField(max_length=255)  # Excel-related information
    p_ind_rek = models.ForeignKey(Przyrzad_zmcbd, related_name='ksiazka_k', on_delete=models.SET_NULL, null=True)  # Klucz obcy do modelu Przyrzad_zmcbd
    u_data_p = models.DateField(null=True, blank=True)  # Date of acceptance into the deposit
    k_temp_k = models.DecimalField(max_digits=6, decimal_places=1)  # Temperature of the instrument
    k_wilgoc_k = models.DecimalField(max_digits=7, decimal_places=1)  # Humidity of the instrument
    k_cisn_k = models.DecimalField(max_digits=10, decimal_places=1)  # Pressure of the instrument
    rbh_b = models.DecimalField(max_digits=5, decimal_places=1)  # Work hours billed
    kp_ps = models.TextField()  # Additional notes on the process
    k_data_spp = models.DateField(null=True, blank=True)  # Date of starting the preparation process
    k_data_spk = models.DateField(null=True, blank=True)  # Date of starting the final process
    nr_sw = models.CharField(max_length=21)  # SW number
    nadzor = models.CharField(max_length=45)  # Supervisor's name
    prot_spr = models.BooleanField()  # Protocol for inspection (True/False)
    prot_kal = models.BooleanField()  # Protocol for calibration (True/False)
    prot_ogr = models.BooleanField()  # Protocol for boundary conditions (True/False)
    wzor_od = models.BooleanField()  # Model for determination (True/False)
    wzor_rob = models.BooleanField()  # Working model (True/False)
    wzor_od_ro = models.BooleanField()  # Model for determination in case of revision (True/False)
    indeks = models.CharField(max_length=11)

    class Meta:
        ordering = ('k_pr_sp_nr',)

    def __str__(self):
        return f"typ:{self.p_typ}, numer:{self.p_nr_fab}, kalibrujący:{self.k_do_nazw}, uzytkownik:{self.u_nazwa_s}\n"


    @classmethod
    def get_uncalibrated_devices_in_BOK(cls, pr_id):
        """
        Metoda zwraca przyrządy przypisane do danej pracowni, które są przeznaczone do kalibracji
        i nie zostały jeszcze pobrane do kalibracji, na podstawie QuerySet z `get_ksiazka_k_with_rbh`.

        Args:
        pr_id: numer ID pracowni, do której przypisane są przyrządy.

        Returns:
        QuerySet: Zbiór przyrządów spełniających podane kryteria.
        """
        # Pobierz QuerySet rozszerzony o `p_norma_k` i `p_norma_u`
        queryset_with_rbh = cls.get_ksiazka_k_with_rbh()

        # Zastosuj dodatkowe filtry do QuerySet
        uncalibrated_devices = queryset_with_rbh.filter(
            pr_id__pr_id=pr_id,        # Przyrządy przypisane do danej pracowni
            k_do_k_n='2',              # Przyrządy są przeznaczone do kalibracji (nie do kontroli wewnętrznej)
            k_do_datap__isnull=True    # Przyrząd nie został jeszcze pobrany do kalibracji
        )

        return uncalibrated_devices
    @classmethod
    def devices_in_BOK_to_assign(cls, pr_id, excluded_words_list):
        """
        Zwraca przyrządy, które spełniają określone warunki:
        1. k_do_nazw jest pusty (równe pusty string).
        2. k_uwagi nie zawiera słów z podanej listy excluded_words_list.

        :param pr_id: ID pracowni do filtrowania.
        :param excluded_words_list: Lista wyrazów, które mają być wykluczone z pola k_uwagi.
        :return: QuerySet z przyrządami do przypisania.
        """
        # Pobranie przyrządów do kalibracji
        devices_uncalibrated_in_BOK = cls.get_uncalibrated_devices_in_BOK(pr_id=pr_id)

        # Filtrowanie wierszy, gdzie k_do_nazw jest pusty
        devices_in_BOK_to_assign = devices_uncalibrated_in_BOK.filter(k_do_nazw='')

        # Wykluczanie wierszy na podstawie zawartości pola k_uwagi
        for word in excluded_words_list:
            devices_in_BOK_to_assign = devices_in_BOK_to_assign.exclude(k_uwagi__icontains=word)

        return devices_in_BOK_to_assign
    @classmethod
    def get_ksiazka_k_with_rbh(cls):
        """
        Metoda, która łączy dane z modelu Ksiazka_k z kolumnami p_norma_k i p_norma_u z modelu Indexy_4_updated.
        Zwraca QuerySet z wynikami.
        """
        Indexy_4_updated = apps.get_model('optylogis', 'Indexy_4_updated')

        # Podzapytania dla kolumn `p_norma_k` i `p_norma_u` z tabeli Indexy_4_updated
        subquery_p_norma_k = Indexy_4_updated.objects.filter(indeks=OuterRef('indeks')).values('p_norma_k')[:1]
        subquery_p_norma_u = Indexy_4_updated.objects.filter(indeks=OuterRef('indeks')).values('p_norma_u')[:1]

        # Wykonanie zapytania z dodanymi kolumnami `p_norma_k` i `p_norma_u`
        wynik = cls.objects.annotate(
            p_norma_k=Subquery(subquery_p_norma_k),
            p_norma_u=Subquery(subquery_p_norma_u)
        )

        return wynik  # Zwraca QuerySet z dodanymi polami `p_norma_k` i `p_norma_u`

    @staticmethod
    def remove_illegal_characters(text):
        """ Funkcja do usuwania nielegalnych znaków z tekstu """
        if isinstance(text, str):
            return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        return text


"""
"""
