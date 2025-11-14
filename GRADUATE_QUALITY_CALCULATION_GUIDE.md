# Graduate Quality Calculation Guide

_Last verified against frontend `/Website/templates/dashboard.html`, scoring core `/models/graduate_quality.py`, and API wiring `/blueprints/dashboard.py` on 14 November 2025._ Use this document to confirm the six scoring criteria that power the seven right-side graduate quality cards and to document every calculation for audit.

## Required Data Inputs
Collect the raw answers from the questionnaire columns below before scoring:
- `Apakah jenis pekerjaan anda sekarang`
- `Apakah status pekerjaan anda sekarang?`
- `Apakah sektor pekerjaan anda?`
- `Berapakah julat gaji bulanan anda sekarang?`
- `Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?`
- `Apakah industri pekerjaan anda sekarang?`

## Dataset Reference & Column Mapping
- **Dataset**: `data/Questionnaire.xlsx` (latest refresh referenced in this guide: 14 Nov 2025, 39 graduan).
- **Core columns feeding each criterion:**
  1. **Jawatan (Position Alignment)** – `Apakah jenis pekerjaan anda sekarang`, `Apakah status pekerjaan anda sekarang?`, `Apakah sektor pekerjaan anda?`
  2. **Gaji (Salary Progression)** – `Berapakah julat gaji bulanan anda sekarang?`
  3. **Jenis Syarikat / Majikan** – `Apakah sektor pekerjaan anda?`
  4. **Tempoh Dapat Kerja** – `Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?`
  5. **Jenis Industri** – `Apakah industri pekerjaan anda sekarang?`
  6. **Status Keusahawanan** – `Apakah jenis pekerjaan anda sekarang`, `Apakah status pekerjaan anda sekarang?`, `Apakah sektor pekerjaan anda?`
- **Processing flow**:
  1. Read `Questionnaire.xlsx` into a dataframe.
  2. Apply `_score_*` helpers from `models/graduate_quality.py` to each row using the column names above.
  3. Sum the six scores to obtain each graduate’s total (max 12).
  4. Aggregate counts, percentages, averages, and quality bands via `calculate_quality_insights`.
  5. Expose the payload through `/dashboard/api/quality-insights` for the frontend and documentation snapshots.

## Scoring Rules (source of truth: `models/graduate_quality.py`)
Each criterion feeds a score between 0 and 2 into `/dashboard/api/quality-insights` and is rendered by `qualityCriteria` in `dashboard.html`.

### 1. Position Alignment (0-2 points)
Backend function: `_score_job_alignment`. Graduan mesti bekerja dalam bidang berkaitan dan sekurang-kurangnya pada tahap Eksekutif.

| Skor | Tahap Jawatan                                      | Penjelasan                          |
|------|----------------------------------------------------|-------------------------------------|
| 0    | Bukan dalam bidang / bawah eksekutif               | Tidak relevan dengan kelayakan      |
| 1    | Eksekutif dalam bidang berkaitan                   | Minimum yang diterima               |
| 2    | Pengurus Muda / Pakar Teknikal dalam bidang        | Menunjukkan kemajuan kerjaya        |

### 2. Salary Assessment (0-2 points)
Backend function: `_score_salary`. Gaji semasa perlu ≥ RM3,000 dan menunjukkan peningkatan daripada gaji permulaan.

| Skor | Gaji Semasa             | Penjelasan                            |
|------|-------------------------|---------------------------------------|
| 0    | < RM3,000               | Tidak kompetitif                      |
| 1    | RM3,000 - RM4,000       | Gaji sederhana, ikut pasaran          |
| 2    | > RM4,000               | Gaji tinggi, menunjukkan nilai tambah |

### 3. Company Type (0-2 points)
Backend function: `_score_employer`. Fokus pada organisasi berskala besar dan berstruktur.

| Skor | Jenis Syarikat                    | Penjelasan                                 |
|------|-----------------------------------|--------------------------------------------|
| 0    | Mikro / tidak berdaftar           | Risiko rendah pembangunan kerjaya          |
| 1    | SME / syarikat tempatan           | Stabil tetapi terhad                       |
| 2    | GLC / MNC / syarikat tersenarai   | Peluang pembangunan tinggi & gaji kompetitif |

### 4. Employment Duration (0-2 points)
Backend function: `_score_time_to_job`. Mengukur tempoh serta keselarasan jawatan pertama.

