import requests
import pandas as pd

from everfit_config import *

def login(session, email, password):
    """
    Logs into the Everfit API using the provided email and password and retrieves an access token.

    Args:
        session (requests.Session): The active session used to make the login request.
        email (str): The user's email address for login.
        password (str): The user's password for login.

    Returns:
        str: The access token if login is successful, or None if login fails.
    """

    # Validate inputs
    if not isinstance(email, str) or not email.strip():
        raise ValueError("Email must be a non-empty string.")
    if not isinstance(password, str) or not password.strip():
        raise ValueError("Password must be a non-empty string.")

    # Define url
    url = "https://api-prod3.everfit.io/api/auth/login_lite"

    # Define payload
    payload = {
        "email": email,
        "password": password,
        "agent": "react",
    }

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "x-app-type": "web-coach",
    }

    # Send a POST request to log in
    try:
        response = session.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Login request failed: {e}")
        return None
    
    try:
        data = response.json()
    except ValueError as e:
        print(f"Failed to parse response JSON: {e}")
        return None
    
    access_token = data.get('token')
    if access_token:
        print("Logged in successfully.")
        return access_token
    else:
        print("Login failed: No token found in response.")
        return None
    
def put_exercise(session, access_token, exercise_id, payload):

    # Validate inputs
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary.")
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Access token must be a non-empty string.")    
    
    # Define url
    url = "https://api-prod3.everfit.io/api/exercise/update/" + exercise_id

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "X-Access-Token": access_token,
        "X-App-Type": "web-coach",
    }

    # Send the PUT request to update the exercise
    try:
        response = session.put(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to update exercise: {e}")
        return None

    try:
        data = response.json()
    except ValueError as e:
        print(f"Failed to parse response JSON: {e}")
        return None

    return data

def post_exercise(session, payload, access_token):
    """
    Sends a POST request to the Everfit API to add a new exercise.

    Args:
        session (requests.Session): The active session used to make the request.
        payload (dict): The exercise data to be added.
        access_token (str): The access token for authenticating the request.

    Returns:
        Response: The response object from the POST request.
    """

    # Validate inputs
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary.")
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Access token must be a non-empty string.")

    # Define url
    url = "https://api-prod3.everfit.io/api/exercise/add"

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "X-Access-Token": access_token,
        "X-App-Type": "web-coach",
    }

    # Send the POST request to add the exercise
    try:
        response = session.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to add exercise: {e}")
        return None

    try:
        data = response.json()
    except ValueError as e:
        print(f"Failed to parse response JSON: {e}")
        return None

    return data

def get_exercises(session, access_token):
    """
    Retrieves a list of exercises from the Everfit API.

    Args:
        session (requests.Session): The active session used to make the request.
        access_token (str): The access token for authenticating the request.

    Returns:
        dict: The JSON response containing the exercises if successful, or None if the request fails.
    """

    # Validate access_token
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Access token must be a non-empty string.")

    total_exercises = 50

    # Define urls
    url = "https://api-prod3.everfit.io/api/exercise/search_filter_library"

    # Define payload
    payload = {
        "body_part": [],
        "category_type": [],
        "equipments": [],
        "from": [False, True], # [False, True] makes it only the Custom Exercises
        "modalities": [],
        "movement_patterns": [],
        "muscle_groups": [],
        "page": 1,
        "per_page": total_exercises,
        "q": "",
        "sort": -1,
        "sorter": "last_interacted",
        "tags": [],
        "video_only": False
    }

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "x-access-token": access_token,
        "x-app-type": "web-coach",
    }

    # Send a POST request to the url   
    try:
        initial_response = session.post(url, json=payload, headers=headers, timeout=30)
        initial_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve exercises: {e}")
        return None
    
    try:
        initial_data = initial_response.json()
        total_exercises = initial_data.get('total', 0)
        if not isinstance(total_exercises, int) or total_exercises <= 0:
            print("No exercises found.")
            return None
    except ValueError as e:
        print(f"Failed to parse initial response JSON: {e}")
        return None

    payload["per_page"] = total_exercises

    # Send request to get all exercises
    try:
        response = session.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve exercises: {e}")
        return None

    try:
        data = response.json()
    except ValueError as e:
        print(f"Failed to parse response JSON: {e}")
        return None
    
    return data['data']

