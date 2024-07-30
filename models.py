# models.py
import pandas as pd
import re
from dataformat import *
import os
import datetime
import sys
import numpy as np
#
class Employee:
    def __init__(self, name, work_time=0, holiday_hours=0, absent_hours=0, sick_hours=0, vacation_hours=0, overtime_hours=0):
        self.name = name
        self.work_time = work_time
        self.holiday_hours = holiday_hours
        self.absent_hours = absent_hours
        self.sick_hours = sick_hours
        self.vacation_hours = vacation_hours
        self.overtime_hours = overtime_hours
        self.hours_minutes_format = "0:00"

    def __str__(self):
        return (f"\nEmployee(name={self.name}, work_time={self.work_time}, hours_minutes_format={self.hours_minutes_format}, "
                f"holiday_hours={self.holiday_hours}, absent_hours={self.absent_hours}, sick_hours={self.sick_hours}, "
                f"vacation_hours={self.vacation_hours}, overtime_hours={self.overtime_hours})")

    def print_work_hours(self):
        print(f"EMPLOYEE: {self.name}\nTOTAL HOURLY: {self.work_time}\nOVERTIME HOURS:{self.overtime_hours}"
              f"\nVACATION {self.vacation_hours}\nSICK {self.sick_hours}\nHOLIDAY {self.holiday_hours}\nABSENT {self.absent_hours}")


#to do
#put names in order
#check totals
#use

def extract_employee_names(df):
    employee_names = []

    for index, row in df.iterrows():
        # Check if the current row is followed by "TIME IN"
        if index + 1 < len(df):
            next_row = df.iloc[index + 1]
            # print(f'Next row{next_row.iloc[0]}')
            if pd.notna(next_row.iloc[0]) and isinstance(next_row.iloc[0], str) and next_row.iloc[0].strip().lower() == 'time in':
                # The current row contains the employee name
                if pd.notna(row.iloc[0]) and row.iloc[0] != '':
                    employee_names.append(row.iloc[0])

    return employee_names

def create_employees(employee_names):
    employees = [Employee(name) for name in employee_names]
    return employees


def rows_to_keep(employee_names,df):
    employees = employee_names
    repeated_index = [name for name in employees for _ in range(5)]
    num_rows_to_keep = len(employee_names)*5
    df = df.iloc[:num_rows_to_keep]
    df.index = repeated_index
    # print(df.to_string())
    return df

def get_employee_df(df,employee_name):
    filtered_df = df.loc[employee_name]
    return filtered_df

def get_valid_columns(df):
    subset_df = df.iloc[1:4, :]
    subset_df = subset_df.iloc[:, 1:14]
    valid_columns = subset_df.columns[subset_df.notna().all(axis=0)]
    filtered_df = subset_df[valid_columns]
    return filtered_df

def get_hours(df):
    def convert_to_time(time):
        time = time.strip()
        # print('time')
        # print(time)

        # Correct regex patterns
        pattern_hh_mm_ss = r'(\d{1,2}):(\d{2}):(\d{2})'  # Matches HH:MM:SS
        pattern_hh_mm = r'(\d{1,2}):(\d{2})'  # Matches HH:MM

        match_3 = re.match(pattern_hh_mm_ss, time)
        match_2 = re.match(pattern_hh_mm, time)

        if match_3:
            # print('match HH:MM:SS')
            hour = int(match_3.group(1))  # Extract the hour
            minute = int(match_3.group(2))  # Extract the minute
            second = int(match_3.group(3))  # Extract the second
            # print(f"Hour: {hour}, Minute: {minute}, Second: {second}")
            total = float(hour * 60 + minute)
            # print('total minutes')
            # print(total)
            return total

        elif match_2:
            # print('match HH:MM')
            hour = int(match_2.group(1))  # Extract the hour
            minute = int(match_2.group(2))  # Extract the minute
            total = float(hour * 60 + minute)
            # print('total minutes')
            # print(total)
            return total

        else:
            # print(f"{time} does not match any known time format.")
            return None

    def check_overtime(week1, week2):
        max = 40
        overtime1 = week1-max
        overtime2 = week2-max
        if overtime1 > 0 and overtime2 > 0:
            return overtime1+overtime2
        if overtime1 > 0:
            return overtime1
        if overtime2> 0:
            return overtime2
        else:
            return 0


    sum_minutes = 0
    hours_by_week1 = 0
    hours_by_week2 = 0
    for column_name, column_data in df.items():
        week1 = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        week2 = ['Mon2', 'Tue2', 'Wed2', 'Thu2', 'Fri2']
        values = [convert_to_time(str(value)) for value in column_data]
        start, end, bre = values[0], values[1], values[2]
        total = end - bre - start
        if column_name in week1:
            hours_by_week1 += total

        if column_name in week2:
            hours_by_week2 += total

        sum_minutes += total

    total_hours_by_week1 = hours_by_week1 / 60
    total_hours_by_week2 = hours_by_week2 / 60
    overtime = check_overtime(total_hours_by_week1, total_hours_by_week2)
    total_hours = sum_minutes / 60
    minutes_format = int(sum_minutes % 60)
    hours_minutes_format = int(sum_minutes / 60)
    hours_minutes_format = f'{hours_minutes_format}.{str(minutes_format).zfill(2)}'
    hours_minutes_format = float(hours_minutes_format)

    return total_hours, hours_minutes_format, sum_minutes, overtime

