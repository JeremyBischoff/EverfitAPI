import pandas as pd
import requests
import getpass

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
        if int(row.get("Everfit Uploaded", 1)) == 1:
            continue
        print(f"Processing exercise: {row['Name']}")

        raw_instructions = row.get("Instructions", "")
        instruction_parts = [part.strip() for part in raw_instructions.split(";") if part.strip()]
        raw_spanish_instructions = row.get("Spanish Instructions", "")
        spanish_instruction_parts = [part.strip() for part in raw_spanish_instructions.split(";") if part.strip()]
        instructions = []  # English and Spanish instructions combined
        max_len = max(len(instruction_parts), len(spanish_instruction_parts))
        for i in range(max_len):
            if i < len(instruction_parts):
                instructions.append(instruction_parts[i])
            if i < len(spanish_instruction_parts):
                instructions.append(spanish_instruction_parts[i])
        instructions_mixed = "\n".join(instructions)

        raw_movement_patterns = row.get("Movement Patterns", "")
        movement_patterns = [pattern.strip() for pattern in raw_movement_patterns.split(";") if pattern.strip()]

        raw_muscle_groups = row.get("Muscle Group", "")
        muscle_groups = [group.strip() for group in raw_muscle_groups.split(";") if group.strip()]

        raw_tracking_fields = row.get("Tracking Fields", "")
        tracking_fields = [field.strip() for field in raw_tracking_fields.split(";") if field.strip()]

        raw_tags = row.get("Exercise Tags", "")
        tags = [tag.strip() for tag in raw_tags.split(";") if tag.strip()]

        exercise_info_dict = {
            # (required) Title of the exercise
            "exercise_name": row["Name"],  # str

            # (optional) Multi‐line instructions (each “\n” becomes a separate list element)
            # Either:
            #   • a single string with newline separators, e.g. "Line 1\nLine 2", or
            #   • None/NaN if you want payload["instructions"] == []
            "instructions": instructions_mixed,  # str (possibly containing "\n") or pandas.NaN

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
            # If blank/NaN, it will simply add the default “Rest” field.
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