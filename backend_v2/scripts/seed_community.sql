-- ==========================================================================
-- PGN Phase 1 — Community Seed Data (SQL version)
-- Run AFTER the Alembic migration: alembic upgrade 001_pgn_phase1
-- ==========================================================================

-- ── Community Users (20 rows) ─────────────────────────────────────────────

INSERT INTO community.community_users
  (id, full_name, email, phone, is_verified, country, state, city, created_at, updated_at)
VALUES
  (gen_random_uuid(),'Priya Rajan',       'priya.rajan@gmail.com',        '+919876543210', true,  'India','Tamil Nadu',     'Chennai',           now(), now()),
  (gen_random_uuid(),'Arun Kumar',        'arun.kumar@yahoo.com',         '+919123456780', false, 'India','Karnataka',      'Bengaluru',         now(), now()),
  (gen_random_uuid(),'Meena Krishnan',    'meena.k@outlook.com',          '+919234567891', true,  'India','Kerala',         'Kochi',             now(), now()),
  (gen_random_uuid(),'Suresh Pillai',     'suresh.pillai@hotmail.com',    '+919345678902', false, 'India','Andhra Pradesh', 'Hyderabad',         now(), now()),
  (gen_random_uuid(),'Divya Nair',        'divya.nair@gmail.com',         '+919456789013', true,  'India','Tamil Nadu',     'Coimbatore',        now(), now()),
  (gen_random_uuid(),'Ramesh Iyer',       'ramesh.iyer@gmail.com',        '+919567890124', false, 'India','Karnataka',      'Mysuru',            now(), now()),
  (gen_random_uuid(),'Latha Venkatesh',   'latha.v@protonmail.com',       '+919678901235', true,  'India','Tamil Nadu',     'Madurai',           now(), now()),
  (gen_random_uuid(),'Vijay Shankar',     'vijay.shankar@gmail.com',      '+919789012346', true,  'India','Kerala',         'Thiruvananthapuram',now(), now()),
  (gen_random_uuid(),'Kavitha Balaji',    'kavitha.b@gmail.com',          '+919890123457', false, 'India','Tamil Nadu',     'Salem',             now(), now()),
  (gen_random_uuid(),'Mohan Das',         'mohan.das@gmail.com',          '+919901234568', false, 'India','Karnataka',      'Hubli',             now(), now()),
  (gen_random_uuid(),'Anitha Reddy',      'anitha.reddy@outlook.com',     '+918012345679', true,  'India','Telangana',      'Hyderabad',         now(), now()),
  (gen_random_uuid(),'Rajesh Murugan',    'rajesh.m@gmail.com',           '+918123456780', false, 'India','Tamil Nadu',     'Trichy',            now(), now()),
  (gen_random_uuid(),'Sunita Joshi',      'sunita.joshi@gmail.com',       '+918234567891', true,  'India','Maharashtra',    'Pune',              now(), now()),
  (gen_random_uuid(),'Deepak Sharma',     'deepak.sharma@gmail.com',      '+918345678902', true,  'India','Delhi',          'New Delhi',         now(), now()),
  (gen_random_uuid(),'Nithya Sundaram',   'nithya.s@gmail.com',           '+918456789013', false, 'India','Tamil Nadu',     'Vellore',           now(), now()),
  (gen_random_uuid(),'Harish Chandar',    'harish.c@yahoo.com',           '+918567890124', false, 'India','Karnataka',      'Mangaluru',         now(), now()),
  (gen_random_uuid(),'Rekha Menon',       'rekha.menon@gmail.com',        '+918678901235', true,  'India','Kerala',         'Kozhikode',         now(), now()),
  (gen_random_uuid(),'Santhosh Kumar',    'santhosh.kumar@gmail.com',     '+918789012346', false, 'India','Tamil Nadu',     'Erode',             now(), now()),
  (gen_random_uuid(),'Pooja Venkataraman','pooja.vr@gmail.com',           '+918890123457', true,  'India','Tamil Nadu',     'Tirunelveli',       now(), now()),
  (gen_random_uuid(),'Bala Subramaniam',  'bala.sub@protonmail.com',      '+918901234568', false, 'India','Tamil Nadu',     'Thoothukudi',       now(), now())
ON CONFLICT (email) DO NOTHING;

-- ── Product Reports (50 rows via generate_series) ─────────────────────────

INSERT INTO community.product_reports
  (id, user_id, barcode, batch_number, product_name, report_type, severity,
   description, purchase_location, purchase_date, status, created_at, updated_at)
SELECT
  gen_random_uuid(),
  u.id,
  ('8901030865023'::text, '8906002393053', '8901011043123', '8902102151020',
   '8901491501073')[floor(random()*5+1)::int],
  ('BATCH-A001'::text, 'BATCH-B002', 'BATCH-C003', 'BATCH-D004', 'BATCH-E005')[floor(random()*5+1)::int],
  ('Amul Milk 1L'::text, 'Maggi Noodles', 'Colgate Toothpaste', 'Parle-G Biscuits',
   'Haldirams Mixture')[floor(random()*5+1)::int],
  ('DAMAGED_PACKAGING'::text, 'WRONG_EXPIRY', 'BAD_SMELL', 'LEAKAGE',
   'WRONG_PRODUCT', 'FOREIGN_OBJECT', 'FAKE_PRODUCT', 'OTHER')[floor(random()*8+1)::int],
  ('LOW'::text, 'MEDIUM', 'HIGH', 'CRITICAL')[floor(random()*4+1)::int],
  'The product had a visible quality defect that was noticed immediately upon delivery receipt. Reporting for safety. Incident number ' || gs,
  ('Zepto - Adyar'::text, 'BigBasket Hub', 'Blinkit - Velachery', 'DMart - Perambur',
   'Swiggy Instamart - OMR')[floor(random()*5+1)::int],
  CURRENT_DATE - (floor(random()*30+1)::int) * INTERVAL '1 day',
  ('PENDING'::text, 'UNDER_REVIEW', 'VERIFIED', 'REJECTED')[floor(random()*4+1)::int],
  now() - (floor(random()*720)::int) * INTERVAL '1 hour',
  now()
FROM generate_series(1, 50) AS gs
CROSS JOIN LATERAL (
  SELECT id FROM community.community_users
  ORDER BY random() LIMIT 1
) u;

-- ── Report Images (100 rows) ──────────────────────────────────────────────

INSERT INTO community.report_images (id, report_id, image_url, uploaded_at)
SELECT
  gen_random_uuid(),
  r.id,
  'https://cdn.example.com/reports/img_' || substr(md5(random()::text), 1, 8) || '.jpg',
  now() - (floor(random()*240)::int) * INTERVAL '1 hour'
FROM generate_series(1, 100) AS gs
CROSS JOIN LATERAL (
  SELECT id
  FROM community.product_reports pr
  WHERE (SELECT count(*) FROM community.report_images WHERE report_id = pr.id) < 5
  ORDER BY random()
  LIMIT 1
) r;