def get_tag_list(session, access_token):
    """
    Retrieves the full list of tags from the Everfit API.

    Args:
        session (requests.Session): The active session used to make the request.
        access_token (str): The access token for authenticating the request.

    Returns:
        list: A list of tags if successful, or None if the request fails.
    """

    # Validate access_token
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Access token must be a non-empty string.")

    # Define url
    base_url = "https://api-prod3.everfit.io/api/tag/get-list-tag-by-team"

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "x-access-token": access_token,
        "x-app-type": "web-coach",
    }

    # First request to get total number of tags
    params = {
        "sorter": "name",
        "per_page": 1,  # Get minimal data to retrieve total
        "page": 1,
        "sort": 1,
        "text_search": "",
        "type": 1
    }

    try:
        response = session.get(base_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve tags: {e}")
        return None
    
    try:
        data = response.json()
        total_tags = data.get('data', {}).get('total', 0)
        if not isinstance(total_tags, int) or total_tags <= 0:
            print("No tags found.")
            return []
    except ValueError as e:
        print(f"Failed to parse response JSON: {e}")
        return None
    
    # Second request to get all tags
    params['per_page'] = total_tags

    try:
        tag_list_response = session.get(base_url, headers=headers, params=params, timeout=30)
        tag_list_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the full list of tags: {e}")
        return None

    try:
        tag_data = tag_list_response.json()
        tag_list = tag_data.get('data', {}).get('data', [])
    except ValueError as e:
        print(f"Failed to parse tag list JSON: {e}")
        return None

    return tag_list
    
def create_new_tag_id(session, access_token, tag):
    """
    Creates a new tag in the Everfit API and returns the newly created tag's ID.

    Args:
        session (requests.Session): The active session used to make the request.
        access_token (str): The access token for authenticating the request.
        tag (str): The name of the new tag to be created.

    Returns:
        str: The ID of the newly created tag if successful, or None if the request fails.
    """

    # Validate inputs
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Access token must be a non-empty string.")
    if not isinstance(tag, str) or not tag.strip():
        raise ValueError("Tag name must be a non-empty string.")

    # Define url
    url = "https://api-prod3.everfit.io/api/tag"

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "x-access-token": access_token,
        "x-app-type": "web-coach",
    }

    # Define payload
    payload = {
        "name": tag.strip(),
        "type": 1
    }

    # Send a POST request to the url to make a new tag
    try:
        response = session.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to create new tag '{tag}': {e}")
        return None

    try:
        data = response.json()
        tag_data = data.get('data', {})
        tag_id = tag_data.get('_id')
        if not tag_id:
            print(f"Failed to get new tag ID from response.")
            return None
    except ValueError as e:
        print(f"Failed to parse response JSON: {e}")
        return None

    return tag_id

# Helper function to safely get string values
def safe_str(value, default=""):
    if pd.isna(value) or value is None:
        return default
    return str(value)

# Helper function to safely get DataFrame values
def safe_get(df, index, column, default=None):
    if column in df.columns:
        value = df.at[index, column]
        return value if not pd.isna(value) else default
    return default