| Skor | Tempoh & Kesesuaian                        | Penjelasan                              |
|------|--------------------------------------------|-----------------------------------------|
| 0    | > 12 bulan / jawatan tidak selaras         | Tidak menunjukkan kebolehpasaran        |
| 1    | 7 - 12 bulan / jawatan separa selaras      | Sederhana                               |
| 2    | <= 6 bulan / jawatan selaras               | Menunjukkan readiness & padanan yang baik |

### 5. Industry Type (0-2 points)
Backend function: `_score_industry`. Graduan digalakkan berada dalam industri strategik yang sedang berkembang.

| Skor | Jenis Industri                                | Penjelasan                                       |
|------|-----------------------------------------------|--------------------------------------------------|
| 0    | Industri stabil / tradisional                 | Kurang relevan dengan transformasi ekonomi       |
| 1    | Industri umum / sokongan                      | Ada potensi                                      |
| 2    | Industri strategik (High Growth High Value)   | Menyokong dasar negara & masa depan pekerjaan    |

**Rujukan industri utama:** kewangan, pembuatan/perkilangan, F&B, pembinaan, perkhidmatan, serta kluster HGHV (AI, Renewable Energy, Digital & Technology, Halal).

### 6. Entrepreneurial Status (0-2 points)
Backend function: `_score_entrepreneurial`. Menilai sama ada graduan mencipta pekerjaan.

| Skor | Status Graduan                         | Penjelasan                                 |
|------|----------------------------------------|--------------------------------------------|
| 0    | Tiada aktiviti keusahawanan            | Tidak menjana impak berganda               |
| 1    | Berniaga sendiri (solo)                | Ada inisiatif kendiri                      |
| 2    | Berniaga dan menggaji pekerja lain     | Menunjukkan impak ekonomi & kepimpinan     |

### 7. Quality Category (displayed as the 7th card)
Backend functions: `calculate_quality_insights`, `default_quality_payload` (both inside `models/graduate_quality.py`), plus frontend `ensureSevenCriteria`
- High Quality Graduate: total score >= 10
- Moderate Quality Graduate: total score 7-9
- Low Quality / Non-competitive: total score <= 6

Maximum possible score remains 12 (six criteria).

## Calculation Workflow (document every step)
1. Capture the raw questionnaire values listed under Required Data Inputs.
2. Map each value to the scoring buckets above and note the justification (attach salary slip, job offer, etc.).
3. Enter the six scores into the calculation sheet or backend payload.
4. Sum the scores to obtain `Total_Score` and derive the quality category.
5. Store the working, evidence, API response, and timestamp in the graduate folder for audit.
6. Re-run the calculation whenever any of the six inputs change.

## Worked Example (step-by-step log)
Graduate answers: `Bekerja dalam bidang pengajian` + `Pekerja tetap`, salary `> RM4,000`, sector `Sektor Swasta ...`, hired in `3 - 6 bulan`, industry `Teknologi Maklumat & Telekomunikasi`, not an entrepreneur.

```
1. Position Alignment  = 2 (in-field & Pekerja tetap)
2. Salary Assessment   = 2 (> RM4,000 bucket)
3. Company Type        = 2 (Sektor Swasta ...)
4. Employment Duration = 2 (3 - 6 bulan <= 6 months)
5. Industry Type       = 2 (Strategic ICT)
6. Entrepreneurial     = 0 (no entrepreneurial signal)
Total_Score            = 10 => High Quality Graduate
```

## Frontend <-> Backend Verification Log (14 Nov 2025)
1. **Frontend binding** - Confirmed the seven cards render from `qualityCriteria.slice(0, 7)` inside `Website/templates/dashboard.html:145-248`, using `criterion.title`, `criterion.average_score`, and `distribution` exactly as delivered by the API. Navigation indicators at lines 233-250 reference the same array.
2. **Data fetch** - Traced `loadData()` in `dashboard.html:870-924`, which calls `fetch('/dashboard/api/quality-insights')` and updates `qualityCriteria`, `qualityBands`, and `qualityMeta` before forcing a seventh "combined" card via `ensureSevenCriteria` (`dashboard.html:800-866`).
3. **Backend scoring** - Reviewed `_score_job_alignment` through `_score_entrepreneurial` plus `calculate_quality_insights` inside `models/graduate_quality.py` to ensure each criterion relies on the questionnaire columns listed above and outputs the `/dashboard/api/quality-insights` payload used by the frontend. `blueprints/dashboard.py` now forwards the filtered dataframe to this module.
4. **Quality bands** - Verified both `default_quality_payload` and `calculate_quality_insights` return the same thresholds (`>= 10`, `7 - 9`, `<= 6`) consumed by the frontend band banners (`qualityBands`).
5. **Unit tests** - Added regression coverage in `tests/test_graduate_quality.py` for empty datasets, high/low classifications, and entrepreneurial scoring so code changes stay aligned with AGENTS.md.
6. **Audit trail** - Recorded this verification in this guide so future checks can reference the exact files, functions, and dates.

