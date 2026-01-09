# Cultural Weaponisation Ukraine Benchmark

A comprehensive research project analyzing Wikipedia article edits related to Ukraine, focusing on cultural weaponisation patterns, user behavior, and article policy evolution.

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Wikipedia API Library](#wikipedia-api-library)
- [Usage Examples](#usage-examples)
- [Data Organization](#data-organization)
- [Notebooks](#notebooks)
- [Modules Documentation](#modules-documentation)

## Overview

This repository contains tools and analyses for studying Wikipedia article edits, with a focus on:
- **User Analysis**: User contributions, metadata, and behavior patterns
- **Article Policy Analysis**: Protection status, quality grades, importance ratings, and vital levels
- **Network Analysis**: User interaction networks and clustering

## Repository Structure

```
.
├── src/                          # Source code library
│   ├── wikipedia/                # Wikipedia API library
│   │   ├── client.py             # Base API client
│   │   ├── users.py              # User-related functions
│   │   ├── pages.py              # General page functions
│   │   └── articles.py           # Article policy API functions
│   └── article_policy/           # Article policy analysis
│       ├── protection.py         # Protection status analysis
│       ├── quality_grade.py      # Quality grade (class) analysis
│       ├── importance.py         # Importance rating analysis
│       ├── vital_level.py        # Vital level analysis
│       ├── plotting.py           # Visualization functions
│       ├── matching.py           # Data matching utilities
│       └── utils.py              # Shared utilities
├── notebooks/                    # Jupyter notebooks
│   ├── Policy Analysis/          # Article policy analysis
│   ├── All Users Analysis/       # Small dataset and user behavior analysis
│   ├── Full Database/            # Full dataset analysis
│   ├── Finegrained Analysis/     # Analysis of the finegrained database
│   └── Article Analysis/         # Article Policy Analysis
├── datas/                        # Data files
│   ├── raw/                      # Raw data
│   ├── interim/                  # Processed intermediate data
│   └── final/                    # Final processed datasets
├── plots/                        # Generated visualizations
└── files/                        # Legacy API functions (deprecated)
```

## Installation

### Prerequisites

- Python 3.7+
- pip

### Dependencies

Install required packages:

```bash
pip install pandas matplotlib requests mwparserfromhell
```

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd dhlab-cultural-weaponisation-ukraine-benchmark
```

2. Install the package (optional, for development):
```bash
pip install -e .
```

3. Add `src/` to your Python path in notebooks:
```python
import sys
import os
project_root = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
sys.path.insert(0, os.path.join(project_root, 'src'))
```

## Wikipedia API Library

**Work In Progress**
The repository includes a well-organized Wikipedia API library in `src/wikipedia/` and article policy analysis tools in `src/article_policy/`.

### Core Modules

#### `wikipedia/` - API Functions

- **`client.py`**: Base `WikipediaClient` class with retry logic and rate limiting
- **`users.py`**: User-related functions (metadata, revisions, contributions)
- **`pages.py`**: General page functions (wikitext, HTML parsing)
- **`articles.py`**: Article policy API functions (creation date, protection, talk pages)

#### `article_policy/` - Analysis Functions

- **`protection.py`**: Protection status timeline building and analysis
- **`quality_grade.py`**: Quality grade (class) extraction and timeline
- **`importance.py`**: Importance rating extraction and timeline
- **`vital_level.py`**: Vital level extraction and timeline
- **`plotting.py`**: Visualization functions for all policy metrics
- **`matching.py`**: Functions to match policy features with edit dataframes
- **`utils.py`**: Shared utilities for metadata extraction

## Data Organization

### Data Directory Structure

- **`datas/raw/`**: Raw data files (CSV, JSON, etc.)
- **`datas/interim/`**: Processed intermediate data
  - `All Users Analysis/`: User analysis results
  - `Policy Analysis/`: Article policy analysis results
  - `Full Database/`: Full dataset analysis results
- **`datas/final/`**: Final processed datasets ready for analysis
  - `full_db_preprocess.csv`: Full preprocessed dataset
  - `small_db_preprocess.csv`: Smaller subset

### Data Formats

- **CSV files**: Main data format for tabular data
- **JSON/JSONL**: For revision data and API responses
- **GraphML**: For network analysis graphs

## Notebooks

### Policy Analysis

- **`article_analysis_new.ipynb`**: Main notebook using the new library (recommended)
- **`article_analysis_full_db.ipynb`**: Original analysis notebook
- **`protection_analysis.ipynb`**: Protection status analysis
- **`grade_analysis.ipynb`**: Quality grade analysis

### User Analysis

- **`All Users Analysis/`**: User behavior, contributions, and metadata analysis
- **`Full Database/users_analysis.ipynb`**: Comprehensive user analysis

### Other Analyses

- **`ip_localisation.ipynb`**: IP geolocation analysis
- **`graph_leiden_analysis.ipynb`**: Network analysis using Leiden algorithm

## Modules Documentation

### Wikipedia API Module (`src/wikipedia/`)

#### Client

```python
from wikipedia import WikipediaClient

client = WikipediaClient(
    user_agent="YourApp/1.0 (contact@example.com)",
    sleep=0.5  # Rate limiting delay
)
```

#### User Functions

- `get_user_metadata(username)`: Get user metadata (groups, editcount, registration, etc.)
- `get_user_revisions(username, max_edits=None)`: Get all edits by a user
- `get_all_bots()`: Get list of all bot usernames

#### Article Functions

- `get_article_creation_date(title)`: Get article creation date and first revision
- `get_article_protection_status(title)`: Get current protection status
- `get_article_protection_history(title)`: Get full protection history
- `fetch_talk_revisions(title)`: Fetch all talk page revisions

### Article Policy Module (`src/article_policy/`)

#### Protection Functions

- `build_protection_timeline(title)`: Build chronological protection timeline
- `timelines_to_dataframe(timelines)`: Convert timelines to DataFrame
- `match_protect_feature_with_df(protect_df, edit_df)`: Match protection with edits

#### Quality Grade Functions

- `extract_article_grade_timeline(title)`: Extract quality grade timeline
- `grade_timelines_to_dataframe(timelines)`: Convert to DataFrame

#### Importance Functions

- `extract_article_importance_timeline(title)`: Extract importance timeline
- `importance_timelines_to_dataframe(timelines)`: Convert to DataFrame

#### Vital Level Functions

- `extract_article_vital_timeline(title)`: Extract vital level timeline
- `vital_timelines_to_dataframe(timelines)`: Convert to DataFrame

#### Plotting Functions

- `plot_protection_timelines(timelines, save_path=None)`: Plot protection timelines
- `plot_grade_quality_change(timelines, save_path=None)`: Plot quality evolution
- `plot_importance_change(timelines, save_path=None)`: Plot importance evolution
- `plot_vital_level_change_from_df(df, save_path=None)`: Plot vital level evolution
- `plot_weap_vs_protection(df, save_path=None)`: Plot weaponisation vs protection
- `plot_weap_vs_importance(df, save_path=None)`: Plot weaponisation vs importance
- `plot_weap_vs_grade(df, save_path=None)`: Plot weaponisation vs grade
- `plot_weap_vs_vital(df, save_path=None)`: Plot weaponisation vs vital level

#### Matching Functions

- `match_features_with_df(grade_df, importance_df, vital_df, edit_df)`: Match all policy features with edit dataframe

## Visualization

All plotting functions support saving figures:

```python
plot_protection_timelines(
    timelines,
    save_path="plots/protection_timeline.png"
)
```

Plots are saved to the `plots/` directory, organized by analysis type.

## 👥 Authors

Maxime Garambois [maximegrmbs]

## 🙏 Acknowledgments

[emanuelaboros]