def get_payload(session, access_token, exercise_info, exercise_df):
    """

    Constructs the payload for uploading an exercise to the Everfit API.

    Args:
        session (requests.Session): The active session used for making requests.
        access_token (str): The access token for authenticating API requests.
        exercise_info (dict): A dictionary containing detailed information about the exercise.

    Returns:
        dict: A dictionary representing the payload with exercise details, ready to be sent to the API.
    """
    
    # Default payload
    payload = {
        "author": "666c67f6c98eb80026f047c9",
        "author_name": "Ruben Lopez Martinez", 
        "title": safe_str(exercise_info.get("exercise_name")),
        "instructions": [] if pd.isna(exercise_info["instructions"]) else safe_str(exercise_info["instructions"]).split('\n'),
        "fields": [],
        "link": "",
        "modality": "66013e83b117d35345209b07",
        "preview_300": "",
        "share": 0,
        "picture": [],
        "thumbnail_url": "",
        "video": "",
        "videoLink": "" if pd.isna(exercise_info.get("video_link", "")) else safe_str(exercise_info.get("video_link", "")),
    }
    
    # Category Type (required)
    category = exercise_info.get("category", "strength")
    if pd.isna(category) or category is None:
        category = "strength"
    category_key = safe_str(category).lower().replace(" ", "")
    payload["category_type"] = CATEGORY_TYPE_MAP.get(category_key, "5cd912c319ae01d22ea76012") # else its the strength category id
    payload["category_type_name"] = category

    # Modality (optional, but has default)
    modality = exercise_info.get("modality", "")
    if not pd.isna(modality) and modality is not None:
        if modality.strip() == "":
            modality = "empty"
        modality_key = safe_str(modality).lower().replace(" ", "")
        payload["modality"] = MODALITY_MAP.get(modality_key, "")
        # error
        if payload["modality"] == "":
            raise Exception(f"Modality {modality} not recognized.")

    # Movement Patterns (optional)
    movement_patterns = []
    for idx, pattern in enumerate(exercise_info.get("movement_patterns", [])):

        if pd.isna(pattern) or pattern is None or pattern == "":
            continue

        pattern_key = safe_str(pattern).lower().replace(" ", "")
        movement_pattern_id = MOVEMENT_PATTERN_MAP.get(pattern_key, "")
        if movement_pattern_id == "":
            raise Exception(f"Movement pattern '{pattern}' not recognized.")
        elif any(d['movement_pattern'] == movement_pattern_id for d in movement_patterns):
            continue
        movement_patterns.append({
            "is_primary": idx == 0,
            "movement_pattern": movement_pattern_id
        })
    payload["movement_patterns"] = movement_patterns

    # Muscle Groups (optional)
    muscle_groups = []
    for idx, muscle in enumerate(exercise_info.get("muscle_groups", [])):
        if pd.isna(muscle) or muscle is None or muscle == "":
            continue
        muscle_key = safe_str(muscle).lower().replace(" ", "")
        muscle_group_id = MUSCLE_GROUP_MAP.get(muscle_key, "")
        if muscle_group_id == "":
            raise Exception(f"Muscle group '{muscle}' not recognized.")
        elif any(d['muscle_group'] == muscle_group_id for d in muscle_groups):
            continue
        muscle_groups.append({
            "is_primary": idx == 0,
            "muscle_group": muscle_group_id
        })
    payload["muscle_groups"] = muscle_groups

    # Tracking Fields (optional)
    tracking_fields = exercise_info.get("tracking_fields", [])
    for field in tracking_fields:
        field_key = field.lower().replace(" ", "")
        field_id = TRACKING_FIELDS_MAP.get(field_key, "")
        if field_id:
            payload["fields"].append(field_id)
    # Always add the "Rest" field
    payload["fields"].append("5cd912bb19ae01d22ea76011")
    
    # Tags
    tags = []
    requested_tags = exercise_info.get("tags", []) #get_requested_tags(exercise_df, exercise_info)  # For old spreadsheet
    tag_list = get_tag_list(session, access_token) or []
    tag_mappings = create_tag_mappings(tag_list)

    # Add or create tag id
    seen_tags = []
    for requested_tag in requested_tags:
        requested_tag = str(requested_tag)
        if requested_tag == "" or requested_tag is None or requested_tag in seen_tags:
            continue
        if requested_tag in tag_mappings:
            tag_id = tag_mappings[requested_tag]
        else:
            tag_id = create_new_tag_id(session, access_token, requested_tag)
        tags.append(tag_id)
        seen_tags.append(requested_tag)
    payload["tags"] = tags

    return payload