## Verification & Audit Notes
- Every score must be backed by evidence (HR letter, contract, payslip, etc.).
- Retain the JSON response from `/dashboard/api/quality-insights` alongside manual calculations for reproducibility.
- Re-run backend tests (e.g., `test_quality_api.py` and `pytest tests/test_graduate_quality.py`) plus a manual sample whenever questionnaire options change.
- Maintain confidentiality and restricted access to calculation logs.

## Current Dataset Calculation Breakdown (Questionnaire.xlsx refresh on 14 Nov 2025, 39 graduan)
Source: `/dashboard/api/quality-insights` generated at `2025-11-14T14:01:30Z` using the latest `Questionnaire.xlsx`. Percentages below are share of 39 validated graduates; counts are shown in parentheses for audit.
**Average_pct rule:** every criterion has a maximum of 2 points, so `average_pct = (average_score / 2) × 100`. Each section below shows the computed value to mirror the API payload.

### 1. Job Alignment (Jawatan & Padanan Bidang)
Scoring:
- 2 points – “Pengurus Muda / Pakar Teknikal dalam bidang”: 53.8% (21/39)
- 1 point – “Eksekutif dalam bidang berkaitan”: 5.1% (2/39)
- 0 points – “Bukan dalam bidang / bawah eksekutif”: 41.0% (16/39)

| Skor | Tahap Jawatan                                | % (Bil. graduan) |
|------|----------------------------------------------|------------------|
| 2    | Pengurus Muda / Pakar Teknikal dalam bidang  | 53.8% (21)       |
| 1    | Eksekutif dalam bidang berkaitan             | 5.1% (2)         |
| 0    | Bukan dalam bidang / bawah eksekutif         | 41.0% (16)       |

Calculation:
`Average score = (53.8% × 2) + (5.1% × 1) + (41.0% × 0) = 1.13` ✔ matches API `average_score`.
`Average_pct = (1.13 / 2) × 100 = 56.5%`.

### 2. Salary Progression (Gaji Semasa & Perkembangan)
Scoring:
- 2 points – “> RM4,000”: 7.7% (3/39)
- 1 point – “RM3,000 - RM4,000”: 46.2% (18/39)
- 0 points – “< RM3,000”: 46.2% (18/39)

| Skor | Julat Gaji Semasa         | % (Bil. graduan) |
|------|---------------------------|------------------|
| 2    | > RM4,000                 | 7.7% (3)         |
| 1    | RM3,000 - RM4,000         | 46.2% (18)       |
| 0    | < RM3,000                 | 46.2% (18)       |

Calculation:
`Average score = (7.7% × 2) + (46.2% × 1) + (46.2% × 0) = 0.62`.
`Average_pct = (0.62 / 2) × 100 = 31.0%`.

### 3. Employer Quality (Jenis Syarikat / Majikan)
Scoring:
- 2 points – “GLC / MNC / syarikat tersenarai”: 92.3% (36/39)
- 1 point – “SME / syarikat tempatan”: 2.6% (1/39)
- 0 points – “Mikro / tidak berdaftar”: 5.1% (2/39)

| Skor | Jenis Majikan                        | % (Bil. graduan) |
|------|--------------------------------------|------------------|
| 2    | GLC / MNC / syarikat tersenarai      | 92.3% (36)       |
| 1    | SME / syarikat tempatan              | 2.6% (1)         |
| 0    | Mikro / tidak berdaftar              | 5.1% (2)         |

Calculation:
`Average score = (92.3% × 2) + (2.6% × 1) + (5.1% × 0) = 1.87`.
`Average_pct = (1.87 / 2) × 100 = 93.5%`.

