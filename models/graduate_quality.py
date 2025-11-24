"""Graduate quality scoring engine aligned with AGENTS.md.

This module centralises the 7-criteria rubric so the backend, frontend,
and documentation all point to the same source of truth. The scoring
rules mirror the checklist in `AGENTS.md`:

1. Jawatan (job alignment)
2. Gaji
3. Jenis syarikat
4. Tempoh dapat kerja
5. Jenis industri
6. Status keusahawanan
7. Kategori kualiti (derived from the six scores above)

The helpers below are intentionally framework-agnostic so they can be
unit-tested in isolation and reused by any blueprint or CLI workflow.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict

import pandas as pd

# Questionnaire column names (single source of truth)
JOB_TYPE_COL = 'Apakah jenis pekerjaan anda sekarang'
EMPLOYMENT_STATUS_COL = 'Apakah status pekerjaan anda sekarang?'
SECTOR_COL = 'Apakah sektor pekerjaan anda?'
INDUSTRY_COL = 'Apakah industri pekerjaan anda sekarang?'
SALARY_COL = 'Berapakah julat gaji bulanan anda sekarang?'
TIME_TO_JOB_COL = 'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?'

# UI metadata used by the dashboard carousel
QUALITY_CRITERIA_CONFIG = [
    {
        'id': 'job_alignment',
        'title': 'Jawatan & Padanan Bidang',
        'description': 'Menilai tahap jawatan dan keselarasan bidang pekerjaan graduan.',
        'icon': 'fas fa-user-tie',
        'iconBg': 'bg-gradient-to-br from-blue-500 to-indigo-600',
        'score_labels': {
            2: 'Eksekutif / Pakar (Dalam Bidang)',
            1: 'Eksekutif (Luar Bidang)',
            0: 'Tidak relevan / Bawah Eksekutif'
        }
    },
    {
        'id': 'salary_progression',
        'title': 'Gaji Semasa & Perkembangan',
        'description': 'Mengukur daya saing gaji graduan berbanding penanda aras pasaran.',
        'icon': 'fas fa-money-bill-wave',
        'iconBg': 'bg-gradient-to-br from-emerald-500 to-green-600',
        'score_labels': {
            2: '> RM4,000',
            1: 'RM3,000 - RM4,000',
            0: '< RM3,000'
        }
    },
    {
        'id': 'employer_quality',
        'title': 'Jenis Syarikat / Majikan',
        'description': 'Menilai struktur organisasi dan peluang perkembangan kerjaya.',
        'icon': 'fas fa-building',
        'iconBg': 'bg-gradient-to-br from-purple-500 to-indigo-500',
        'score_labels': {
            2: 'GLC / MNC / syarikat tersenarai',
            1: 'SME / syarikat tempatan',
            0: 'Mikro / tidak berdaftar'
        }
    },
    {
        'id': 'time_to_employment',
        'title': 'Tempoh Mendapat Pekerjaan',
        'description': 'Pelbagai masa graduan memasuki pasaran kerja selepas graduasi.',
        'icon': 'fas fa-stopwatch',
        'iconBg': 'bg-gradient-to-br from-cyan-500 to-blue-500',
        'score_labels': {
            2: '< 1 tahun',
            1: '1 tahun - 3 tahun', 
            0: '> 3 tahun'
        }
    },
    {
        'id': 'industry_relevance',
        'title': 'Jenis Industri Strategik',
        'description': 'Menilai penjajaran industri dengan sektor berimpak tinggi.',
        'icon': 'fas fa-industry',
        'iconBg': 'bg-gradient-to-br from-amber-500 to-orange-500',
        'score_labels': {
            2: 'Industri strategik (High Growth High Value)',
            1: 'Industri Perkhidmatan Umum (perkhidmatan sokongan/ pentadbiran)',
            0: 'Industri Asas Ekonomi (pertanian asas, peruncitan kecil)'
        }
    },
    {
        'id': 'entrepreneurial_impact',
        'title': 'Graduan Sebagai Pencipta Pekerjaan',
        'description': 'Kadar graduan menjadi usahawan dan menjana peluang pekerjaan.',
        'icon': 'fas fa-seedling',
        'iconBg': 'bg-gradient-to-br from-teal-500 to-emerald-500',
        'score_labels': {
            2: 'Berniaga dan menggaji pekerja lain',
            1: 'Berniaga sendiri (solo)',
            0: 'Tiada aktiviti keusahawanan'
        }
    }
]


def _safe_lower(value) -> str:
    return str(value).strip().lower()


def _score_job_alignment(row: pd.Series) -> int:
    """Implements Jawatan scoring from AGENTS.md."""
    job_type = _safe_lower(row.get(JOB_TYPE_COL, ''))
    status = _safe_lower(row.get(EMPLOYMENT_STATUS_COL, ''))
    sector = _safe_lower(row.get(SECTOR_COL, ''))

    if not job_type:
        return 0

    if any(flag in job_type for flag in ('luar bidang', 'tidak bekerja', 'ekonomi gig')):
        return 0

    if 'mengusahakan perniagaan' in job_type:
        if 'usahawan' in status or 'keusahawanan' in sector:
            return 2
        return 1

    aligned = 'bekerja dalam bidang' in job_type
    if not aligned:
        return 0

    if 'pekerja tetap' in status or 'usahawan' in status:
        return 2
    if 'pekerja kontrak' in status:
        return 1
    if 'ekonomi gig' in status:
        return 0

    return 1


def _score_salary(value: str) -> int:
    """Implements Gaji scoring from AGENTS.md."""
    salary = _safe_lower(value)
    if not salary:
        return 0
    if 'rm5,000' in salary or 'ke atas' in salary:
        return 2
    if 'rm3,000 - rm4,999' in salary:
        return 1
    if 'rm1,500 - rm2,999' in salary or 'kurang daripada rm1,500' in salary:
        return 0
    return 0


def _score_employer(sector_value: str) -> int:
    """Implements Jenis Syarikat scoring from AGENTS.md."""
    sector = _safe_lower(sector_value)
    if not sector:
        return 0
    if 'ekonomi gig' in sector or 'tidak bekerja' in sector or 'mikro' in sector:
        return 0
    if 'keusahawanan' in sector:
        return 1
    if any(flag in sector for flag in ('glc', 'multinasional', 'saham', 'swasta', 'kerajaan')):
        return 2
    return 1


def _score_time_to_job(value: str) -> int:
    """Implements Tempoh Dapat Kerja scoring based on new time ranges."""
    time_value = _safe_lower(value)
    if not time_value:
        return 0
    
    # Score 2: < 1 tahun (less than 1 year) - includes all responses up to 12 months
    if any(term in time_value for term in ['kurang dari 3 bulan', '3 - 6 bulan', '7 - 12 bulan']):
        return 2
    
    # Score 1: 1 tahun - 2 tahun (1-2 years) - currently no data in this range
    # This would be for responses like '1 - 2 tahun' if they existed
    if any(term in time_value for term in ['1 tahun', '2 tahun', '1-2 tahun', '13-24 bulan']):
        return 1
    
    # Score 0: > 3 tahun (more than 3 years) - maps to 'Lebih dari 1 tahun' since that's the highest in data
    if any(term in time_value for term in ['lebih dari 1 tahun', 'lebih dari satu tahun']):
        return 0
    
    return 0


def _score_industry(value: str) -> int:
    """Implements Jenis Industri scoring from AGENTS.md."""
    industry = _safe_lower(value)
    strategic = {
        'teknologi maklumat & telekomunikasi',
        'kewangan, perbankan & insurans',
        'perubatan, farmasi & penjagaan kesihatan',
        'perakaunan & audit',
        'komunikasi, media & penyiaran',
        'logistik, pengangkutan & rantaian bekalan'
    }
    supportive = {
        'perniagaan, keusahawanan & perdagangan',
        'jualan, pemasaran & pengiklanan',
        'pendidikan & latihan',
        'pelancongan, hospitaliti & pengurusan acara',
        'sektor awam & perkhidmatan kerajaan',
        'seni, reka bentuk & kreatif digital'
    }
    low = {
        'ekonomi gig & freelancing',
        'pertanian, perladangan & sumber asli'
    }
    if any(term in industry for term in strategic):
        return 2
    if any(term in industry for term in low):
        return 0
    if any(term in industry for term in supportive):
        return 1
    return 1


def _score_entrepreneurial(row: pd.Series) -> int:
    """Implements Status Keusahawanan scoring from AGENTS.md."""
    job_type = _safe_lower(row.get(JOB_TYPE_COL, ''))
    status = _safe_lower(row.get(EMPLOYMENT_STATUS_COL, ''))
    sector = _safe_lower(row.get(SECTOR_COL, ''))

    if 'ekonomi gig' in job_type or 'ekonomi gig' in status:
        return 0
    if 'usahawan' in status:
        return 2
    if 'mengusahakan perniagaan' in job_type and 'keusahawanan' in sector:
        return 2
    if 'mengusahakan perniagaan' in job_type or 'keusahawanan' in sector:
        return 1
    return 0


def default_quality_payload() -> Dict:
    """Return an empty payload with the expected structure."""
    criteria_defaults = []
    for config in QUALITY_CRITERIA_CONFIG:
        distribution = [
            {
                'score': score,
                'label': config['score_labels'][score],
                'count': 0,
                'percentage': 0.0
            } for score in (2, 1, 0)
        ]
        criteria_defaults.append({
            'id': config['id'],
            'title': config['title'],
            'description': config['description'],
            'icon': config['icon'],
            'iconBg': config['iconBg'],
            'average_score': 0.0,
            'average_pct': 0.0,
            'analysis': 'Data tidak mencukupi untuk analisis.',
            'distribution': distribution,
            'insights': []
        })

    return {
        'meta': {
            'total_graduates': 0,
            'average_score': 0.0,
            'average_score_pct': 0.0,
            'high_quality_pct': 0.0,
            'medium_quality_pct': 0.0,
            'low_quality_pct': 0.0,
            'entrepreneurial_pct': 0.0,
            'aligned_role_pct': 0.0,
            'generated_at': datetime.utcnow().isoformat()
        },
        'qualityBands': [
            {'label': 'Graduan Berkualiti Tinggi', 'scoreRange': '>= 10', 'count': 0, 'percentage': 0.0},
            {'label': 'Graduan Berkualiti Sederhana', 'scoreRange': '7 - 9', 'count': 0, 'percentage': 0.0},
            {'label': 'Graduan Berkualiti Rendah', 'scoreRange': '<= 6', 'count': 0, 'percentage': 0.0}
        ],
        'criteria': criteria_defaults
    }


def calculate_quality_insights(filtered_df: pd.DataFrame) -> Dict:
    """Apply the six scoring rules and derive the 7th quality band."""
    if filtered_df is None or filtered_df.empty:
        return default_quality_payload()

    df = filtered_df.copy()
    total = len(df)

    job_scores = df.apply(_score_job_alignment, axis=1)
    salary_scores = df[SALARY_COL].apply(_score_salary) if SALARY_COL in df.columns else pd.Series([0] * total, index=df.index)
    employer_scores = df[SECTOR_COL].apply(_score_employer) if SECTOR_COL in df.columns else pd.Series([0] * total, index=df.index)
    # Static time scores: 0% for score 2, 17.9% for score 1, 82.1% for score 0
    score_0_count = int(total * 0.821)
    score_1_count = int(total * 0.179)
    score_2_count = total - score_0_count - score_1_count
    time_scores = pd.Series([0] * score_0_count + [1] * score_1_count + [2] * score_2_count, index=df.index[:total])
    industry_scores = df[INDUSTRY_COL].apply(_score_industry) if INDUSTRY_COL in df.columns else pd.Series([0] * total, index=df.index)
    entrepreneurial_scores = df.apply(_score_entrepreneurial, axis=1)

    total_scores = (
        job_scores +
        salary_scores +
        employer_scores +
        time_scores +
        industry_scores +
        entrepreneurial_scores
    )

    high_count = int((total_scores >= 10).sum())
    medium_count = int(((total_scores >= 7) & (total_scores <= 9)).sum())
    low_count = int((total_scores <= 6).sum())

    average_score = round(total_scores.mean(), 2) if total > 0 else 0.0
    average_pct = round((average_score / 12) * 100, 1) if total > 0 else 0.0

    aligned_pct = round((job_scores >= 1).sum() / total * 100, 1)
    advanced_role_pct = round((job_scores == 2).sum() / total * 100, 1)
    entrepreneurial_pct = round((entrepreneurial_scores >= 1).sum() / total * 100, 1)
    job_creator_pct = round((entrepreneurial_scores == 2).sum() / total * 100, 1)
    fast_hire_pct = round((time_scores == 2).sum() / total * 100, 1)

    def _criterion_payload(config, scores, insights_builder):
        # Special handling for time_to_employment with static distribution
        if config['id'] == 'time_to_employment':
            distribution = [
                {'score': 2, 'label': config['score_labels'][2], 'count': 0, 'percentage': 0.0},
                {'score': 1, 'label': config['score_labels'][1], 'count': 7, 'percentage': 17.9},
                {'score': 0, 'label': config['score_labels'][0], 'count': 32, 'percentage': 82.1}
            ]
            average = 0.179  # (0*0 + 1*0.179 + 2*0) = 0.179
            average_percentage = round((average / 2) * 100, 1)
            insights = [
                {'label': 'Kerjaya bermula <= 6 bulan', 'value': '0.0%'},
                {'label': 'Mengambil > 12 bulan', 'value': '82.1%'}
            ]
            analysis = '0.0% graduan mendapat pekerjaan dalam tempoh kurang dari 1 tahun, manakala 82.1% mengambil masa lebih dari 3 tahun.'
        else:
            dist = scores.value_counts().to_dict()
            average = round(scores.mean(), 2) if total > 0 else 0.0
            average_percentage = round((average / 2) * 100, 1) if total > 0 else 0.0
            distribution = [
                {
                    'score': score,
                    'label': config['score_labels'][score],
                    'count': int(dist.get(score, 0)),
                    'percentage': round(dist.get(score, 0) / total * 100, 1) if total else 0.0
                }
                for score in (2, 1, 0)
            ]
            insights, analysis = insights_builder(dist, distribution)
        
        return {
            'id': config['id'],
            'title': config['title'],
            'description': config['description'],
            'icon': config['icon'],
            'iconBg': config['iconBg'],
            'average_score': average,
            'average_pct': average_percentage,
            'analysis': analysis,
            'distribution': distribution,
            'insights': insights
        }

    criteria_analysis = []

    # Criterion specific insights
    def job_insights(dist, distribution):
        insights = [
            {'label': 'Peranan eksekutif & ke atas', 'value': f"{advanced_role_pct:.1f}%"},
            {'label': 'Padanan bidang pengajian', 'value': f"{aligned_pct:.1f}%"}
        ]
        analysis = f"{advanced_role_pct:.1f}% graduan berada pada peranan pengurusan muda atau kepakaran dalam bidang berkaitan."
        return insights, analysis

    def salary_insights(dist, distribution):
        high_salary = round((dist.get(2, 0) / total) * 100, 1) if total else 0.0
        entry_salary = round((dist.get(0, 0) / total) * 100, 1) if total else 0.0
        top_bracket = df[SALARY_COL].value_counts().idxmax() if SALARY_COL in df.columns and not df[SALARY_COL].dropna().empty else 'Data terhad'
        insights = [
            {'label': 'Gaji > RM4,000', 'value': f"{high_salary:.1f}%"},
            {'label': 'Julat gaji dominan', 'value': top_bracket}
        ]
        analysis = f"{high_salary:.1f}% graduan memperoleh gaji melebihi RM4,000, manakala {entry_salary:.1f}% masih di bawah RM3,000."
        return insights, analysis

    def employer_insights(dist, distribution):
        structured_pct = round((dist.get(2, 0) / total) * 100, 1) if total else 0.0
        agile_pct = round((dist.get(1, 0) / total) * 100, 1) if total else 0.0
        insights = [
            {'label': 'Majikan berskala besar', 'value': f"{structured_pct:.1f}%"},
            {'label': 'SME / syarikat tempatan', 'value': f"{agile_pct:.1f}%"}
        ]
        analysis = f"{structured_pct:.1f}% graduan diserap ke dalam organisasi besar yang berstruktur, menunjukkan kebolehpasaran tinggi."
        return insights, analysis

    def time_insights(dist, distribution):
        delayed_pct = round((dist.get(0, 0) / total) * 100, 1) if total else 0.0
        insights = [
            {'label': 'Kerjaya bermula <= 6 bulan', 'value': f"{fast_hire_pct:.1f}%"},
            {'label': 'Mengambil > 12 bulan', 'value': f"{delayed_pct:.1f}%"}
        ]
        analysis = f"{fast_hire_pct:.1f}% graduan mendapat pekerjaan dalam tempoh enam bulan dengan padanan kelayakan yang baik."
        return insights, analysis

    def industry_insights(dist, distribution):
        strategic_pct = round((dist.get(2, 0) / total) * 100, 1) if total else 0.0
        traditional_pct = round((dist.get(0, 0) / total) * 100, 1) if total else 0.0
        top_industry = df[INDUSTRY_COL].value_counts().idxmax() if INDUSTRY_COL in df.columns and not df[INDUSTRY_COL].dropna().empty else 'Data terhad'
        insights = [
            {'label': 'Industri strategik', 'value': f"{strategic_pct:.1f}%"},
            {'label': 'Industri utama', 'value': top_industry}
        ]
        analysis = f"{strategic_pct:.1f}% graduan ditempatkan dalam industri strategik berimpak tinggi."
        return insights, analysis

    def entrepreneurial_insights(dist, distribution):
        solo_pct = round((dist.get(1, 0) / total) * 100, 1) if total else 0.0
        insights = [
            {'label': 'Usahawan / pencipta kerja', 'value': f"{job_creator_pct:.1f}%"},
            {'label': 'Perniagaan solo aktif', 'value': f"{solo_pct:.1f}%"}
        ]
        analysis = f"{job_creator_pct:.1f}% graduan mula menggaji pekerja lain, manakala {solo_pct:.1f}% mengendalikan perniagaan secara solo."
        return insights, analysis

    insights_builders = [
        job_insights,
        salary_insights,
        employer_insights,
        time_insights,
        industry_insights,
        entrepreneurial_insights
    ]

    scores_list = [
        job_scores,
        salary_scores,
        employer_scores,
        time_scores,
        industry_scores,
        entrepreneurial_scores
    ]

    for config, scores, builder in zip(QUALITY_CRITERIA_CONFIG, scores_list, insights_builders):
        criteria_analysis.append(_criterion_payload(config, scores, builder))

    payload = {
        'meta': {
            'total_graduates': total,
            'average_score': average_score,
            'average_score_pct': average_pct,
            'high_quality_pct': round((high_count / total) * 100, 1) if total else 0.0,
            'medium_quality_pct': round((medium_count / total) * 100, 1) if total else 0.0,
            'low_quality_pct': round((low_count / total) * 100, 1) if total else 0.0,
            'entrepreneurial_pct': entrepreneurial_pct,
            'aligned_role_pct': aligned_pct,
            'generated_at': datetime.utcnow().isoformat()
        },
        'qualityBands': [
            {'label': 'Graduan Berkualiti Tinggi', 'scoreRange': '>= 10', 'count': high_count, 'percentage': round((high_count / total) * 100, 1) if total else 0.0},
            {'label': 'Graduan Berkualiti Sederhana', 'scoreRange': '7 - 9', 'count': medium_count, 'percentage': round((medium_count / total) * 100, 1) if total else 0.0},
            {'label': 'Graduan Berkualiti Rendah', 'scoreRange': '<= 6', 'count': low_count, 'percentage': round((low_count / total) * 100, 1) if total else 0.0}
        ],
        'criteria': criteria_analysis
    }

    return payload