def get_exercises_list(start_index, exercise_df, post_exercises_flag=True, put_exercises_flag=False, end_index=-1):
    """
    Extracts a list of exercises and their associated information from a DataFrame.

    Args:
        start_index (int): The row index from which to start reading exercise data.
        exercise_df (DataFrame): The DataFrame containing exercise information.

    Returns:
        list: A list of dictionaries, each containing detailed information about an exercise.
    """

    # Creates a list of exercises with information
    exercises_list = []

    if end_index == -1:
        end_index = len(exercise_df)

    # Goes through each cell with an exercise, adding info to list of exercises
    for i in range(start_index, min(len(exercise_df), end_index+1)):
        # Breaks if at end
        if pd.isna(exercise_df.iloc[i, 0]):
            break
        
        # Continue if video status is not 1
        video_status = safe_get(exercise_df, i, "VIDEO STATUS", 0)
        if post_exercises_flag and video_status != 1:
            continue
        # To update exercises
        elif put_exercises_flag and video_status != 3:
            continue
        
        # Creates a dictionary of exercise info
        exercise_info = {
            "exercise_name": safe_get(exercise_df, i, "EXERCISE NAME", ""),
            "video_status": video_status,
            "description": safe_get(exercise_df, i, "EXERCISE NAME", ""),
            "modality": safe_get(exercise_df, i, "Modality", ""),
            "muscle_groups": [
                safe_get(exercise_df, i, "Muscle group", ""),
                safe_get(exercise_df, i, "Muscle group 2", ""),
                safe_get(exercise_df, i, "Muscle group 3", "")
            ],
            "movement_patterns":  [
                safe_get(exercise_df, i, "Movement pattern 1", ""),
                safe_get(exercise_df, i, "Movement pattern 2", ""),
                safe_get(exercise_df, i, "Movement pattern 3", "")
            ],
            "category": safe_get(exercise_df, i, "Category", "strength"),
            "tracking_fields": safe_get(exercise_df, i, "Tracking fields", ""),
            "instructions": safe_get(exercise_df, i, "Instructions", ""),
            "video_link": safe_get(exercise_df, i, "Video link", ""),
            "tags": {
                "exercise_level_1": safe_get(exercise_df, i, "Basic", 0),
                "exercise_level_2": safe_get(exercise_df, i, "Intermediate", 0),
                "exercise_level_3": safe_get(exercise_df, i, "Advanced", 0),
                "skill_name_1": safe_get(exercise_df, i, "SKILL NAME 1", ""), 
                "skill_name_2": safe_get(exercise_df, i, "SKILL NAME 2", ""), 
                "skill_name_3": safe_get(exercise_df, i, "SKILL NAME 3", ""), 
                "calisthenics": safe_get(exercise_df, i, "Calisthenics", 0),
                "wx_athlete": safe_get(exercise_df, i, "WX Athlete", 0),
                "hp_gymnast": safe_get(exercise_df, i, "HP gymnast", 0),
                "equipment_1": safe_get(exercise_df, i, "EQUIPMENT 1", ""), 
                "equipment_2": safe_get(exercise_df, i, "EQUIPMENT 2", ""), 
                "equipment_3": safe_get(exercise_df, i, "EQUIPMENT 3", ""), 
                "equipment_4": safe_get(exercise_df, i, "EQUIPMENT 4", ""), 
                "warm_up": safe_get(exercise_df, i, "Warm up", 0),
                "cardio": safe_get(exercise_df, i, "Cardio", 0),
                "crossfit_lift": safe_get(exercise_df, i, "Crossfit lift", 0),
                "bodyweight": safe_get(exercise_df, i, "Bodyweight", 0),
                "weight": safe_get(exercise_df, i, "Weight", 0),
                "band_resistance": safe_get(exercise_df, i, "Band resistance", 0),
                "weightlifting": safe_get(exercise_df, i, "Weightlifting", 0),
                "mobility": safe_get(exercise_df, i, "mobility", 0),
                "active": safe_get(exercise_df, i, "active", 0),
                "passive": safe_get(exercise_df, i, "passive", 0),
                "stretching": safe_get(exercise_df, i, "stretching", 0),
                "upperbody": safe_get(exercise_df, i, "Upperbody", 0),
                "lowerbody": safe_get(exercise_df, i, "Lowerbody", 0),
                "core": safe_get(exercise_df, i, "Core", 0),
                "push": safe_get(exercise_df, i, "Push", 0),
                "pull": safe_get(exercise_df, i, "Pull", 0),
                "arms_straight": safe_get(exercise_df, i, "Arms straight", 0),
                "arms_bend": safe_get(exercise_df, i, "Arms bend", 0),
                "iso": safe_get(exercise_df, i, "Iso", 0),
                "plyo": safe_get(exercise_df, i, "Plyo", 0),
                "set": safe_get(exercise_df, i, "Set", 0),
                "shoulders": safe_get(exercise_df, i, "Shoulders", 0),
                "pecs": safe_get(exercise_df, i, "Pecs", 0),
                "triceps": safe_get(exercise_df, i, "Triceps", 0),
                "biceps": safe_get(exercise_df, i, "Biceps", 0),
                "back": safe_get(exercise_df, i, "Back", 0),
                "abs": safe_get(exercise_df, i, "Abs", 0),
                "lower_back": safe_get(exercise_df, i, "Lower back", 0),
                "obliques": safe_get(exercise_df, i, "Obliques", 0),
                "glute": safe_get(exercise_df, i, "Glute", 0),
                "quads": safe_get(exercise_df, i, "Quads", 0),
                "hamstrings": safe_get(exercise_df, i, "Hamstrings", 0),
                "calves": safe_get(exercise_df, i, "Calves", 0),
                "wrist": safe_get(exercise_df, i, "Wrist", 0),
                "hips": safe_get(exercise_df, i, "Hips", 0),
                "elbows": safe_get(exercise_df, i, "Elbows", 0),
                "ankle": safe_get(exercise_df, i, "Ankle", 0),
                "thoracic": safe_get(exercise_df, i, "Thoracic", 0),
                "forearms": safe_get(exercise_df, i, "Forearms", 0),
                "neck": safe_get(exercise_df, i, "Neck", 0),
                "pull_up": safe_get(exercise_df, i, "Pull up", 0),
                "push_up": safe_get(exercise_df, i, "Push up", 0),
                "dip": safe_get(exercise_df, i, "Dip", 0),
                "row": safe_get(exercise_df, i, "Row", 0),
                "press": safe_get(exercise_df, i, "Press", 0),
                "curl": safe_get(exercise_df, i, "Curl", 0),
                "squat": safe_get(exercise_df, i, "Squat", 0),
                "bridge": safe_get(exercise_df, i, "Bridge", 0),
                "throws": safe_get(exercise_df, i, "Throws", 0),
                "slams": safe_get(exercise_df, i, "Slams", 0),
                "sit_up": safe_get(exercise_df, i, "Sit up", 0),
                "leg_lift": safe_get(exercise_df, i, "Leg lift", 0),
                "balance": safe_get(exercise_df, i, "Balance", 0),
                "raise": safe_get(exercise_df, i, "Raise", 0),
                "rocks": safe_get(exercise_df, i, "Rocks", 0),
                "arch-hollow_shape": safe_get(exercise_df, i, "Arch-hollow shape", 0),
                "rotation": safe_get(exercise_df, i, "Rotation", 0),
                "gymnastics_skill": safe_get(exercise_df, i, "Gymnastics skill", 0),
                "plank": safe_get(exercise_df, i, "Plank", 0),
                "preS_explosive": safe_get(exercise_df, i, "PreS explosive", 0),
                "preS_legs": safe_get(exercise_df, i, "PreS legs", 0),
                "postS_legs": safe_get(exercise_df, i, "PostS legs", 0),
                "postS_rings": safe_get(exercise_df, i, "PostS rings", 0),
                "postS_altern_rings": safe_get(exercise_df, i, "PostS altern rings", 0),
                "postS_weights": safe_get(exercise_df, i, "PostS weights", 0),
            }  
        }

        # Adds to list of exercises
        exercises_list.append(exercise_info)

    return exercises_list

