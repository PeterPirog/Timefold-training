from django.core.management import call_command
from django.db import models, connection
import pandas as pd


# Create your models here.
from django.db import models

class Pers_st(models.Model):
    l_pesel = models.CharField(max_length=11, unique=True)
    l_nazwisko = models.CharField(max_length=30)
    l_imie = models.CharField(max_length=15)
    l_nazw_im = models.CharField(max_length=45)
    l_login = models.CharField(max_length=45)
    sp_id = models.CharField(max_length=3)
    sw_id = models.CharField(max_length=3)
    sw2_id = models.CharField(max_length=3)
    l_grupa = models.IntegerField()  # Numeric, 1 digit, no decimals
    l_kl3 = models.DateField()  # Date format
    swk3_id = models.CharField(max_length=3)
    l_kl3_rozk = models.CharField(max_length=40)
    l_kl2 = models.DateField()  # Date format
    swk2_id = models.CharField(max_length=3)
    l_kl2_rozk = models.CharField(max_length=40)
    l_kl1 = models.DateField()  # Date format
    swk1_id = models.CharField(max_length=3)
    l_kl1_rozk = models.CharField(max_length=40)
    l_klm = models.DateField()  # Date format
    swkm_id = models.CharField(max_length=3)
    l_klm_rozk = models.CharField(max_length=40)
    st_id = models.CharField(max_length=19)
    tyn_id = models.CharField(max_length=3)
    l_z_pcw = models.BooleanField()  # Logical field
    l_stopien = models.CharField(max_length=2)
    l_2imie = models.CharField(max_length=15)
    l_imie_o = models.CharField(max_length=15)
    l_imie_m = models.CharField(max_length=15)
    l_ur = models.DateField()  # Date format
    l_m_ur = models.CharField(max_length=20)
    l_nip = models.CharField(max_length=13)
    l_miasto = models.CharField(max_length=20)
    l_kod_p = models.CharField(max_length=6)
    l_ulica = models.CharField(max_length=30)
    l_fax = models.CharField(max_length=20)
    l_tel_s = models.CharField(max_length=40)
    l_tel_d = models.CharField(max_length=40)
    l_kat_zasz = models.CharField(max_length=2)
    l_wz = models.DecimalField(max_digits=10, decimal_places=2)
    l_pzu = models.DecimalField(max_digits=3, decimal_places=0)
    l_premia = models.DecimalField(max_digits=3, decimal_places=0)
    l_pin = models.CharField(max_length=4)
    l_foto = models.CharField(max_length=70)
    l_podpis = models.CharField(max_length=70)
    l_opinia = models.TextField()  # Memo field
    l_pr_thn = models.DecimalField(max_digits=4, decimal_places=1)
    l_pr_1 = models.BooleanField()  # Logical field
    l_pr_1od = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_1odm = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_1do = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_1dom = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_2 = models.BooleanField()  # Logical field
    l_pr_2od = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_2odm = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_2do = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_2dom = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_3 = models.BooleanField()  # Logical field
    l_pr_3od = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_3odm = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_3do = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_3dom = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_4 = models.BooleanField()  # Logical field
    l_pr_4od = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_4odm = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_4do = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_4dom = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_5 = models.BooleanField()  # Logical field
    l_pr_5od = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_5odm = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_5do = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_5dom = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_m = models.BooleanField()  # Logical field
    l_pr_mod = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_modm = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_mdo = models.DecimalField(max_digits=2, decimal_places=0)
    l_pr_mdom = models.DecimalField(max_digits=2, decimal_places=0)
    l_norma_p = models.DecimalField(max_digits=4, decimal_places=0)
    l_status_p = models.DecimalField(max_digits=1, decimal_places=0)
    l_pr_th = models.CharField(max_length=15)
    pr_id = models.CharField(max_length=10)

    class Meta:
        ordering = ('l_nazw_im',)


class Pers_gr(models.Model):
    pers_st = models.ForeignKey('optylogis.Pers_st', on_delete=models.CASCADE, to_field='l_pesel')  # Klucz obcy na pole l_pesel
    ium = models.CharField(max_length=6)
    nr_sw = models.CharField(max_length=12)
    data_nad = models.DateField()
    zaw = models.BooleanField()
    cof = models.BooleanField()
    ost_sp = models.DateField()

    class Meta:
        ordering = ('pers_st__l_nazw_im',)  # Sortowanie po l_nazw_im z modelu Pers_st

class Indexy_4(models.Model):
    indeks = models.CharField(max_length=11,unique=True)
    nazwa = models.CharField(max_length=70)
    nsn = models.CharField(max_length=13)
    p_jm = models.CharField(max_length=10)
    p_prod = models.CharField(max_length=10)
    p_komplet = models.TextField()  # Memo field, zmienione na TextField
    p_tech = models.TextField()  # Memo field, zmienione na TextField
    p_wymagani = models.TextField()  # Memo field, zmienione na TextField
    ind_rek = models.CharField(max_length=17)
    p_pwaz_k = models.DecimalField(max_digits=5, decimal_places=2)  # Numeric, 5 digits total, 2 decimal places
    p_pwaz_u = models.DecimalField(max_digits=5, decimal_places=2)  # Numeric, 5 digits total, 2 decimal places
    p_norma_k = models.DecimalField(max_digits=6, decimal_places=2)  # Numeric, 6 digits total, 2 decimal places
    p_norma_u = models.DecimalField(max_digits=6, decimal_places=2)  # Numeric, 6 digits total, 2 decimal places

    class Meta:
        ordering = ('indeks',)
class Osrodek_met(models.Model):
    om_id = models.CharField(max_length=7,unique=True,null=False)
    om_nazwa_p = models.CharField(max_length=50)
    om_nazwa_s = models.CharField(max_length=6)
    om_kod = models.CharField(max_length=6)
    om_miasto = models.CharField(max_length=30)
    om_ulica = models.CharField(max_length=40)
    om_fax = models.CharField(max_length=35)
    ind_rek = models.CharField(max_length=17)
    ind_poczta = models.BooleanField()  # Zmienione na BooleanField, ponieważ w danych jest to pole logiczne
    om_is_wom = models.BooleanField()  # Zmienione na BooleanField, ponieważ w danych jest to pole logiczne
    om_tel = models.CharField(max_length=11)
    om_email = models.CharField(max_length=16)
    om_www = models.CharField(max_length=35)

    class Meta:
        ordering = ('om_id',)
class Ind4_om(models.Model):
    indeks = models.CharField(max_length=11, unique=True)
    osrodek_met = models.ForeignKey('optylogis.Osrodek_met',on_delete=models.CASCADE, to_field='om_id',blank=True, null=True)
    p_pwaz_k = models.DecimalField(max_digits=5, decimal_places=2)
    p_pwaz_u = models.DecimalField(max_digits=5, decimal_places=2)
    p_norma_k = models.DecimalField(max_digits=6, decimal_places=2)
    p_norma_u = models.DecimalField(max_digits=6, decimal_places=2)
    p_norma_w = models.DecimalField(max_digits=6, decimal_places=2)
    p_metoda = models.TextField()
    p_metodyka = models.TextField()
    p_excel = models.TextField()
    ind_rek = models.CharField(max_length=17)

    class Meta:
        ordering = ('indeks',)