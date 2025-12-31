-- Drop existing tables and indexes if they exist
DROP TABLE IF EXISTS santri_map CASCADE;
DROP TABLE IF EXISTS pesantren_map CASCADE;

-- Drop orphan indexes
DROP INDEX IF EXISTS idx_santri_map_lokasi;
DROP INDEX IF EXISTS idx_pesantren_map_lokasi;
DROP INDEX IF EXISTS idx_santri_map_santri_id;
DROP INDEX IF EXISTS idx_santri_map_nama;
DROP INDEX IF EXISTS idx_santri_map_pesantren_id;
DROP INDEX IF EXISTS idx_santri_map_kategori;
DROP INDEX IF EXISTS idx_pesantren_map_pesantren_id;
DROP INDEX IF EXISTS idx_pesantren_map_nama;
DROP INDEX IF EXISTS idx_pesantren_map_kabupaten;
DROP INDEX IF EXISTS idx_pesantren_map_provinsi;
DROP INDEX IF EXISTS idx_pesantren_map_kategori;

-- Create santri_map table
CREATE TABLE santri_map (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    santri_id UUID NOT NULL UNIQUE REFERENCES santri_pribadi(id) ON DELETE CASCADE,
    nama VARCHAR(150) NOT NULL,
    skor_terakhir INTEGER NOT NULL DEFAULT 0,
    kategori_kemiskinan VARCHAR(50) NOT NULL DEFAULT 'Tidak Miskin',
    lokasi GEOMETRY(POINT, 4326),
    pesantren_id UUID REFERENCES pondok_pesantren(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for santri_map
CREATE INDEX idx_santri_map_santri_id ON santri_map(santri_id);
CREATE INDEX idx_santri_map_nama ON santri_map(nama);
CREATE INDEX idx_santri_map_pesantren_id ON santri_map(pesantren_id);
CREATE INDEX idx_santri_map_kategori ON santri_map(kategori_kemiskinan);
CREATE INDEX idx_santri_map_lokasi ON santri_map USING GIST(lokasi);

-- Create pesantren_map table
CREATE TABLE pesantren_map (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pesantren_id UUID NOT NULL UNIQUE REFERENCES pondok_pesantren(id) ON DELETE CASCADE,
    nama VARCHAR(200) NOT NULL,
    nsp VARCHAR(50),
    skor_terakhir INTEGER NOT NULL DEFAULT 0,
    kategori_kelayakan VARCHAR(50) NOT NULL DEFAULT 'tidak_layak',
    lokasi GEOMETRY(POINT, 4326),
    kabupaten VARCHAR(100),
    provinsi VARCHAR(100),
    jumlah_santri INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for pesantren_map
CREATE INDEX idx_pesantren_map_pesantren_id ON pesantren_map(pesantren_id);
CREATE INDEX idx_pesantren_map_nama ON pesantren_map(nama);
CREATE INDEX idx_pesantren_map_kabupaten ON pesantren_map(kabupaten);
CREATE INDEX idx_pesantren_map_provinsi ON pesantren_map(provinsi);
CREATE INDEX idx_pesantren_map_kategori ON pesantren_map(kategori_kelayakan);
CREATE INDEX idx_pesantren_map_lokasi ON pesantren_map USING GIST(lokasi);