def create_tag_mappings(tag_list):
    """
    Creates a dictionary mapping tag names to their corresponding IDs.

    Args:
        tag_list (list): A list of dictionaries where each dictionary contains
                         'name' and '_id' fields representing a tag.

    Returns:
        dict: A dictionary where keys are tag names and values are tag IDs.
    """
    tag_mappings = {}
    for tag in tag_list:
        tag_mappings[tag['name']] = tag['_id']
    return tag_mappings

def get_requested_tags(exercise_df, exercise_info):
    """
    Retrieves a list of requested tags based on exercise information.

    Args:
        exercise_df (DataFrame): The DataFrame containing the exercise data.
        exercise_info (dict): A dictionary containing details about the exercise, 
                              including a 'tags' field.

    Returns:
        list: A list of tag names associated with the exercise.
    """
    requested_tags = []
    string_cols = ["SKILL NAME 1", "SKILL NAME 2", "SKILL NAME 3", "EQUIPMENT 1", "EQUIPMENT 2", "EQUIPMENT 3", "EQUIPMENT 4"]
    col_names = exercise_df.columns.tolist()
    cur_tag_col = col_names.index("Basic")

    # Goes through each tag, adding the proper tag name to the list
    for key, val in exercise_info.get('tags', {}).items():
        col_name = col_names[cur_tag_col]
        # Skip if na or 0
        if pd.isna(val) or val == 0 or val is None or val == "":
            cur_tag_col += 1
            continue
        # Add value if in string_cols, else add col name
        if col_name in string_cols:
            requested_tags.append(val)
        else:
            requested_tags.append(col_name)
        cur_tag_col += 1
            
    return requested_tags