from enum import Enum as PyEnum

class KondisiBangunanEnum(str, PyEnum):
    permanen = "permanen"
    semi_permanen = "semi_permanen"
    non_permanen = "non_permanen"

class SanitasiEnum(str, PyEnum):
    layak = "layak"
    cukup = "cukup"
    tidak_layak = "tidak_layak"

class AirBersihEnum(str, PyEnum):
    lancar = "lancar"
    terbatas = "terbatas"
    tidak_tersedia = "tidak_tersedia"

class KeamananBangunanEnum(str, PyEnum):
    standar = "standar"
    minim = "minim"
    tidak_aman = "tidak_aman"
    tinggi = "tinggi"

class KelayakanEnum(str, PyEnum):
    layak = "layak"
    cukup = "cukup"
    tidak_layak = "tidak_layak"

class KetersediaanEnum(str, PyEnum):
    ada = "ada"
    terbatas = "terbatas"
    tidak_ada = "tidak_ada"

class KestabilanEnum(str, PyEnum):
    stabil = "stabil"
    tidak_stabil = "tidak_stabil"
    tidak_ada = "tidak_ada"

class JenjangPendidikanEnum(str, PyEnum):
    semua_ra_ma = "semua_ra_ma"  # Semua Ada dari RA-MA
    pendidikan_dasar = "pendidikan_dasar"  # Pendidikan Dasar Saja (MI)
    dasar_menengah_pertama = "dasar_menengah_pertama"  # MI-MTs
    dasar_menengah_atas = "dasar_menengah_atas"  # MI-MA
    satu_jenjang = "satu_jenjang"  # Hanya satu jenjang Pendidikan

class KurikulumEnum(str, PyEnum):
    terstandar = "terstandar"
    internal = "internal"
    tidak_jelas = "tidak_jelas"

class AkreditasiEnum(str, PyEnum):
    a = "a"
    b = "b"
    c = "c"
    belum = "belum"

class PrestasiEnum(str, PyEnum):
    nasional = "nasional"
    regional = "regional"
    tidak_ada = "tidak_ada"

class KategoriKelayakanEnum(str, PyEnum):
    sangat_layak = "sangat_layak"
    layak = "layak"
    cukup_layak = "cukup_layak"
    tidak_layak = "tidak_layak"

class StatusBangunanEnum(str, PyEnum):
    milik_sendiri = "milik_sendiri"
    sewa = "sewa"
    pinjam = "pinjam"
    hibah = "hibah"
    wakaf = "wakaf"

class SumberAirEnum(str, PyEnum):
    sumur = "sumur"
    PDAM = "PDAM"
    sungai = "sungai"
    hujan = "hujan"
    berbagai_macam = "berbagai_macam"

class FasilitasMCKEnum(str, PyEnum):
    lengkap = "lengkap"
    kurang_lengkap = "kurang_lengkap"
    cukup = "cukup"
    tidak_layak = "tidak_layak"

class JenisLantaiEnum(str, PyEnum):
    keramik = "keramik"
    marmer = "marmer"
    kayu = "kayu"
    beton = "beton"
    tanah = "tanah"

class JenisAtapEnum(str, PyEnum):
    genteng_tanah_liat = "genteng_tanah_liat"
    metal = "metal"
    seng = "seng"
    upvc = "upvc"
    asbes = "asbes"
    ijuk = "ijuk"

class JenisDindingEnum(str, PyEnum):
    tembok = "tembok"
    kayu = "kayu"
    bambu = "bambu"
    anyaman = "anyaman"
    papan = "papan"

class SumberListrikEnum(str, PyEnum):
    PLN = "PLN"
    genset = "genset"
    listrik_tidak_ada = "listrik_tidak_ada"
    tenaga_surya = "tenaga_surya"

class FasilitasMengajarEnum(str, PyEnum):
    projector = "projector"
    papan_tulis = "papan_tulis"
    tv_monitor = "tv_monitor"
    whiteboard = "whiteboard"

class KualitasAirBersihEnum(str, PyEnum):
    asin = "asin"
    layak_minum = "layak_minum"
    berbau = "berbau"
    keruh = "keruh"

class FasilitasKomunikasiEnum(str, PyEnum):
    internet = "internet"
    telepon = "telepon"
    pos = "pos"

class MetodePembayaranEnum(str, PyEnum):
    tunai = "tunai"
    non_tunai = "non_tunai"
    campuran = "campuran"

class FasilitasTransportasiEnum(str, PyEnum):
    bus = "bus"
    angkutan_umum = "angkutan_umum"
    kendaraan_pribadi = "kendaraan_pribadi"
    ojek = "ojek"

class AksesJalanEnum(str, PyEnum):
    aspal = "aspal"
    cor_block = "cor_block"
    tanah = "tanah"
    kerikil = "kerikil"