from .sleep_features import SleepFeaturesExtractor
from tqdm import tqdm

def compute_sleep_timing_functions(extractor: SleepFeaturesExtractor, participant_id, day_number):
    """
    Compute a set of core sleep timing metrics for a participant on a specific day.

    This method aggregates key temporal features related to sleep, including bedtime,
    risetime, time in bed (TIB), sleep onset and wake time, total sleep time (TST),
    midpoint of sleep, and related timing ratios and latencies.

    Parameters:
        participant_id (int): The ID of the participant.
        day_number (int): The day number to compute timing metrics for.

    Returns:
        dict:
            A dictionary with the following keys (values may be None if not computable):
                - "bedtime"
                - "risetime"
                - "tib_minutes"
                - "sleep_onset_time"
                - "wake_time"
                - "tst_minutes"
                - "midpoint_sleep"
                - "sleep_onset_latency"
                - "time_wake_to_risetime"
                - "ratio_sol_tib"

            Returns None if all values are None.

    Notes:
        - Use `extractor.verbose = True` to log which features are skipped.
    """
    features = {}

    for name, function in [
        ("bedtime", extractor.compute_bedtime),
        ("risetime", extractor.compute_risetime),
        ("tib_minutes", extractor.compute_tib_minutes),
        ("sleep_onset_time", extractor.compute_sleep_onset_time),
        ("wake_time", extractor.compute_wake_time),
        ("tst_minutes", extractor.compute_tst_minutes),
        ("midpoint_sleep", extractor.compute_midpoint_sleep),
        ("sleep_onset_latency", extractor.compute_sleep_onset_latency),
        ("time_wake_to_risetime", extractor.compute_time_between_wake_and_risetime),
        ("ratio_sol_tib", extractor.compute_ratio_sol_tib),
    ]:
        try:
            features[name] = function(participant_id, day_number)
        except ValueError as e:
            if extractor.verbose:
                print(f"Skipping {name} for participant {participant_id} on day {day_number}: {e}.")
            features[name] = None

    return features if any(v is not None for v in features.values()) else None

def compute_sleep_architecture_features(extractor: SleepFeaturesExtractor, participant_id, day_number):
    """
    Compute sleep architecture metrics for a participant on a specific day.

    This includes absolute and relative durations of different sleep stages (light, deep, REM)
    as well as the longest uninterrupted period in each of these stages.

    Parameters:
        participant_id (int): The ID of the participant.
        day_number (int): The day number to compute architecture metrics for.

    Returns:
        dict:
            A dictionary with keys (values may be None if not computable):
                - "time_in_light_sleep" (float or None)
                - "time_in_deep_sleep" (float or None)
                - "time_in_rem_sleep" (float or None)
                - "pct_light_sleep" (float or None)
                - "pct_deep_sleep" (float or None)
                - "pct_rem_sleep" (float or None)
                - "longest_light" (float or None)
                - "longest_deep" (float or None)
                - "longest_rem" (float or None)

    Notes:
        - If a specific sleep stage is missing or TST is unavailable, relevant metrics will be None.
        - Use `extractor.verbose = True` to log errors per feature.
    """
    features = {}

    for name, function in [
        ("time_in_light_sleep", extractor.compute_time_light_sleep),
        ("time_in_deep_sleep", extractor.compute_time_deep_sleep),
        ("time_in_rem_sleep", extractor.compute_time_rem_sleep),
        ("pct_light_sleep", extractor.compute_percentage_light_sleep),
        ("pct_deep_sleep", extractor.compute_percentage_deep_sleep),
        ("pct_rem_sleep", extractor.compute_percentage_rem_sleep),
        ("longest_light", extractor.compute_longest_light_sleep_period),
        ("longest_deep", extractor.compute_longest_deep_sleep_period),
        ("longest_rem", extractor.compute_longest_rem_sleep_period),
    ]:
        try:
            features[name] = function(participant_id, day_number)
        except ValueError as e:
            if extractor.verbose:
                print(f"Skipping {name} for participant {participant_id} on day {day_number}: {e}.")
            features[name] = None

    return features if any(v is not None for v in features.values()) else None

def compute_sleep_continuity_features(extractor: SleepFeaturesExtractor, participant_id, day_number):
    """
    Compute sleep continuity metrics for a participant on a specific day.

    Includes WASO, number and average duration of awakenings, fragmentation index,
    and two additional ratios (fragmentation and WASO relative to TST).

    Parameters:
        participant_id (int): The ID of the participant.
        day_number (int): The day number to compute continuity metrics for.

    Returns:
        dict:
            A dictionary containing:
                - "waso_minutes" (float or None)
                - "num_awakenings" (int or None)
                - "avg_awake_duration" (float or None)
                - "sleep_frag_index" (float or None)
                - "sleep_frag_ratio" (float or None)
                - "waso_tst_ratio" (float or None)

            Returns None if all metrics fail to compute.
    """
    features = {}

    for name, function in [
        ("waso_minutes", extractor.compute_waso_minutes),
        ("num_awakenings", extractor.compute_num_awakenings),
        ("avg_awake_duration", extractor.compute_avg_duration_awakenings),
        ("sleep_frag_index", extractor.compute_sleep_frag_index),
        ("sleep_frag_ratio", extractor.compute_sleep_frag_ratio),
        ("waso_tst_ratio", extractor.compute_waso_tst_ratio),
    ]:
        try:
            features[name] = function(participant_id, day_number)
        except ValueError as e:
            if extractor.verbose:
                print(f"Skipping {name} for participant {participant_id} on day {day_number}: {e}.")
            features[name] = None

    return features if any(v is not None for v in features.values()) else None

