import pandas as pd
import numpy as np

class SleepFeaturesExtractor:
    def __init__(self, df: pd.DataFrame, verbose=False, filter_verbose=False):
        self.df = df
        self.verbose = verbose
        self.filter_verbose = filter_verbose

    # ----------------------------------------------------------------------------------------------------------------------------
    # Filtering functions

    def _filter(self, **kwargs):
        """
        Filter the DataFrame based on one or more column-value conditions.
        
        Each keyword argument specifies a column name and the value(s) to filter by. 
        If the value is a list, the method filters rows where the column's value is in the list.

        Parameters:
            **kwargs: Column-value pairs to filter the DataFrame by.

        Returns:
            pd.DataFrame: A filtered copy of the original DataFrame.

        Raises:
            ValueError: If any specified column does not exist in the DataFrame.
        """
        if self.filter_verbose:
            print(f"Filtering with: {kwargs}")
        # Checking if the input columns exist in the dataframe
        missing_cols = [col for col in kwargs if col not in self.df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns in dataframe: {missing_cols}.")

        df = self.df.copy()
        for col, val in kwargs.items():
            df = df[df[col].isin(val) if isinstance(val, list) else df[col] == val]
        return df
    
    def get_sleep_stage_data(self, participant_id=None, day_number=None, sleep_stage_state=None):
        """
        Retrieve rows from the DataFrame that match the given participant ID, day number, 
        and/or sleep stage state.

        This is a convenience method that filters sleep stage data based on one or more 
        of the provided parameters.

        Parameters:
            participant_id (int or str, optional): ID of the participant to filter by.
            day_number (int, optional): Experimental or recorded day number.
            sleep_stage_state (str or int, optional): Sleep stage label (e.g., "REM", "Light", 1, 2, etc.).

        Returns:
            pd.DataFrame: A filtered DataFrame containing rows that match the provided criteria.

        """
        filters = {}
        if participant_id is not None:
            filters["participant_id"] = participant_id
        if day_number is not None:
            filters["day_number"] = day_number
        if sleep_stage_state is not None:
            filters["sleep_stage_state"] = sleep_stage_state
        return self._filter(**filters)
    
    def get_participant_day_data(self, participant_id, day_number):
        """
        Retrieve data for a specific participant on a given day.

        This method filters the internal DataFrame to return all rows matching the 
        given participant ID and day number. Raises an error if no such data exists.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to filter by.

        Returns:
            pd.DataFrame: A filtered DataFrame containing the participant's data for that day.

        Raises:
            AssertionError: If `participant_id` or `day_number` is not an integer.
            ValueError: If no matching data is found for the given inputs.
        """
        assert isinstance(participant_id, int), f"participant_id input has to be an integer!"
        assert isinstance(day_number, int), f"day_number input has to be an integer!"

        df = self._filter(participant_id=participant_id, day_number=day_number)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")

        return df

    # ----------------------------------------------------------------------------------------------------------------------------
    # Sleep timing functions

    def compute_bedtime(self, participant_id, day_number):
        """
        Compute the bedtime for a given participant on a specific day.

        This method retrieves the participant's data for the given day and returns 
        the 'start_time' value from the first row, which is assumed to represent bedtime.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute bedtime for.

        Returns:
            pd.Timestamp: The bedtime as a pandas Timestamp.

        Raises:
            ValueError: If no data is found for the given participant and day,
                        or if the bedtime value is missing (NaT).
        """
        df = self.get_participant_day_data(participant_id, day_number)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        # Assumes the bedtime will be the first row
        bedtime = df["start_time"].iloc[0]

        if pd.isnull(bedtime):
            raise ValueError(f"Bedtime is missing for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"Bedtime for participant {participant_id} on day {day_number}: {bedtime}")

        return bedtime
    
    def compute_risetime(self, participant_id, day_number):
        """
        Compute the risetime for a given participant on a specific day.

        This method retrieves the participant's data for the given day and returns 
        the 'end_time' value from the last row, which is assumed to represent risetime.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute risetime for.

        Returns:
            pd.Timestamp: The risetime as a pandas Timestamp.

        Raises:
            ValueError: If no data is found for the given participant and day,
                        or if the risetime value is missing (NaT).
        """
        df = self.get_participant_day_data(participant_id, day_number)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        # Assumes risetime will be the last row
        risetime = df["end_time"].iloc[-1]

        if pd.isnull(risetime):
            raise ValueError(f"Risetime is missing for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"Risetime for participant {participant_id} on day {day_number}: {risetime}")

        return risetime
    
    def compute_tib_minutes(self, participant_id, day_number):
        """
        Compute Time In Bed (TIB) in minutes for a given participant on a specific day.

        TIB is defined as the sum of durations between the first recorded start time 
        (assumed to be bedtime) and the last recorded end time (assumed to be risetime) 
        for the specified day. Rows outside this range are excluded from the calculation.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute TIB for.

        Returns:
            float: Total time in bed in minutes.

        Raises:
            ValueError: If no data is found for the given participant and day,
                        if bedtime is after or equal to risetime,
                        or if either bedtime or risetime is missing.
        
        Notes:
            - Assumes bedtime corresponds to the first row's 'start_time',
            and risetime to the last row's 'end_time'.
            - TIB is calculated by summing the 'duration_minutes' of rows 
            within the bedtime-to-risetime interval.
        """
        df = self.get_participant_day_data(participant_id, day_number)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        # Assuming bedtime is first row in data for specific night and
        # that risetime is the last recorded time
        bedtime = df["start_time"].iloc[0]
        risetime = df["end_time"].iloc[-1]

        if bedtime >= risetime:
            raise ValueError(f"Invalid time range: bedtime >= risetime for participant {participant_id} on day {day_number}.")

        if pd.isnull(bedtime) or pd.isnull(risetime):
            raise ValueError(f"Missing bedtime or risetime for participant {participant_id} on day {day_number}.")
        
        df = df[(df["start_time"] >= bedtime) & (df["end_time"] <= risetime)]

        tib = df["duration_minutes"].sum(skipna=True)
        
        if self.verbose:
            print(f"Time In Bed (TIB) for participant {participant_id} on day {day_number}: {tib} minutes")

        return tib
    
    def compute_sleep_onset_time(self, participant_id, day_number):
        """
        Compute the sleep onset time for a participant on a specific day.

        Sleep onset time is defined as the start time of the first recorded 
        sleep stage classified as "light", "deep", or "REM".

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute sleep onset time for.

        Returns:
            pd.Timestamp: The timestamp when the participant first enters sleep.

        Raises:
            ValueError: If no sleep stage data is found for the given participant and day,
                        or if the sleep onset time is missing (NaT).
        
        Notes:
            - Sleep onset is identified as the earliest occurrence of a sleep stage 
            labeled "light", "deep", or "REM".
            - Data is assumed to be sorted chronologically by start time.
        """
        df = self.get_sleep_stage_data(participant_id=participant_id, day_number=day_number, sleep_stage_state=["light", "deep", "rem"])
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        sleep_onset_time = df["start_time"].iloc[0]

        if pd.isnull(sleep_onset_time):
            raise ValueError(f"Missing data for sleep onset time for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"Sleep onset time for participant {participant_id} on day {day_number}: {sleep_onset_time}")
        
        return sleep_onset_time
    
    def compute_wake_time(self, participant_id, day_number):
        """
        Compute the wake time for a participant on a specific day.

        Wake time is defined as the end time of the last recorded 
        sleep stage classified as "light", "deep", or "REM".

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute wake time for.

        Returns:
            pd.Timestamp: The timestamp when the participant last exits a sleep stage.

        Raises:
            ValueError: If no sleep stage data is found for the given participant and day,
                        or if the wake time value is missing (NaT).
        
        Notes:
            - Wake time is determined as the `end_time` of the last qualifying sleep stage.
            - Assumes sleep stages are chronologically ordered.
        """
        df = self.get_sleep_stage_data(participant_id=participant_id, day_number=day_number, sleep_stage_state=["light", "deep", "rem"])
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        wake_time = df["end_time"].iloc[-1]

        if pd.isnull(wake_time):
            raise ValueError(f"Missing data for calculating wake up time for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"Wake time for participant {participant_id} on day {day_number}: {wake_time}")

        return wake_time
    
    def compute_tst_minutes(self, participant_id, day_number):
        """
        Compute Total Sleep Time (TST) in minutes for a participant on a specific day.

        TST is calculated as the sum of all durations spent in recognized sleep stages:
        "light", "deep", or "REM". Wake and unknown states are excluded.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute TST for.

        Returns:
            float: Total sleep time in minutes.

        Raises:
            ValueError: If no valid sleep stage data is found for the given participant and day,
                        or if TST is zero or missing.
        
        Notes:
            - Assumes sleep stages are already classified and labeled in the data.
            - Uses the 'duration_minutes' column for calculation.
        """
        df = self.get_sleep_stage_data(participant_id=participant_id, day_number=day_number, sleep_stage_state=["light", "deep", "rem"])
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")

        # Sums up the duration of hours where participant is in a sleep stage       
        tst = df["duration_minutes"].sum(skipna=True)

        if pd.isnull(tst) or tst == 0:
            raise ValueError(f"TST could not be computed for participant {participant_id} on day {day_number}, missing data...")

        if self.verbose:
            print(f"Total Sleep Time (TST) for participant {participant_id} on day {day_number}: {tst} minutes")

        return tst
    
    def compute_midpoint_sleep(self, participant_id, day_number):
        """
        Compute the midpoint of sleep for a participant on a specific day.

        The sleep midpoint is calculated as the halfway point between 
        sleep onset and wake time. This metric can be used to infer 
        chronotype or sleep phase timing.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the midpoint for.

        Returns:
            pd.Timestamp: The midpoint of the participant's sleep period.

        Raises:
            ValueError: If sleep onset or wake time cannot be computed.
        
        Notes:
            - Relies on `compute_sleep_onset_time` and `compute_wake_time`.
            - Assumes both onset and wake times are valid and timezone-consistent.
        """
        sleep_onset = self.compute_sleep_onset_time(participant_id, day_number)
        wake_time = self.compute_wake_time(participant_id, day_number)

        midpoint = sleep_onset + (wake_time - sleep_onset) / 2

        if self.verbose:
            print(f"Midpoint of sleep for participant {participant_id} on day {day_number}: {midpoint}")

        return midpoint
    
    def compute_sleep_onset_latency(self, participant_id, day_number):
        """
        Compute Sleep Onset Latency (SOL) in minutes for a participant on a specific day.

        SOL is defined as the duration between bedtime (initial time in bed) and sleep onset
        (first occurrence of a sleep stage such as "light", "deep", or "REM").

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute SOL for.

        Returns:
            float: Sleep Onset Latency in minutes.

        Raises:
            ValueError: If bedtime or sleep onset time cannot be computed.

        Notes:
            - A longer SOL may indicate difficulty falling asleep.
            - SOL = (sleep_onset_time - bedtime), measured in clock time.
        """
        bedtime = self.compute_bedtime(participant_id, day_number)
        onset = self.compute_sleep_onset_time(participant_id, day_number)

        if onset < bedtime:
            raise ValueError(f"Sleep onset time occurs before bedtime for participant {participant_id} on day {day_number}.")
        
        sol = (onset - bedtime)
        sol_minutes = sol.total_seconds() / 60
        
        if self.verbose:
            print(f"Sleep Onset Latency (SOL) for participant {participant_id} on day {day_number}: {sol_minutes:.2f} minutes")

        return sol_minutes

    
    def compute_time_between_wake_and_risetime(self, participant_id, day_number):
        """
        Computes the time (in minutes) between wake time and risetime for a given
        participant and day.

        This reflects the duration the participant spends awake in bed before actually getting up.

        Parameters
        ----------
        participant_id : int or str
            Unique identifier for the participant.
        day_number : int
            Day index to analyze (e.g., relative to study start).

        Returns
        -------
        float
            Time between wake time and risetime, in minutes.

        Raises
        ------
        ValueError
            If risetime occurs before wake time, or if the computed duration is null.

        Notes
        -----
        A longer duration may indicate grogginess or difficulty initiating activity after waking.
        """
        wake_time = self.compute_wake_time(participant_id, day_number)
        risetime = self.compute_risetime(participant_id, day_number)

        if wake_time > risetime:
            raise ValueError(f"Could not compute, risetime happens before wake time...")
        
        diff = (risetime - wake_time)

        if pd.isnull(diff):
            raise ValueError(f"Could not compute time between wake time and risetime for particiapnt {participant_id} on day {day_number}.")
        diff_minutes = diff.total_seconds() / 60

        if self.verbose:
            print(f"Time between wake time and risetime for participant {participant_id} on day {day_number}: {diff_minutes:.2f} minutes")

        return diff_minutes
    # ----------------------------------------------------------------------------------------------------------------------------
    # Sleep Architecture

    def compute_time_in_sleep_stage_minutes(self, participant_id, day_number, sleep_stage_state):
        """
        Compute the total time spent in a specific sleep stage for a participant on a given day.

        This method filters sleep stage data by participant ID, day number, and the 
        specified sleep stage, and sums the total duration in minutes.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.
            sleep_stage_state (str or list[str]): The sleep stage(s) to include 
                (e.g., "REM", "deep", "light", or a list of them).

        Returns:
            float: Total time spent in the specified sleep stage(s), in minutes.

        Raises:
            ValueError: If no matching sleep stage data is found for the given inputs.

        Notes:
            - The duration is computed from the 'duration_minutes' column.
            - Accepts either a single sleep stage as a string or a list of stages.
        """
        df = self.get_sleep_stage_data(participant_id=participant_id,
                                       day_number=day_number,
                                       sleep_stage_state=sleep_stage_state)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        duration = df["duration_minutes"].sum(skipna=True)

        if self.verbose:
            print(f"Time in stage '{sleep_stage_state}' for participant {participant_id} on day {day_number}: {duration:.2f} minutes")
        
        return duration
    
    def compute_time_light_sleep(self, participant_id, day_number):
        """
        Compute total time spent in light sleep for a participant on a specific day.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Total duration of light sleep in minutes.
        """
        return self.compute_time_in_sleep_stage_minutes(participant_id=participant_id, day_number=day_number, sleep_stage_state="light")
    

    def compute_time_deep_sleep(self, participant_id, day_number):
        """
        Compute total time spent in deep sleep for a participant on a specific day.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Total duration of deep sleep in minutes.
        """
        return self.compute_time_in_sleep_stage_minutes(participant_id=participant_id, day_number=day_number, sleep_stage_state="deep")
    

    def compute_time_rem_sleep(self, participant_id, day_number):
        """
        Compute total time spent in REM sleep for a participant on a specific day.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Total duration of REM sleep in minutes.
        """
        return self.compute_time_in_sleep_stage_minutes(participant_id=participant_id, day_number=day_number, sleep_stage_state="rem")
    
    def compute_percentage_sleep_stage_of_tst(self, participant_id, day_number, sleep_stage_state):
        """
        Compute the percentage of Total Sleep Time (TST) spent in a specific sleep stage.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.
            sleep_stage_state (str or list[str]): The sleep stage(s) to include 
                (e.g., "REM", "deep", "light", or a list of them).

        Returns:
            float: Percentage of TST spent in the specified sleep stage(s).

        Raises:
            ValueError: If TST or sleep stage duration cannot be computed.

        Notes:
            - This value is calculated as: (time_in_stage / TST) * 100.
            - TST includes only "light", "deep", and "REM" stages.
        """
        tst = self.compute_tst_minutes(participant_id, day_number)
        time_in_sleep_stage = self.compute_time_in_sleep_stage_minutes(participant_id, day_number, sleep_stage_state)

        pct_time_spent_in_sleep_stage = time_in_sleep_stage / tst * 100
        
        if self.verbose:
            print(f"Time in TST spent in {sleep_stage_state} for participant {participant_id} on day {day_number}: {pct_time_spent_in_sleep_stage:.2f}%")
        
        return pct_time_spent_in_sleep_stage
        

    def compute_percentage_light_sleep(self, participant_id, day_number):
        """
        Compute the percentage of Total Sleep Time (TST) spent in light sleep.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Percentage of TST spent in light sleep.
        """
        return self.compute_percentage_sleep_stage_of_tst(participant_id, day_number, sleep_stage_state="light")
    
    def compute_percentage_deep_sleep(self, participant_id, day_number):
        """
        Compute the percentage of Total Sleep Time (TST) spent in deep sleep.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Percentage of TST spent in deep sleep.
        """
        return self.compute_percentage_sleep_stage_of_tst(participant_id, day_number, sleep_stage_state="deep")
    
    def compute_percentage_rem_sleep(self, participant_id, day_number):
        """
        Compute the percentage of Total Sleep Time (TST) spent in REM sleep.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Percentage of TST spent in REM sleep.
        """
        return self.compute_percentage_sleep_stage_of_tst(participant_id, day_number, sleep_stage_state="rem")
    
     
    def compute_longest_uninterrupted_sleep_stage(self, participant_id, day_number, sleep_stage_state):
        """
        Compute the longest uninterrupted period (in minutes) spent in a given sleep stage 
        for a participant on a specific day.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.
            sleep_stage_state (str): The sleep stage to evaluate (e.g., "light", "deep", "rem", "awake").

        Returns:
            float: The duration (in minutes) of the longest uninterrupted bout of the given sleep stage.

        Raises:
            ValueError: If no matching data is found, or if no valid durations are present.

        Notes:
            - Assumes each row represents a continuous episode of a sleep stage.
            - Useful for assessing sleep stability and consolidation.
        """
        df = self.get_sleep_stage_data(participant_id=participant_id,
                                       day_number=day_number,
                                       sleep_stage_state=sleep_stage_state)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} for {sleep_stage_state} sleep on day {day_number}.")
            
        max_duration = df["duration_minutes"].max(skipna=True)

        if pd.isnull(max_duration) or max_duration <= 0:
            raise ValueError(f"No valid duration recorded for participant {participant_id} on day {day_number} for {sleep_stage_state} sleep.")
        
        if self.verbose:
            print(f"Longest recorded period in {sleep_stage_state} sleep for participant {participant_id} "
                  f"on day {day_number}: {max_duration:.2f} minutes")
        
        return max_duration
    
    def compute_longest_light_sleep_period(self, participant_id, day_number):
        """
        Compute the longest uninterrupted period (in minutes) spent in light sleep 
        for a participant on a specific day.

        This method is a wrapper around 
        `compute_longest_uninterrupted_sleep_stage(...)`, with the sleep stage 
        fixed to "light". It returns the maximum duration (in minutes) of any 
        continuous light sleep episode for the specified participant and day.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: The duration (in minutes) of the longest uninterrupted bout of light sleep.

        Raises:
            ValueError: If no matching data is found, or if no valid durations are present.

        Notes:
            - Assumes each row in the dataset represents a continuous episode of a sleep stage.
        """
        return self.compute_longest_uninterrupted_sleep_stage(
            participant_id=participant_id,
            day_number=day_number,
            sleep_stage_state="light")
    
    def compute_longest_deep_sleep_period(self, participant_id, day_number):
        """
        Compute the longest uninterrupted period (in minutes) spent in deep sleep 
        for a participant on a specific day.

        This method is a wrapper around 
        `compute_longest_uninterrupted_sleep_stage(...)`, with the sleep stage 
        fixed to "deep". It returns the maximum duration (in minutes) of any 
        continuous deep sleep episode for the specified participant and day.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: The duration (in minutes) of the longest uninterrupted bout of deep sleep.

        Raises:
            ValueError: If no matching data is found, or if no valid durations are present.

        Notes:
            - Assumes each row in the dataset represents a continuous episode of a sleep stage.
        """
        return self.compute_longest_uninterrupted_sleep_stage(
            participant_id=participant_id,
            day_number=day_number,
            sleep_stage_state="deep")

    def compute_longest_rem_sleep_period(self, participant_id, day_number):
        """
        Compute the longest uninterrupted period (in minutes) spent in REM sleep 
        for a participant on a specific day.

        This method is a wrapper around 
        `compute_longest_uninterrupted_sleep_stage(...)`, with the sleep stage 
        fixed to "rem". It returns the maximum duration (in minutes) of any 
        continuous REM sleep episode for the specified participant and day.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: The duration (in minutes) of the longest uninterrupted bout of REM sleep.

        Raises:
            ValueError: If no matching data is found, or if no valid durations are present.

        Notes:
            - Assumes each row in the dataset represents a continuous episode of a sleep stage.
        """
        return self.compute_longest_uninterrupted_sleep_stage(
            participant_id=participant_id,
            day_number=day_number,
            sleep_stage_state="rem")
    
    # ----------------------------------------------------------------------------------------------------------------------------
    # Sleep Continuity (Fragmentation)

    def compute_waso_minutes(self, participant_id, day_number):
        """
        Compute Wake After Sleep Onset (WASO) in minutes for a participant on a specific day.

        WASO is defined as the total time spent awake between sleep onset and final wake time.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute WASO for.

        Returns:
            float: Total duration of wakefulness after sleep onset, in minutes.

        Raises:
            ValueError: If no awake data is found in the sleep period,
                        or if WASO is missing or zero.

        Notes:
            - Sleep onset is determined by the first occurrence of "light", "deep", or "REM".
            - Wake time is the end of the last such sleep stage.
            - Only "awake" stages occurring between these two times are included in WASO.
        """
        sleep_onset_time = self.compute_sleep_onset_time(participant_id, day_number)
        wake_time = self.compute_wake_time(participant_id, day_number)
        df = self.get_sleep_stage_data(participant_id=participant_id, day_number=day_number, sleep_stage_state="awake")
        df = df[(df["start_time"] >= sleep_onset_time) & (df["start_time"] < wake_time)]
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        waso = df["duration_minutes"].sum(skipna=True)

        if pd.isnull(waso) or waso == 0:
            raise ValueError(f"WASO could not be computed for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"WASO for participant {participant_id} on day {day_number}: {waso} minutes")

        return waso
    
    def compute_num_awakenings(self, participant_id, day_number):
        """
        Compute the number of awakenings during the sleep period for a participant on a specific day.

        An awakening is defined as any "awake" stage that occurs between sleep onset and the final wake time,
        excluding the final wake episode.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            int: Number of discrete awakenings during the sleep period.

        Raises:
            ValueError: If the number of awakenings cannot be computed (e.g., due to missing data).

        Notes:
            - Sleep onset is the start of the first "light", "deep", or "REM" stage.
            - Wake time is the end of the last such sleep stage.
            - Awake stages occurring entirely within this window are counted.
        """
        sleep_onset = self.compute_sleep_onset_time(participant_id, day_number)
        wake_up_time = self.compute_wake_time(participant_id, day_number)

        df = self.get_sleep_stage_data(participant_id=participant_id, day_number=day_number, sleep_stage_state="awake")
        # Exlcudes the final wake if the last recorded sleep stage is "awake"
        df = df[(df["start_time"] >= sleep_onset) & (df["end_time"] < wake_up_time)]

        num_awakenings = len(df)
        if pd.isnull(num_awakenings):
            raise ValueError(f"Could not compute the number of awakenings for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"Number of awakenings for participant {participant_id} on day {day_number}: {num_awakenings}")

        return num_awakenings
    
    def compute_avg_duration_awakenings(self, participant_id, day_number):
        """
        Compute the average duration of awakenings during the sleep period for a participant on a specific day.

        Only "awake" stages occurring between sleep onset and final wake time are considered.
        The final wake episode is excluded.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Average duration of awakenings in minutes.

        Raises:
            ValueError: If no qualifying awakenings are found,
                        or if duration data is missing.

        Notes:
            - Sleep onset is the first occurrence of a "light", "deep", or "REM" stage.
            - Wake time is the end of the last such stage.
            - Only durations of awakenings within this window are included.
        """
        sleep_onset = self.compute_sleep_onset_time(participant_id, day_number)
        wake_time = self.compute_wake_time(participant_id, day_number)

        df = self.get_sleep_stage_data(participant_id=participant_id, day_number=day_number, sleep_stage_state="awake")
        df = df[(df["start_time"] >= sleep_onset) & (df["start_time"] < wake_time)]

        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        if df["duration_minutes"].count() == 0:
            raise ValueError(f"Could not compute average duration of awkenings for participant {participant_id} on day {day_number}.")

        avg_duration_awakenings = df["duration_minutes"].mean()

        if self.verbose:
            print(f"Average duration of awakenings for participant {participant_id} on day {day_number}: {avg_duration_awakenings:.2f} minutes")

        return avg_duration_awakenings
    
    def compute_sleep_frag_index(self, participant_id, day_number):
        """
        Compute the Sleep Fragmentation Index for a participant on a specific day.

        The Sleep Fragmentation Index is calculated as the number of awakenings divided by Total Sleep Time (TST),
        representing the frequency of sleep interruptions.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Sleep Fragmentation Index (awakenings per minute of sleep).

        Raises:
            ValueError: If the index cannot be computed due to missing data.

        Notes:
            - A higher index indicates more fragmented sleep.
            - TST includes only "light", "deep", and "REM" sleep.
            - The final awakening at the end of sleep is excluded from the count.
        """
        num_awakenings = self.compute_num_awakenings(participant_id, day_number)
        tst = self.compute_tst_minutes(participant_id, day_number)

        sleep_frag_index = num_awakenings / tst

        if pd.isnull(sleep_frag_index):
            raise ValueError(f"Could not compute sleep fragmentation index for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"Sleep Fragmentation Index for participant {participant_id} on day {day_number}: {sleep_frag_index:.2f}")

        return sleep_frag_index
    
    def compute_sleep_frag_ratio(self, participant_id, day_number):
        """
        Computes the sleep fragmentation ratio for a specific participant and day.

        The fragmentation ratio is defined as the number of awakenings divided by the 
        total number of sleep stage transitions (light, deep, REM), expressed as a percentage.

        Parameters
        ----------
        participant_id : int or str
            Unique identifier for the participant.
        day_number : int
            Day index to analyze (e.g., relative to study start).

        Returns
        -------
        float
            Sleep fragmentation ratio as a percentage.

        Raises
        ------
        ValueError
            If no relevant sleep stage data is found for the given participant and day,
            or if the number of sleep stages is zero.

        Notes
        -----
        This function may be updated to optionally return the ratio as a proportion (0–1) 
        instead of a percentage, depending on usage preferences.
        """
        num_awakenings = self.compute_num_awakenings(participant_id, day_number)
        df = self.get_sleep_stage_data(
            participant_id=participant_id,
            day_number=day_number,
            sleep_stage_state=["light", "deep", "rem"])
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} in sleep stages 'light', 'deep, or 'rem'.")
        
        num_sleep_stages = len(df)
        if pd.isnull(num_sleep_stages) or num_sleep_stages == 0:
            raise ValueError(f"Could not compute fragmentation ratio for participant {participant_id} on day {day_number}: No sleep stages recorded.")
    
        frag_ratio = num_awakenings / num_sleep_stages * 100

        if self.verbose:
            print(f"Fragmentation ratio for participant {participant_id} on day {day_number}: {frag_ratio:.2f}%")        
        
        return frag_ratio
    
    def compute_waso_tst_ratio(self, participant_id, day_number):
        """
        Computes the ratio of Wake After Sleep Onset (WASO) to Total Sleep Time (TST)
        for a given participant and day, expressed as a percentage.

        Parameters
        ----------
        participant_id : int or str
            Unique identifier for the participant.
        day_number : int
            Day index to analyze (e.g., relative to study start).

        Returns
        -------
        float
            WASO/TST ratio as a percentage.

        Notes
        -----
        A higher ratio may indicate more fragmented or less restful sleep.
        """
        waso = self.compute_waso_minutes(participant_id, day_number)
        tst = self.compute_tst_minutes(participant_id, day_number)

        ratio = waso / tst * 100

        if self.verbose:
            print(f"Ratio between WASO and TST for participant {participant_id} on day {day_number}: {ratio:.2f}%")

        return ratio
    
    def compute_ratio_sol_tib(self, participant_id, day_number):
        """
        Computes the ratio of Sleep Onset Latency (SOL) to Time in Bed (TIB)
        for a given participant and day, expressed as a percentage.

        Parameters
        ----------
        participant_id : int or str
            Unique identifier for the participant.
        day_number : int
            Day index to analyze (e.g., relative to study start).

        Returns
        -------
        float
            Ratio of SOL to TIB as a percentage. Returns 0 if SOL is missing or 0.

        Raises
        ------
        ValueError
            If the computed ratio is NaN or cannot be determined.

        Notes
        -----
        A high ratio may indicate difficulty falling asleep relative to time spent in bed.
        """
        sol = self.compute_sleep_onset_latency(participant_id, day_number)
        tib = self.compute_tib_minutes(participant_id, day_number)

        if pd.isnull(sol) or sol == 0:
            ratio = 0
            if self.verbose:
                print(f"Ratio between SOL and TIB for participant {participant_id} on day {day_number}: {ratio:.2f}%.")

            return ratio

        ratio = sol / tib * 100

        if pd.isnull(ratio):
            raise ValueError(f"Could not compute ratio between SOL and TIB for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"Ratio between SOL and TIB for participant {participant_id} on day {day_number}: {ratio:.2f}%.")

        return ratio
    
    def compute_avg_tst(self, participant_id):
        """
        Compute the average Total Sleep Time (TST) in minutes across multiple valid days 
        for a given participant.

        TST is calculated per day using compute_tst_minutes(). This method collects TST 
        values for all days where computation is successful, and returns their average.

        Parameters:
            participant_id (int): The ID of the participant.

        Returns:
            float: The average TST in minutes across valid days.

        Raises:
            ValueError: If fewer than 2 valid TST values are available for the participant.

        Notes:
            - Days where TST cannot be computed (e.g. due to missing data) are skipped.
            - A minimum of 2 valid days is required to ensure a meaningful average.
        """
        df = self._filter(participant_id=participant_id)

        tst_list = []
        for day in df["day_number"].unique():
            try:
                tst = self.compute_tst_minutes(participant_id, day)
                if not pd.isnull(tst):
                    tst_list.append(tst)
            except ValueError:
                if self.verbose:
                    print(f"Skipping day {day} for participant {participant_id}: no valid TST")
                continue
        
        if len(tst_list) < 2:
            raise ValueError(f"Not enough valid TST values to calculate average for participant {participant_id}.")
        
        avg_tst = np.mean(tst_list)

        if self.verbose:
            print(f"Average TST for participant {participant_id}: {avg_tst:.2f} minutes over {len(tst_list)} days.")

        return avg_tst
        
    # ----------------------------------------------------------------------------------------------------------------------------
    # Sleep Efficiency and Quality

    def compute_sleep_efficiency(self, participant_id, day_number):
        """
        Compute the sleep efficiency for a participant on a specific day.

        Sleep efficiency is defined as the percentage of Time In Bed (TIB) spent asleep,
        calculated as (TST / TIB) * 100.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Sleep efficiency as a percentage.

        Raises:
            ValueError: If participant data is missing or TST/TIB cannot be computed.

        Notes:
            - TST (Total Sleep Time) includes only "light", "deep", and "REM" stages.
            - TIB is the duration from bedtime to risetime.
            - A higher sleep efficiency indicates more consolidated sleep.
        """
        tst = self.compute_tst_minutes(participant_id, day_number)
        tib = self.compute_tib_minutes(participant_id, day_number)

        df = self.get_participant_day_data(participant_id, day_number)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        sleep_efficiency = tst / tib * 100

        if self.verbose:
            print(f"Sleep effiency (% of time in bed spent asleep) for participant {participant_id} on day {day_number}: {sleep_efficiency:.2f}%")

        return sleep_efficiency
    
    def compute_sleep_onset_reg(self, participant_id):
        """
        Compute sleep onset regularity (circular standard deviation) for a participant across all days.

        This metric quantifies how consistent a participant's sleep onset times are from day to day,
        using circular statistics to account for the 24-hour cycle.

        Parameters:
            participant_id (int): The ID of the participant.

        Returns:
            float: Sleep onset regularity, expressed as the circular standard deviation in minutes.

        Raises:
            ValueError: If less than two valid onset times are available for the participant.

        Notes:
            - Converts each sleep onset time to an angle on the 24-hour clock.
            - Uses the length of the mean resultant vector (R) to compute circular std dev.
            - A lower value indicates more consistent sleep onset timing.
            - Days with missing or invalid sleep onset times are skipped.
        """
        df = self.get_sleep_stage_data(participant_id=participant_id, sleep_stage_state=["light", "deep", "rem"])
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id}.")
        
        days = df["day_number"].unique()
        angles = []
        
        for day in days:
            try:
                onset_time = self.compute_sleep_onset_time(participant_id, day)
                minutes = onset_time.hour * 60 + onset_time.minute + onset_time.second / 60
                angle = 2 * np.pi * (minutes / 1440)
                angles.append(angle)
            except ValueError:
                if self.verbose:
                    print(f"Skipping day {day} due to missing time.")
                continue

        if len(angles) < 2:
            raise ValueError(f"Not enough valid sleep data to compute onset regularity for participant {participant_id}.")
        
        sin_sum = np.sum(np.sin(angles))
        cos_sum = np.sum(np.cos(angles))
        R = np.sqrt(sin_sum**2 + cos_sum**2) / len(angles)
        
        R = np.clip(R, 0, 1)
        onset_std_minutes = np.sqrt(-2 * np.log(R)) * (1440 / (2 * np.pi))

        if self.verbose:
            print(f"Sleep Onset Regularity for participant {participant_id}: {onset_std_minutes:.2f} minutes")
        
        return onset_std_minutes
    
    def compute_wake_time_reg(self, participant_id):
        """
        Compute wake time regularity (circular standard deviation) for a participant across all days.

        This metric quantifies how consistent a participant's wake times are day-to-day,
        accounting for the circular nature of time over a 24-hour cycle.

        Parameters:
            participant_id (int): The ID of the participant.

        Returns:
            float: Wake time regularity, expressed as the circular standard deviation in minutes.

        Raises:
            ValueError: If fewer than two valid wake times are available for the participant.

        Notes:
            - Each wake time is converted into an angle on a 24-hour circle.
            - Regularity is computed using the length of the mean resultant vector (R).
            - A smaller value indicates more consistent wake timing across days.
            - Days with invalid or missing wake times are skipped.
        """
        df = self.get_sleep_stage_data(participant_id=participant_id)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id}.")
        
        days = df["day_number"].unique()
        angles = []
        
        for day in days:
            try:
                wake_time = self.compute_wake_time(participant_id, day)
                minutes = wake_time.hour * 60 + wake_time.minute + wake_time.second / 60
                angle = 2 * np.pi * (minutes / 1440)
                angles.append(angle)
            except ValueError:
                if self.verbose:
                    print(f"Skipping day {day} due to missing time.")
                continue

        if len(angles) < 2:
            raise ValueError(f"Not enough valid sleep data to compute wake time regularity for participant {participant_id}.")
        
        sin_sum = np.sum(np.sin(angles))
        cos_sum = np.sum(np.cos(angles))
        R = np.sqrt(sin_sum**2 + cos_sum**2) / len(angles)

        R = np.clip(R, 0, 1)
        wake_time_std_minutes = np.sqrt(-2 * np.log(R)) * (1440 / (2 * np.pi))
        
        if self.verbose:
            print(f"Wake Time Regularity for participant {participant_id}: {wake_time_std_minutes:.2f} minutes")

        return wake_time_std_minutes
    
    def compute_bedtime_reg(self, participant_id):
        """
        Compute bedtime regularity (circular standard deviation) across all days for a participant.

        This metric quantifies the consistency of a participant's bedtime by calculating the circular 
        standard deviation of clock times across multiple days. A lower value indicates more regular bedtimes.

        Parameters:
            participant_id (int): The ID of the participant whose bedtime regularity should be computed.

        Returns:
            float: The circular standard deviation of bedtime in minutes.

        Raises:
            ValueError: If no data is available for the participant or if fewer than two valid bedtimes exist.

        Notes:
            - Bedtime is defined as the 'start_time' of the first row for each day.
            - Time is mapped to angles on a 24-hour circle to account for the cyclical nature of time.
            - Requires at least two valid bedtime values to compute a meaningful result.
        """
        df = self._filter(participant_id=participant_id)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id}.")

        days = df["day_number"].unique()
        angles = []

        for day in days:
            day = int(day)
            try:
                bedtime = self.compute_bedtime(participant_id, day)
                minutes = bedtime.hour * 60 + bedtime.minute + bedtime.second / 60
                angle = 2 * np.pi * (minutes / 1440)
                angles.append(angle)
            except ValueError:
                if self.verbose:
                    print(f"Skipping day {day} due to missing bedtime.")
                continue
        
        if len(angles) < 2:
            raise ValueError(f"Not enough valid sleep data to compute bedtime regularity for participant {participant_id}.")
        
        sin_sum = np.sum(np.sin(angles))
        cos_sum = np.sum(np.cos(angles))
        R = np.sqrt(sin_sum**2 + cos_sum**2) / len(angles)

        R = np.clip(R, 0, 1)
        bedtime_reg = np.sqrt(-2 * np.log(R)) * (1440 / (2 * np.pi))

        if self.verbose:
            print(f"Bedtime regularity for participant {participant_id}: {bedtime_reg:.2f} minutes")

        return bedtime_reg
    
    def compute_midpoint_sleep_reg(self, participant_id):
        """
        Compute midpoint of sleep regularity (circular standard deviation) for a participant across all days.

        This metric quantifies how consistent the midpoint of sleep is from night to night by calculating 
        the circular standard deviation of mid-sleep times. A lower value indicates more regular sleep timing 
        and may reflect a stable circadian rhythm.

        Parameters:
            participant_id (int): The ID of the participant whose midpoint regularity is to be computed.

        Returns:
            float: The circular standard deviation of midpoint of sleep times, in minutes.

        Raises:
            ValueError: If no data is available or if fewer than two valid midpoint values are found.

        Notes:
            - Midpoint of sleep is computed as the time halfway between sleep onset and final wake time.
            - Time is mapped onto a 24-hour circle to properly handle circularity (e.g., 23:30 and 00:30 are close).
            - Days with missing midpoint values are skipped.
            - Requires at least two valid days to compute regularity.
        """
        df = self._filter(participant_id=participant_id)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id}.")

        days = df["day_number"].unique()
        angles = []

        for day in days:
            day = int(day)
            try:
                bedtime = self.compute_midpoint_sleep(participant_id, day)
                minutes = bedtime.hour * 60 + bedtime.minute + bedtime.second / 60
                angle = 2 * np.pi * (minutes / 1440)
                angles.append(angle)
            except ValueError:
                if self.verbose:
                    print(f"Skipping day {day} due to missing midpoint sleep.")
                continue
        
        if len(angles) < 2:
            raise ValueError(f"Not enough valid sleep data to compute midpoint sleep regularity for participant {participant_id}.")
        
        sin_sum = np.sum(np.sin(angles))
        cos_sum = np.sum(np.cos(angles))
        R = np.sqrt(sin_sum**2 + cos_sum**2) / len(angles)

        R = np.clip(R, 0, 1)
        midpoint_reg = np.sqrt(-2 * np.log(R)) * (1440 / (2 * np.pi))

        if self.verbose:
            print(f"Midpoint sleep regularity for participant {participant_id}: {midpoint_reg:.2f} minutes")

        return midpoint_reg