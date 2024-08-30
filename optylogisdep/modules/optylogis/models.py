# Create your models here.
from django.db import models


# models to run examples

class Department(models.Model):
    """
    Model reprezentujący departament w organizacji.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    """
    Model reprezentujący projekt w organizacji.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class EmployeeAssignment(models.Model):
    """
    Model reprezentujący przypisanie pracownika do projektu w danym departamencie.
    """
    department = models.ForeignKey(Department, related_name='employee_assignments', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='employee_assignments', on_delete=models.CASCADE)
    role = models.CharField(max_length=255, null=True, blank=True)
    project_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.department.name} - {self.project.name} - {self.role}"


##########################################################################

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

    def __str__(self):
        return self.l_pesel


class Pers_gr(models.Model):
    l_pesel = models.ForeignKey(Pers_st, related_name='pers_gr_iums', on_delete=models.CASCADE)
    ium = models.CharField(max_length=6)
    nr_sw = models.CharField(max_length=12)
    data_nad = models.DateField()
    zaw = models.BooleanField()
    cof = models.BooleanField()
    ost_sp = models.DateField()

    def __str__(self):
        # Tworzymy bardziej opisową reprezentację tekstową
        return f"{self.l_pesel.l_nazw_im} - {self.ium} - {self.nr_sw}"


"""
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
    #osrodek_met = models.ForeignKey('optylogis.Osrodek_met',on_delete=models.CASCADE, to_field='om_id',default=None)
    om_id = models.CharField(max_length=7,default=None)
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

from django.db import models

class Ksiazka_k(models.Model):
    k_pr_sp_nr = models.CharField(max_length=15, unique=True)
    bk_id = models.CharField(max_length=15)
    kp_nr = models.CharField(max_length=16)
    pr_id = models.CharField(max_length=10)
    p_nr_fab = models.CharField(max_length=20)
    p_typ = models.CharField(max_length=50)
    u_nazwa_s = models.CharField(max_length=12)
    k_do_k_n = models.CharField(max_length=1)
    k_do_data = models.DateTimeField()
    # Klucze obce na kolumny z PESEL-em
    k_do_pesel = models.CharField(max_length=11) #models.ForeignKey('optylogis.Pers_st', on_delete=models.CASCADE, to_field='l_pesel', related_name='do_pesel_ksiazka')
    k_bk_pesel = models.CharField(max_length=11) #models.ForeignKey('optylogis.Pers_st', on_delete=models.CASCADE, to_field='l_pesel', related_name='bk_pesel_ksiazka')
    k_do_nazw = models.CharField(max_length=40)
    k_do_datap = models.DateTimeField()
    k_do_dec = models.CharField(max_length=40)
    k_do_ddata = models.DateTimeField()
    k_sk_do = models.CharField(max_length=1)
    k_bk_data = models.DateTimeField()
    k_bk_dec = models.CharField(max_length=40)
    k_bk_ddata = models.DateTimeField()
    kp_rbh_p = models.DecimalField(max_digits=10, decimal_places=2)
    kp_rbh_n = models.DecimalField(max_digits=10, decimal_places=2)
    k_data_sp = models.DateField()
    k_data_wa = models.DateField()
    k_pin_sp = models.CharField(max_length=4)
    k_nazw_kp = models.CharField(max_length=40)
    k_data_kp = models.DateField()
    k_pin_kp = models.CharField(max_length=4)
    k_stan_tk = models.BooleanField()
    k_temp = models.DecimalField(max_digits=6, decimal_places=1)
    k_wilgoc = models.DecimalField(max_digits=7, decimal_places=1)
    k_cisn = models.DecimalField(max_digits=10, decimal_places=1)
    k_nap_zas = models.DecimalField(max_digits=7, decimal_places=2)
    k_czes_zas = models.DecimalField(max_digits=6, decimal_places=2)
    k_pr_stron = models.DecimalField(max_digits=2, decimal_places=0)
    kp_prace = models.TextField()
    ostatni = models.DateTimeField()
    k_pr_sp_po = models.CharField(max_length=60)
    k_pr_sp_wg = models.CharField(max_length=40)
    k_nazw_kj = models.CharField(max_length=40)
    k_data_kj = models.DateField()
    k_pin_kj = models.CharField(max_length=4)
    k_nazw_kz = models.CharField(max_length=40)
    k_data_kz = models.DateField()
    k_pin_kz = models.CharField(max_length=4)
    k_pr_sp_op = models.CharField(max_length=60)
    k_pr_sp_np = models.BooleanField()
    k_pilne = models.BooleanField()
    k_uwagi = models.CharField(max_length=100)
    k_zaznacz = models.BooleanField()
    p_excel = models.CharField(max_length=255)
    p_ind_rek = models.CharField(max_length=17)
    u_data_p = models.DateField()
    k_temp_k = models.DecimalField(max_digits=6, decimal_places=1)
    k_wilgoc_k = models.DecimalField(max_digits=7, decimal_places=1)
    k_cisn_k = models.DecimalField(max_digits=10, decimal_places=1)
    rbh_b = models.DecimalField(max_digits=5, decimal_places=1)
    kp_ps = models.TextField()
    k_data_spp = models.DateField()
    k_data_spk = models.DateField()
    nr_sw = models.CharField(max_length=21)
    nadzor = models.CharField(max_length=45)
    prot_spr = models.BooleanField()
    prot_kal = models.BooleanField()
    prot_ogr = models.BooleanField()
    wzor_od = models.BooleanField()
    wzor_rob = models.BooleanField()
    wzor_od_ro = models.BooleanField()
    indeks = models.CharField(max_length=11)

    class Meta:
        ordering = ('k_pr_sp_nr',)
"""
