-- Extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Enums
DO $$ BEGIN
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'jenis_kelamin_enum') THEN
  CREATE TYPE jenis_kelamin_enum AS ENUM ('L','P');
END IF;
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_tinggal_enum') THEN
  CREATE TYPE status_tinggal_enum AS ENUM ('mondok','pp','mukim');
END IF;
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sumber_biaya_enum') THEN
  CREATE TYPE sumber_biaya_enum AS ENUM ('orang_tua','wali','donatur','beasiswa');
END IF;
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_pembayaran_enum') THEN
  CREATE TYPE status_pembayaran_enum AS ENUM ('lancar','terlambat','menunggak');
END IF;
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'hubungan_enum') THEN
  CREATE TYPE hubungan_enum AS ENUM ('ayah','ibu','wali');
END IF;
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_hidup_enum') THEN
  CREATE TYPE status_hidup_enum AS ENUM ('hidup','meninggal');
END IF;
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_gizi_enum') THEN
  CREATE TYPE status_gizi_enum AS ENUM ('baik','kurang','lebih');
END IF;
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_rumah_enum') THEN
  CREATE TYPE status_rumah_enum AS ENUM ('milik_sendiri','kontrak','menumpang');
END IF;
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'jenis_lantai_enum') THEN
  CREATE TYPE jenis_lantai_enum AS ENUM ('tanah','semen','keramik');
END IF;
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'jenis_dinding_enum') THEN
  CREATE TYPE jenis_dinding_enum AS ENUM ('bambu','kayu','tembok');
END IF;
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'jenis_atap_enum') THEN
  CREATE TYPE jenis_atap_enum AS ENUM ('rumbia','seng','genteng','beton');
END IF;
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'akses_air_enum') THEN
  CREATE TYPE akses_air_enum AS ENUM ('layak','tidak_layak');
END IF;
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'daya_listrik_va_enum') THEN
  CREATE TYPE daya_listrik_va_enum AS ENUM ('450','900','1300','2200','3500','5500');
END IF;
IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'jenis_aset_enum') THEN
  CREATE TYPE jenis_aset_enum AS ENUM ('motor','mobil','sepeda','hp','laptop','lahan','ternak','alat_kerja','lainnya');
END IF;
END $$;

-- santri_pribadi
CREATE TABLE IF NOT EXISTS santri_pribadi (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nama              varchar(150) NOT NULL,
  nik               varchar(16),
  no_kk             varchar(16),
  tempat_lahir      varchar(100),
  tanggal_lahir     date,
  jenis_kelamin     jenis_kelamin_enum NOT NULL,
  status_tinggal    status_tinggal_enum,
  lama_mondok_tahun integer,
  provinsi          varchar(100),
  kabupaten         varchar(100),
  kecamatan         varchar(100),
  desa              varchar(100),
  lokasi            geometry(Point, 4326)
);

CREATE INDEX IF NOT EXISTS idx_santri_pribadi_lokasi
  ON santri_pribadi USING GIST (lokasi);

-- santri_bansos
CREATE TABLE IF NOT EXISTS santri_bansos (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  santri_id        uuid NOT NULL,
  pkh              boolean DEFAULT false,
  bpnt             boolean DEFAULT false,
  pip              boolean DEFAULT false,
  kis_pbi          boolean DEFAULT false,
  blt_desa         boolean DEFAULT false,
  bantuan_lainnya  varchar,
  CONSTRAINT fk_bansos_santri
    FOREIGN KEY (santri_id) REFERENCES santri_pribadi(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_bansos_santri_id
  ON santri_bansos (santri_id);

-- santri_pembiayaan
CREATE TABLE IF NOT EXISTS santri_pembiayaan (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  santri_id          uuid NOT NULL,
  biaya_per_bulan    integer,
  sumber_biaya       sumber_biaya_enum,
  nama_donatur       varchar(150),
  jenis_beasiswa     varchar(100),
  status_pembayaran  status_pembayaran_enum,
  tunggakan_bulan    integer DEFAULT 0,
  keterangan         varchar,
  CONSTRAINT fk_pembiayaan_santri
    FOREIGN KEY (santri_id) REFERENCES santri_pribadi(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_pembiayaan_santri_id
  ON santri_pembiayaan (santri_id);

-- santri_orangtua
CREATE TABLE IF NOT EXISTS santri_orangtua (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  santri_id          uuid NOT NULL,
  nama               varchar(150) NOT NULL,
  nik                varchar(16),
  hubungan           hubungan_enum,
  pendidikan         varchar(50),
  pekerjaan          varchar(100),
  pendapatan_bulanan integer,
  status_hidup       status_hidup_enum,
  kontak_telepon     varchar(15),
  CONSTRAINT fk_orangtua_santri
    FOREIGN KEY (santri_id) REFERENCES santri_pribadi(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_orangtua_santri_id
  ON santri_orangtua (santri_id);

-- santri_kesehatan
CREATE TABLE IF NOT EXISTS santri_kesehatan (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  santri_id        uuid NOT NULL,
  tinggi_badan     double precision,
  berat_badan      double precision,
  status_gizi      status_gizi_enum,
  riwayat_penyakit varchar,
  alergi_obat      varchar,
  kebutuhan_khusus varchar,
  CONSTRAINT fk_kesehatan_santri
    FOREIGN KEY (santri_id) REFERENCES santri_pribadi(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_kesehatan_santri_id
  ON santri_kesehatan (santri_id);

-- santri_rumah
CREATE TABLE IF NOT EXISTS santri_rumah (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  santri_id         uuid NOT NULL,
  status_rumah      status_rumah_enum NOT NULL,
  jenis_lantai      jenis_lantai_enum NOT NULL,
  jenis_dinding     jenis_dinding_enum NOT NULL,
  jenis_atap        jenis_atap_enum NOT NULL,
  akses_air_bersih  akses_air_enum NOT NULL,
  daya_listrik_va   daya_listrik_va_enum,
  CONSTRAINT fk_rumah_santri
    FOREIGN KEY (santri_id) REFERENCES santri_pribadi(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rumah_santri_id
  ON santri_rumah (santri_id);

-- santri_asset
CREATE TABLE IF NOT EXISTS santri_asset (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  santri_id        uuid NOT NULL,
  jenis_aset       jenis_aset_enum NOT NULL,
  jumlah           integer NOT NULL DEFAULT 1,
  nilai_perkiraan  integer,
  CONSTRAINT fk_asset_santri
    FOREIGN KEY (santri_id) REFERENCES santri_pribadi(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_asset_santri_id
  ON santri_asset (santri_id);
