import pandas as pd

from models.graduate_quality import (
    JOB_TYPE_COL,
    EMPLOYMENT_STATUS_COL,
    SECTOR_COL,
    INDUSTRY_COL,
    SALARY_COL,
    TIME_TO_JOB_COL,
    calculate_quality_insights,
    default_quality_payload,
)


def _df(row):
    return pd.DataFrame([row])


def test_empty_dataframe_returns_default_payload():
    payload = calculate_quality_insights(pd.DataFrame())
    reference = default_quality_payload()
    payload['meta']['generated_at'] = 'stub'
    reference['meta']['generated_at'] = 'stub'
    assert payload == reference


def test_high_quality_graduate_classified_correctly():
    row = {
        JOB_TYPE_COL: 'Bekerja dalam bidang pengajian',
        EMPLOYMENT_STATUS_COL: 'Pekerja tetap',
        SECTOR_COL: 'Sektor Swasta (Syarikat Tempatan, Syarikat Multinasional)',
        INDUSTRY_COL: 'Teknologi Maklumat & Telekomunikasi',
        SALARY_COL: 'RM5,000 ke atas',
        TIME_TO_JOB_COL: '3 - 6 bulan'
    }
    payload = calculate_quality_insights(_df(row))

    assert payload['qualityBands'][0]['count'] == 1
    assert payload['meta']['high_quality_pct'] == 100.0
    assert payload['criteria'][0]['average_score'] == 2.0


def test_low_quality_graduate_classified_correctly():
    row = {
        JOB_TYPE_COL: 'Tidak bekerja',
        EMPLOYMENT_STATUS_COL: 'Pekerja ekonomi gig (contoh: Grab, freelancer, Shopee seller)',
        SECTOR_COL: 'Ekonomi Gig & Freelancing',
        INDUSTRY_COL: 'Ekonomi Gig & Freelancing',
        SALARY_COL: 'Kurang daripada RM1,500',
        TIME_TO_JOB_COL: 'Lebih dari 1 tahun'
    }
    payload = calculate_quality_insights(_df(row))

    assert payload['qualityBands'][-1]['count'] == 1
    assert payload['meta']['low_quality_pct'] == 100.0


def test_entrepreneurial_signal_counts_as_job_creator():
    row = {
        JOB_TYPE_COL: 'Mengusahakan perniagaan sendiri',
        EMPLOYMENT_STATUS_COL: 'Usahawan',
        SECTOR_COL: 'Sektor Keusahawanan (Menjalankan perniagaan sendiri)',
        INDUSTRY_COL: 'Perniagaan, Keusahawanan & Perdagangan',
        SALARY_COL: 'RM3,000 - RM4,999',
        TIME_TO_JOB_COL: 'Kurang dari 3 bulan'
    }
    payload = calculate_quality_insights(_df(row))

    entrepreneur_card = next(
        criterion for criterion in payload['criteria']
        if criterion['id'] == 'entrepreneurial_impact'
    )

    assert payload['meta']['entrepreneurial_pct'] == 100.0
    assert entrepreneur_card['average_score'] == 2.0
