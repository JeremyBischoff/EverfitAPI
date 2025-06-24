import pandas as pd
import requests
import getpass
import re
from itertools import zip_longest

from everfit_api import login, post_exercise, get_exercises, put_exercise, get_payload, get_exercises_list

def upload_exercises_to_everfit():
    # Start a session
    session = requests.Session()

    # Get user credentials from user input
    email = input("Enter your Everfit email: ").strip()
    password = getpass.getpass("Enter your Everfit password: ").strip()

    # Log in to Everfit API
    access_token = login(session, email, password)
    if not access_token:
        print("Failed to log in. Exiting.")
        return
    
    # Load exercise data from Excel
    file_path = input("Enter the path to the Excel file: ").strip()
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        print("Excel file not found. Please check the path and try again.")
        return
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return
    
    exercises_info = []
    
    # Get exercise information from Excel
    for idx, row in df.iterrows():
        # Handle NaN values in "Everfit Uploaded" column
        everfit_uploaded = row.get("Everfit Uploaded", 0)
        if pd.isna(everfit_uploaded):
            everfit_uploaded = 0
        elif everfit_uploaded == 1:
            continue
        
        # Skip rows with NaN exercise names
        exercise_name = row.get("Name", "")
        if pd.isna(exercise_name) or exercise_name == "":
            continue
            
        print(f"Processing exercise: {exercise_name}")

        # Helper function to safely handle string operations on potentially NaN values
        def safe_string_split(value, delimiter=";"):
            if pd.isna(value) or value == "":
                return []
            return [part.strip() for part in str(value).split(delimiter) if part.strip()]

        raw_instructions = row.get("Instructions", "")
        instruction_parts = safe_string_split(raw_instructions)
        raw_spanish_instructions = row.get("Spanish Instructions", "")
        spanish_instruction_parts = safe_string_split(raw_spanish_instructions)
        # Strip numbering
        instruction_parts = [re.sub(r'^\d+\.\s*', '', s) for s in instruction_parts]
        spanish_instruction_parts = [re.sub(r'^\d+\.\s*', '', s) for s in spanish_instruction_parts]
        # Pair each English with Spanish counterpart
        instructions = []
        for eng, spa in zip_longest(instruction_parts, spanish_instruction_parts, fillvalue=""):
            pair = " | ".join(p for p in (eng, spa) if p)
            instructions.append(pair)
        # Separate by newline
        instructions_mixed = "\n".join(instructions)

        movement_patterns = safe_string_split(row.get("Movement Patterns", ""))
        muscle_groups = safe_string_split(row.get("Muscle Group", ""))
        tracking_fields = safe_string_split(row.get("Tracking Fields", ""))
        tags = safe_string_split(row.get("Exercise Tags", ""))

        exercise_info_dict = {
            # (required) Title of the exercise
            "exercise_name": exercise_name,  # str

            # (optional) Multi‐line instructions (each "n" becomes a separate list element)
            # Either:
            #   • a single string with newline separators, e.g. "Line 1nLine 2", or
            #   • None/NaN if you want payload["instructions"] == []
            "instructions": instructions_mixed,  # str (possibly containing "n") or pandas.NaN

            # (optional) Which modality this exercise falls under.
            # Must match one of the keys in MODALITY_MAP (e.g. "bodyweight", "dumbbell", etc.), or ""/NaN to leave default.
            "modality": "",  # str

            # (required) Primary category, e.g. "strength", "flexibility", etc.
            # Must match a key in CATEGORY_TYPE_MAP (lowercased, no spaces). If blank/NaN, defaults to "strength".
            "category": "",  # str

            # (optional) A list of movement‐pattern names (each must match a key in MOVEMENT_PATTERN_MAP).
            # The first element is treated as primary (is_primary=True), any duplicates are ignored.
            "movement_patterns": movement_patterns,  # list[str]

            # (optional) A list of muscle‐group names (each must match a key in MUSCLE_GROUP_MAP).
            # The first element is treated as primary (is_primary=True), duplicates are ignored.
            "muscle_groups": muscle_groups,  # list[str]

            # (optional) Any tracking fields you want (comma‐separated string).
            # Example: "Reps,Weight,Duration". Each token is looked up in TRACKING_FIELDS_MAP.
            # If blank/NaN, it will simply add the default "Rest" field.
            "tracking_fields": tracking_fields,  # str or pandas.NaN

            # (optional) A URL for a demo video. If blank/NaN, payload["videoLink"] becomes "".
            "video_link": str(row.get("Video Link", "")),  # str or pandas.NaN

            # (optional) A dictionary of tag‐columns from your Excel sheet. get_requested_tags(...) will scan through this dict 
            # and pick any column whose value is nonzero/nonnull. Keys should match the column names in your sheet, e.g.:
            #    "exercise_level_1", "exercise_level_2", "exercise_level_3",
            #    "SKILL NAME 1", "SKILL NAME 2", "SKILL NAME 3",
            #    "EQUIPMENT 1", "EQUIPMENT 2", … etc.
            # Values are typically 0/1 or blank. get_requested_tags(...) only cares if value != 0/NaN.
            "tags": tags,
        }
        exercises_info.append(exercise_info_dict)
    
    # Upload each exercise to Everfit
    for exercise_info in exercises_info:
        name = exercise_info.get("exercise_name", "Unknown")
        try:
            payload = get_payload(session, access_token, exercise_info, df)
        except Exception as e:
            print(f"Error generating payload for exercise {name}: {e}")
            continue
        
        response = post_exercise(session, payload, access_token)
        if response and response.get("exercise"):
            print(f"Successfully added '{name}'")
            df.loc[df["Name"] == name, "Everfit Uploaded"] = 1
        else:
            print(f"Failed to add '{name}'. Response: {response}")

    # Save the updated Excel file
    df.to_excel(file_path, index=False)

    print(f"Updated {len(exercises_info)} exercises in {file_path}")

    session.close()

def main():
    upload_exercises_to_everfit()

if __name__ == "__main__":
    main()