# def pattern():
#     pattern = ["time in", "time out", "break", "total"]

def count_vacation_occurrences(df):
    count = (df.map(lambda x: isinstance(x, str) and x.lower() == 'vacation')).sum().sum()
    return count

def count_absent_occurrences(df):
    count = (df.map(lambda x: isinstance(x, str) and x.lower() == 'absent')).sum().sum()
    return count

def count_holiday_occurrences(df):
    count = (df.map(lambda x: isinstance(x, str) and x.lower() == 'holiday')).sum().sum()
    return count
def count_sick_occurrences(df):
    count = (df.map(lambda x: isinstance(x, str) and x.lower() == 'sick')).sum().sum()
    return count

def check_same(df):
    df = df.dropna(axis=1, how='all')
    non_empty_values = df.iloc[:, 13].dropna().tolist()
    # print(f'total values found in excel {non_empty_values}')
    return non_empty_values
def compare_list_details(list1, sum_minutes, list2, employee):
    list2 = f"{list2:.2f}"
    parts = list2.split('.')
    hours = parts[0]
    minutes = parts[1]
    parts = int(hours)*60+int(minutes)
    print(f'the sum minutes = {sum_minutes} and the list2 {list2} and the parts {parts} and the hours = {hours} and the minutes = {minutes}')
    if sum_minutes != parts:
        print(f"{employee} INCORRECT\nHH:MM value is {list1} but Excel sheet shows {list2}.")
    else:
        print(f"{employee} CORRECT")

def main(file_path):
    df = pd.read_excel(file_path)
    first_column = df.iloc[:, 0]
    first_column_list = first_column.tolist()
    first_column_list = nan_none(first_column_list)
    first_column_list = time_total(first_column_list)
    df.iloc[:,0]=first_column_list
    check_original = check_same(df)
    df = merge_rows(df)

    employee_names = extract_employee_names(df)

    df = rows_to_keep(employee_names, df)
    employees = create_employees(employee_names)

    for index, employee in enumerate(employees):
        df_sub = get_employee_df(df, employee.name)
        vacation_count = count_vacation_occurrences(df_sub)
        absent = count_absent_occurrences(df_sub)
        holiday = count_holiday_occurrences(df_sub)
        sick = count_sick_occurrences(df_sub)


        num_columns = df_sub.shape[1]
        # Define the base column names
        df_col = ['Row Title', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'NaN', 'Mon2', 'Tue2', 'Wed2', 'Thu2', 'Fri2']

        # Generate the column names dynamically
        columns = []
        nan_count = 1
        base_columns_length = 12
        for i in range(num_columns):
            if i < base_columns_length:
                columns.append(df_col[i])
            else:
                columns.append(f'NaN{nan_count}')
                nan_count += 1

        # Assign the generated column names to the dataframe
        df_sub.columns = columns

        df_work_hours = get_valid_columns(df_sub)
        # print('final df')
        # print(df_work_hours.shape)
        # print(df_work_hours.to_string())
        # print('valid df')
        # print(df_work_hours.to_string())

        # print('good rows df')
        # print(df_work_hours.to_string())
        total_hours, hours_minutes_format, sum_minutes, overtime = get_hours(df_work_hours)
        employee.work_time = total_hours
        employee.hours_minutes_format = hours_minutes_format
        check_computer = employee.hours_minutes_format
        employee.vacation_hours = vacation_count
        employee.absent_hours = absent
        employee.holiday_hours = holiday
        employee.sick_hours = sick
        employee.overtime_hours = overtime
        compare_list_details(check_computer, sum_minutes, check_original[index], employee.name)
        print(f'File path used: {file_path}')
        employee.print_work_hours()
        print('\n')





def models(file_path):


    # Define the end date
    end_date = datetime.datetime(2024, 8, 8)  # Example: 5th August 2024

    # Get the current date
    current_date = datetime.datetime.now()

    # Check if the current date is past the end date
    if current_date > end_date:
        print("This script is no longer allowed to run after the specified date.")
        return  # Exit the script

    # The rest of your script
    print("Running script... Deadline to renew is: 8th August 2024")

    if os.path.isfile(file_path):
        main(file_path)
    elif os.path.isdir(file_path):
        for filename in os.listdir(file_path):
            # Construct full file path
            full_path = os.path.join(file_path, filename)

            # Check if it's an Excel file and not a hidden file
            if filename.startswith('.') or not filename.lower().endswith('.xlsx'):
                continue

            # Call main with the full file path
            main(full_path)
#
# file_path = '/Users/jinhe/Downloads/Payflex'
# models(file_path)