def compute_sleep_efficiency_and_regularity(extractor: SleepFeaturesExtractor, participant_id, day_number):
    """
    Compute sleep efficiency and regularity metrics for a participant.

    This method returns a mix of within-day and across-day sleep quality and regularity measures.

    Parameters:
        participant_id (int): The ID of the participant.
        day_number (int): The day number to compute metrics for.

    Returns:
        dict: A dictionary containing:
            - "sleep_efficiency" (float or None)
            - "sleep_onset_regularity" (float or None)
            - "wake_time_regularity" (float or None)
            - "ratio_sol_tib" (float or None)
            - "time_wake_to_risetime" (float or None)
    """
    features = {}

    for name, function in [
        ("sleep_efficiency", extractor.compute_sleep_efficiency),
        ("ratio_sol_tib", extractor.compute_ratio_sol_tib),
        ("time_wake_to_risetime", extractor.compute_time_between_wake_and_risetime),
    ]:
        try:
            features[name] = function(participant_id, day_number)
        except ValueError as e:
            if extractor.verbose:
                print(f"Skipping {name} for {participant_id} on day {day_number}: {e}")
            features[name] = None

    for name, function in [
        ("sleep_onset_regularity", extractor.compute_sleep_onset_reg),
        ("wake_time_regularity", extractor.compute_wake_time_reg),
    ]:
        try:
            features[name] = function(participant_id)
        except ValueError as e:
            if extractor.verbose:
                print(f"Skipping {name} for {participant_id}: {e}")
            features[name] = None

    return features

def build_dict_day_level_features(extractor: SleepFeaturesExtractor, participant_id):
    """
    Build a list of day-level sleep feature dictionaries for a given participant.

    This function loops through each available day for a specified participant and
    computes a predefined set of day-specific sleep features using the provided
    `SleepFeaturesExtractor` instance. For each day, it constructs a dictionary
    with both identifiers and feature values.

    Parameters:
        extractor (SleepFeaturesExtractor): 
            An instance of the SleepFeaturesExtractor class initialized with a sleep dataset.
        participant_id (int or str): 
            The ID of the participant for whom day-level features should be computed.

    Returns:
        list of dict:
            A list where each element is a dictionary representing one day's features for the participant.
            Each dictionary includes:
                - "participant_id" (int)
                - "day_number" (int)
                - Additional keys for each computed feature (e.g., "bedtime", "tst_minutes", "longest_rem", etc.)

    Notes:
        - If a specific feature cannot be computed due to missing or invalid data, its value will be set to `None`.
        - If an unexpected error occurs for a specific day, that day will be skipped.
        - Progress is displayed using a `tqdm` progress bar.
        - Assumes that the input DataFrame contains at least the columns "participant_id" and "day_number".
        - Participant ID is coerced to `int` for consistency.
    """
    participant_id = int(participant_id)
    df = extractor.df[extractor.df["participant_id"] == participant_id]
    days = df["day_number"].unique()
    results = []
    for day in tqdm(days, desc=f"Participant {participant_id}"):
        day = int(day)
        feature_dict = {"participant_id": participant_id, "day_number": day}
        try:
            for name, function in [
                ("bedtime", extractor.compute_bedtime),
                ("risetime", extractor.compute_risetime),
                ("tib_minutes", extractor.compute_tib_minutes),
                ("sleep_onset_latency", extractor.compute_sleep_onset_latency),
                ("wake_time", extractor.compute_wake_time),
                ("tst_minutes", extractor.compute_tst_minutes),
                ("midpoint_sleep", extractor.compute_midpoint_sleep),
                ("waso_tst_ratio", extractor.compute_waso_tst_ratio),
                ("sleep_frag_ratio", extractor.compute_sleep_frag_ratio),
                ("ratio_sol_tib", extractor.compute_ratio_sol_tib),
                ("time_wake_to_risetime", extractor.compute_time_between_wake_and_risetime),
                ("num_awakenings", extractor.compute_num_awakenings),
                ("avg_duration_awakenings", extractor.compute_avg_duration_awakenings),
                ("time_light_sleep", extractor.compute_time_light_sleep),
                ("time_deep_sleep", extractor.compute_time_deep_sleep),
                ("time_rem_sleep", extractor.compute_time_rem_sleep),
                ("longest_light", extractor.compute_longest_light_sleep_period),
                ("longest_deep", extractor.compute_longest_deep_sleep_period),
                ("longest_rem", extractor.compute_longest_rem_sleep_period),
            ]:
                try:
                    feature_dict[name] = function(participant_id, day)
                except ValueError:
                    feature_dict[name] = None
        except Exception as e:
            print(f"Skipping participant {participant_id}, day {day}: {e}")
            continue

        results.append(feature_dict)
    return results

