# SoundSleep 😴
SoundSleep is a Python package for extracting comprehensive sleep features from wearable or sleep stage-labeled data. It enables detailed analysis of sleep architecture, continuity, timing, and efficiency across nights and individuals. Designed for researchers, developers, and health data enthusiasts, it simplifies feature extraction from raw segmented data.

# Installation
You can install directly from PyPI:
```bash
pip install sound-sleep
```

# Quickstart
```python
from sound_sleep import (
    SleepFeaturesExtractor,
    load_csv_file,
    build_dict_all_day_level_features,
    build_dict_day_level_features,
    build_dict_all_participant_level_features,
    build_dict_participant_level_features,
)
from sound_sleep.io.exports import save_feature_dicts_to_csv

# Load your data
df = load_csv_file("path/to/your/sleep_data.csv")

# Initialize the feature extractor
extractor = SleepFeaturesExtractor(df, verbose=True)

# Extract day-level features for all participants
all_day_level = build_dict_all_day_level_features(extractor)
save_feature_dicts_to_csv(all_day_level, "all_day_level_features.csv")

# Extract day-level features for one participant
participant_day_level = build_dict_day_level_features(extractor, participant_id=101)
save_feature_dicts_to_csv(participant_day_level, "participant_101_day_features.csv")

# Extract participant-level summary features for all participants
all_participant_level = build_dict_all_participant_level_features(extractor)
save_feature_dicts_to_csv(all_participant_level, "all_participant_level_features.csv")

# Extract participant-level summary for one participant
participant_summary = build_dict_participant_level_features(extractor, participant_id=101)
save_feature_dicts_to_csv([participant_summary], "participant_101_summary.csv")
```

See the "CSV format" section below for instructions on how your data must be formatted.

# Features Extracted
## Sleep Duration and Timing
- **Bedtime**: Clock time of going to bed.
- **Risetime**: Clock time of waking up.
- **Time in Bed (TIB)**: Duration between Bedtime and Risetime.
- **Sleep Onset Time**: First time falling asleep.
- **Wake Time**: Final time waking up from sleep.
- **Total Sleep Time (TST)**: Total time asleep (excluding awakenings).
- **Midpoint of Sleep**: Midpoint between sleep onset and wake.
- **Sleep Onset Latency (SOL)**: Duration between Bedtime and Sleep Onset.
- **Time Between Wake Time and Risetime**: Duration spent awake in bed before actually getting up.

## Sleep Architecture
- **Time in Light Sleep**
- **Time in Deep Sleep**
- **Time in REM Sleep**
- **% Light Sleep**
- **% Deep Sleep**
- **% REM Sleep**
- **Longest Light Sleep Stage Period**
- **Longest Deep Sleep Stage Period**
- **Longest REM Sleep Stage Period**

## Sleep Continuity (Fragmentation)
- **Wake After Sleep Onset (WASO)**: Time awake after sleep starts
- **Number of Awakenings**
- **Average Duration of Awakenings**
- **Sleep Fragmentation Index**: Awakenings / TST
- **Sleep Fragmentation Ratio**: Awakenings / Num Sleep Stages
- **Ratio between Wake After Sleep Onset time and Total Sleep Time**
- **Ratio between Sleep Onset Latency and Time in Bed**
- **Average Total Sleep Time**

## Sleep Efficiency and Regularity
- **Sleep Efficiency**: (TST / TIB) × 100
- **Sleep Onset Regularity**: Circular std dev of onset time across days
- **Wake Time Regularity**: Circular std dev of wake time across days
- **Bedtime Regularity**
- **Midpoint Sleep Regularity**

# CSV Format
The input CSV must include the following columns:

| Column              | Type         | Description                              |
|---------------------|--------------|------------------------------------------|
| `participant_id`    | int or str   | Unique ID per participant                |
| `day_number`        | int          | Study or recording day number            |
| `sleep_stage_state` | str or int   | Stage label (e.g., "light", "rem")       |
| `start_time`        | timestamp    | Segment start datetime                   |
| `end_time`          | timestamp    | Segment end datetime                     |
| `duration_minutes`  | float        | Duration of sleep segment in minutes     |
| `start_date`        | date         | Date of `start_time`                     |
| `end_date`          | date         | Date of `end_time`                       |
| `start_time_of_day` | time         | Clock time of `start_time`               |
| `end_time_of_day`   | time         | Clock time of `end_time`                 |

Use the load_csv_file(filepath) utility from sound_sleep to correctly parse, format, and clean the dataset.
Note: This function automatically removes duplicate rows using drop_duplicates() to prevent inflated sleep durations due to accidental row duplication.

To export feature dictionaries to CSV:
```python
from sound_sleep.io.exports import save_feature_dicts_to_csv
save_feature_dicts_to_csv(list_of_dicts, "output.csv")
```

# Contributing
We welcome improvements, bug reports, and feature requests! Please open an issue or submit a pull request.

To test locally:
```bash
pytest tests/
```
or use sample usage from the Quickstart with synthetic data.

If you wish to develop in your own environment:
```bash
git clone https://github.com/theBigTao/SoundSleep.git
cd sound-sleep
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
```

# Developing
## Extending Features
1. Create a new method in `SleepFeaturesExtractor` (in `sleep_features.py`).
2. Add documentation.
3. Optionally include it in a dictionary in `aggregators.py` to compute features across days or participants.
4. Add corresponding tests in `tests/`.

## Aggregators
High-level aggregators live in `sound_sleep/aggregators.py`. These functions group together multiple low-level feature functions into:

- Day-level aggregators:
  - `build_dict_day_level_features(extractor, participant_id)`
  - `build_dict_all_day_level_features(extractor)`

- Participant-level aggregators:
  - `build_dict_participant_level_features(extractor, participant_id)`
  - `build_dict_all_participant_level_features(extractor)`

- Modular one-day functions:
  - `compute_all_features(extractor, participant_id, day_number)`
  - `compute_sleep_timing_functions(...)`
  - `compute_sleep_architecture_features(...)`
  - `compute_sleep_continuity_features(...)`
  - `compute_sleep_efficiency_and_regularity(...)`

You can import and use any individual feature function or dictionary-building aggregator directly from the `sound_sleep` namespace.

## New Device Support
Write a parsing function like `load_<device>_data(filepath)` that reformats your device's data into the expected schema. Place it in the `sound_sleep/io/` module.

Example:
```python
from sound_sleep.io import load_fitbit_data

df = load_fitbit_data("fitbit.json")
```

# Running the Package
You can run the complete extraction pipeline using the provided `main.py` script:

```bash
python src/sound_sleep/main.py
```

Make sure the input file path is correctly specified in `main.py`. You can modify `main.py` to run only day-level or only participant-level pipelines.