### 4. Time to Employment (Tempoh Mendapat Pekerjaan)
Scoring:
- 2 points – “<= 6 bulan / jawatan selaras”: 74.4% (29/39)
- 1 point – “7 - 12 bulan / jawatan separa selaras”: 7.7% (3/39)
- 0 points – “> 12 bulan / jawatan tidak selaras”: 17.9% (7/39)

| Skor | Tempoh & Kesesuaian                      | % (Bil. graduan) |
|------|------------------------------------------|------------------|
| 2    | ≤ 6 bulan / jawatan selaras              | 74.4% (29)       |
| 1    | 7 – 12 bulan / jawatan separa selaras    | 7.7% (3)         |
| 0    | > 12 bulan / jawatan tidak selaras       | 17.9% (7)        |

Calculation:
`Average score = (74.4% × 2) + (7.7% × 1) + (17.9% × 0) = 1.56`.
`Average_pct = (1.56 / 2) × 100 = 78.0%`.

### 5. Industry Relevance (Jenis Industri Strategik)
Scoring:
- 2 points – “Industri strategik (High Growth High Value)”: 64.1% (25/39)
- 1 point – “Industri umum / sokongan”: 30.8% (12/39)
- 0 points – “Industri stabil / tradisional”: 5.1% (2/39)

| Skor | Jenis Industri                               | % (Bil. graduan) |
|------|----------------------------------------------|------------------|
| 2    | Industri strategik (High Growth High Value)  | 64.1% (25)       |
| 1    | Industri umum / sokongan                     | 30.8% (12)       |
| 0    | Industri stabil / tradisional                | 5.1% (2)         |

Calculation:
`Average score = (64.1% × 2) + (30.8% × 1) + (5.1% × 0) = 1.59`.
`Average_pct = (1.59 / 2) × 100 = 79.5%`.

### 6. Entrepreneurial Impact (Graduan Sebagai Pencipta Pekerjaan)
Scoring:
- 2 points – “Berniaga dan menggaji pekerja lain”: 2.6% (1/39)
- 1 point – “Berniaga sendiri (solo)”: 0.0% (0/39)
- 0 points – “Tiada aktiviti keusahawanan”: 97.4% (38/39)

| Skor | Status Keusahawanan                | % (Bil. graduan) |
|------|------------------------------------|------------------|
| 2    | Berniaga dan menggaji pekerja lain | 2.6% (1)         |
| 1    | Berniaga sendiri (solo)            | 0.0% (0)         |
| 0    | Tiada aktiviti keusahawanan        | 97.4% (38)       |

Calculation:
`Average score = (2.6% × 2) + (0.0% × 1) + (97.4% × 0) = 0.05`.
`Average_pct = (0.05 / 2) × 100 = 2.5%`.

### 7. Quality Category (Kategori Kualiti)
Scoring:
- Graduan Berkualiti Tinggi (≥ 10 mata): 5.1% (2/39)
- Graduan Berkualiti Sederhana (7 – 9 mata): 51.3% (20/39)
- Graduan Berkualiti Rendah (≤ 6 mata): 43.6% (17/39)

| Kategori                                | Skor Jumlah | % (Bil. graduan) |
|-----------------------------------------|-------------|------------------|
| Graduan Berkualiti Tinggi               | ≥ 10        | 5.1% (2)         |
| Graduan Berkualiti Sederhana            | 7 – 9       | 51.3% (20)       |
| Graduan Berkualiti Rendah / Tidak Kompetitif | ≤ 6   | 43.6% (17)       |

Calculation:
- Σ skor individu (jumlah semua skor graduan) = `265.98`. Bahagian ini datang daripada menambah keenam-enam skor setiap graduan atau, lebih mudah, `meta.average_score × meta.total_graduates = 6.82 × 39 ≈ 265.98`.
- Skor purata keseluruhan = `Σ skor individu ÷ total graduan = 265.98 ÷ 39 = 6.82`, iaitu nilai `meta.average_score` dalam API.
- Peratus purata kad ke-7 = `(6.82 / 12) × 100 = 56.8%`, kerana maksimum tugasan ialah 12 mata (6 kriteria × 2 mata).
- Semakan band: `2 (≥10) + 20 (7–9) + 17 (≤6) = 39`, jadi High/Medium/Low sentiasa menyamai jumlah responden.