def build_dict_all_day_level_features(extractor: SleepFeaturesExtractor):
    """
    Build day-level sleep feature dictionaries for all participants in the dataset.

    This function iterates over all unique participant IDs in the input dataset and
    computes day-level sleep features for each of them using `aggregate_day_level_features`.
    It returns a list of lists, where each inner list contains daily feature dictionaries
    for one participant.

    Parameters:
        extractor (SleepFeaturesExtractor): 
            An instance of the SleepFeaturesExtractor class initialized with a sleep dataset.

    Returns:
        list of list of dict:
            A list where each element corresponds to one participant and contains
            dictionaries of daily sleep features. Each dictionary includes:
                - "participant_id" (int)
                - "day_number" (int)
                - Various day-level feature keys (e.g., "tst_minutes", "bedtime", etc.)

    Notes:
        - Participant IDs are coerced to `int` for consistency.
        - If an error occurs while processing a participant, it may be skipped internally depending on the logic of `aggregate_day_level_features`.
        - Uses a `tqdm` progress bar to track progress across participants.
    """
    all_results = []
    pids = extractor.df["participant_id"].unique()
    for pid in tqdm(pids, desc=f"Processing all participants"):
        pid = int(pid)
        participant_result = build_dict_day_level_features(extractor, pid)
        all_results.extend(participant_result)
    
    return all_results

def build_dict_participant_level_features(extractor: SleepFeaturesExtractor, participant_id: int):
    """
    Compute participant-level sleep summary features across all available days.

    This function calculates aggregate features that describe a participant's
    sleep patterns over time, such as average total sleep time and the regularity
    of sleep onset, wake time, bedtime, and midpoint of sleep.

    Parameters:
        extractor (SleepFeaturesExtractor): 
            An instance of the SleepFeaturesExtractor class initialized with a sleep dataset.
        participant_id (int): 
            The unique identifier of the participant to compute features for.

    Returns:
        dict:
            A dictionary containing the participant ID and the following keys:
                - "average_tst" (float or None): Mean total sleep time in minutes.
                - "sleep_onset_regularity" (float or None): Circular std of sleep onset times.
                - "wake_time_regularity" (float or None): Circular std of wake times.
                - "bedtime_reg" (float or None): Circular std of bedtimes.
                - "midpoint_sleep_reg" (float or None): Circular std of midpoints of sleep.

    Notes:
        - If a specific metric cannot be computed due to missing data, its value is set to None.
        - Verbose mode on the extractor will not print messages here, but could be integrated.
    """
    feature_dict = {"participant_id": participant_id}
    for name, function in [
        ("average_tst", extractor.compute_avg_tst),
        ("sleep_onset_regularity", extractor.compute_sleep_onset_reg),
        ("wake_time_regularity", extractor.compute_wake_time_reg),
        ("bedtime_reg", extractor.compute_bedtime_reg),
        ("midpoint_sleep_reg", extractor.compute_midpoint_sleep_reg),
    ]:
        try:
            feature_dict[name] = function(participant_id)
        except ValueError:
            feature_dict[name] = None
        
    return feature_dict

def build_dict_all_participant_level_features(extractor: SleepFeaturesExtractor):
    """
    Compute participant-level summary features for all participants in the dataset.

    This function iterates over all unique participant IDs and computes their 
    across-day aggregate sleep features, such as average total sleep time and 
    regularity metrics for sleep onset, wake time, bedtime, and midpoint of sleep.

    Parameters:
        extractor (SleepFeaturesExtractor): 
            An instance of the SleepFeaturesExtractor class initialized with the full dataset.

    Returns:
        list of dict:
            A list where each element is a dictionary of participant-level features for one participant.
            Each dictionary contains:
                - "participant_id" (int)
                - "average_tst" (float or None)
                - "sleep_onset_regularity" (float or None)
                - "wake_time_regularity" (float or None)
                - "bedtime_reg" (float or None)
                - "midpoint_sleep_reg" (float or None)

    Notes:
        - Participants for whom feature computation fails are skipped.
        - If extractor.verbose is True, skipped participants and reasons are printed.
        - Uses tqdm to display progress over participants.
    """
    all_results = []
    pids = extractor.df["participant_id"].unique()
    for pid in tqdm(pids, desc=f"Building participant level summary"):
        pid = int(pid)
        try:
            result = build_dict_participant_level_features(extractor, pid)
            all_results.append(result)
        except Exception as e:
            if extractor.verbose:
                print(f"Skipping participant {pid} due to error: {e}")
            continue

    return all_results