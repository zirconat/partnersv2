import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from PIL import Image
import io
import base64
from pathlib import Path
import os
import json

# --- MUST BE THE FIRST STREAMLIT COMMAND ---
st.set_page_config(layout="wide", page_title="Contact Card App 📞")

# --- 0. Data Initialization and Session State Management ---
# Define all expected columns for the DataFrame
EXPECTED_COLUMNS = [
    "Name", "Designation", "Country", "Company", "Phone Number",
    "Office Number", "Email Address", "Posting Date", "Deposted Date",
    "Office Address", "Home Address", "Hobbies", "Dietary Restrictions",
    "Festivities", "Vehicle", "Golf", "Golf Handicap", "Reception",
    "Marital Status", "Children (Son)", "Children (Daughter)",
    "Date of Birth", "Known Age (Current Year)",
    "Status", "Tiering", "Category", "Photo", "Comments",
    "Last Updated By", "Last Updated On", "History"
]

# Define the GMT+8 offset
GMT8_OFFSET = timedelta(hours=8)

# Helper function to get current time in GMT+8
def get_gmt8_now():
    # Get current UTC time and add the GMT+8 offset
    return datetime.utcnow() + GMT8_OFFSET

if 'contacts_df' not in st.session_state:
    st.session_state.contacts_df = pd.DataFrame(columns=EXPECTED_COLUMNS)

    # Initial sample data (ensure it aligns with EXPECTED_COLUMNS)
    initial_data = [
        # Local Rep Category (2 samples)
        ["Albert Tan", "Senior Manager", "Singapore", "Tech Innovations", "98765432", "67890123", "albert.t@techinnov.com", date(2025, 8, 12), None, "123 Orchard Rd", "456 Home Rd, Singapore", "Gaming", "Vegetarian", "Deepavali", "BMW X5", "Yes", "20", "NYR, ALSE", "Married", 1, 1, date(1980, 5, 15), None, "Active", "A", "Local Rep", None, [], "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"),[]],
        ["Serene Lim", "Marketing Lead", "Singapore", "Creative Solutions", "91234567", "61234567", "serene.l@creatives.com", date(2024, 3, 1), None, "789 Marina Blvd", "10 Queen St, Singapore", "Yoga", "None", "Chinese New Year", "Mercedes C-Class", "No", "N/A", "Client Event", "Single", 0, 0, date(1992, 11, 22), None, "Active", "B", "Local Rep", None, [], "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"),[]],

        # Overseas Rep Category (2 samples)
        ["Bob Johnson", "Regional Director", "Australia", "Global Reach Inc.", "0412345678", "029876543", "bob.j@globalreach.com", date(2023, 1, 20), None, "Sydney CBD", "Melbourne Suburbs", "Surfing", "None", "Australia Day", "Ford Ranger", "Yes", "15", "Networking Mixer", "Married", 2, 1, date(1975, 7, 10), None, "Active", "A+", "Overseas Rep", None, [], "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"),[]],
        ["Catherine Dubois", "Business Development", "France", "EuroConnect", "0612345678", "0123456789", "catherine.d@euroconnect.fr", date(2022, 10, 5), None, "Paris Office", "Nice Apartment", "Art, Cooking", "Pescatarian", "Bastille Day", "Renault Clio", "No", "N/A", "Industry Fair", "Single", 0, 0, date(1988, 2, 29), None, "Active", "B", "Overseas Rep", None, [], "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"),[]],

        # Chief Category (2 samples)
        ["Chief Lee", "Chief Strategy Officer", "USA", "Innovate Global", "123-456-7890", "987-654-3210", "clee@innovateglobal.com", date(2021, 5, 1), None, "New York HQ", "Greenwich, CT", "Golf, Philanthropy", "None", "Thanksgiving", "Tesla Model S", "Yes", "5", "Board Meeting", "Married", 2, 2, date(1965, 9, 3), None, "Active", "A+", "Chief", None, [], "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"),[]],
        ["Maria Gomez", "Chief Financial Officer", "Spain", "Finance Leaders", "600112233", "910112233", "maria.g@financeleaders.es", date(2020, 1, 1), None, "Madrid HQ", "Barcelona Apartment", "Sailing, Reading", "Gluten-Free", "Christmas", "Audi Q7", "No", "N/A", "Investor Call", "Married", 1, 1, date(1970, 4, 25), None, "Active", "A", "Chief", None, [], "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"),[]],

        # Dy Chief Category (2 samples)
        ["David Chen", "Deputy Chief Architect", "China", "Future Systems", "13800138000", "01012345678", "david.c@futuresystems.cn", date(2023, 7, 15), None, "Beijing R&D Center", "Shanghai Penthouse", "Calligraphy", "None", "Lunar New Year", "BYD Han", "Yes", "10", "Tech Conference", "Married", 1, 0, date(1978, 8, 8), None, "Active", "A", "Dy Chief", None, [], "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"),[]],
        ["Sarah White", "Deputy Chief of Staff", "UK", "Government Affairs", "07700900123", "02012345678", "sarah.w@govaffairs.co.uk", date(2024, 2, 20), None, "Whitehall Office", "Rural Estate", "Horse Riding", "Dairy-Free", "Royal Jubilee", "Range Rover", "No", "N/A", "Parliament Session", "Single", 0, 0, date(1985, 6, 1), None, "Active", "B", "Dy Chief", None, [], "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"),[]],

        # ID Category (2 samples)
        ["Ivan Petrov", "Independent Consultant", "Russia", "Self-Employed", "9012345678", "N/A", "ivan.p@consult.ru", date(2024, 4, 1), None, "Moscow Home Office", "St. Petersburg Apartment", "Skiing", "None", "Victory Day", "Lada Vesta", "No", "N/A", "Project Review", "Divorced", 1, 0, date(1973, 1, 1), None, "Active", "C", "ID", None, [], "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"),[]],
        ["Unknown Child Example", "Tester", "USA", "TestCo","111", "222", "unknown@test.com", date(2025, 1, 1), None, "Test Address", "Test Home", "Testing", "None", "None", "bicycle", "No", "N/A", "Review", "Single", None, None, None, None, "Active", "B", "ID", None, [], "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"),[]],


        # Others Category (2 samples)
        ["Zoe Adams", "Freelance Writer", "Canada", "Self-Employed", "555-555-1212", "N/A", "zoe.a@freelance.com", date(2024, 6, 1), None, "Vancouver Cafe", "Whistler Cabin", "Writing, Hiking", "Vegan", "Canada Day", "Electric Scooter", "No", "N/A", "Book Launch", "Single", 0, 0, date(1995, 3, 3), None, "Active", "Untiered", "Others", None, [], "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"),[]],
        ["Youssef Hassan", "Community Organizer", "Egypt", "Local NGO", "01012345678", "N/A", "youssef.h@ngo.org", date(2025, 1, 1), None, "Cairo Community Center", "Giza Flat", "Volunteering", "Halal", "Eid al-Fitr", "Bicycle", "No", "N/A", "Charity Event", "Married", 0, 0, date(1982, 10, 10), None, "Active", "C", "Others", None, [], "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"),[]],
    ]

    # Create the initial DataFrame from the sample data
    st.session_state.contacts_df = pd.DataFrame(initial_data, columns=EXPECTED_COLUMNS)


# Ensure all EXPECTED_COLUMNS are present in the DataFrame, adding them if missing
for col in EXPECTED_COLUMNS:
    if col not in st.session_state.contacts_df.columns:
        # For numerical columns like children, initialize with None for "Unknown"
        if col in ["Children (Son)", "Children (Daughter)", "Date of Birth", "Known Age (Current Year)"]:
            st.session_state.contacts_df[col] = None
        elif col == "Comments": # Initialize comments as an empty list
            st.session_state.contacts_df[col] = [[] for _ in range(len(st.session_state.contacts_df))]
        elif col == "History": # Initialize history as an empty list
            st.session_state.contacts_df[col] = [[] for _ in range(len(st.session_state.contacts_df))]
        else:
            st.session_state.contacts_df[col] = None # Or an appropriate default value like ""

# Define ALL valid categories
valid_categories = ["Local Rep", "Overseas Rep", "Chief", "Dy Chief", "ID", "Others"]
if 'contacts_df' in st.session_state:
    st.session_state.contacts_df['Category'] = st.session_state.contacts_df['Category'].apply(
        lambda x: x if x in valid_categories else "Others" # Default to "Others" for unrecognized categories
    )

# Initialize selected category for buttons
if 'selected_category_button' not in st.session_state:
    st.session_state.selected_category_button = "All" # Default to showing all

if 'user_role' not in st.session_state:
    st.session_state.user_role = None

if 'show_add_form' not in st.session_state:
    st.session_state.show_add_form = False

if 'editing_contact_index' not in st.session_state:
    st.session_state.editing_contact_index = None

# --- Standard Lists ---
STANDARD_COUNTRIES = [
    "United States", "Canada", "Mexico", "Brazil", "Argentina",
    "United Kingdom", "France", "Germany", "Italy", "Spain", "Netherlands",
    "Switzerland", "Sweden", "Norway", "Denmark", "Ireland", "Belgium",
    "Australia", "New Zealand", "China", "India", "Japan", "South Korea",
    "Singapore", "Malaysia", "Indonesia", "Thailand", "Philippines", "Vietnam",
    "United Arab Emirates", "Saudi Arabia", "Qatar", "South Africa", "Egypt",
    "Nigeria", "Kenya", "Israel", "Turkey", "Russia", "Ukraine", "Poland",
    "Portugal", "Greece", "Austria", "Finland", "Czech Republic", "Hungary",
    "Chile", "Colombia", "Peru", "Pakistan", "Bangladesh", "Sri Lanka",
    # Add more countries as needed
]
STANDARD_COUNTRIES.sort() # Keep them sorted for easier selection

# Removed RECEPTION_OPTIONS as a fixed list; it will now be dynamically populated from data + custom inputs
# RECEPTION_OPTIONS = ["ALSE", "NYR", "Others"]

COMMON_FESTIVITIES = [
    "Chinese New Year", "Deepavali", "Christmas", "Hari Raya Puasa", "Eid al-Fitr",
    "Eid al-Adha", "Halloween", "Thanksgiving", "Diwali", "New Year's Day",
    "Easter", "Ramadan", "Hanukkah", "Oktoberfest", "Carnival",
    "St. Patrick's Day", "Independence Day (US)", "Canada Day", "Bastille Day"
    # Add more common festivities
]
COMMON_FESTIVITIES.sort() # Keep them sorted

MARITAL_STATUS_OPTIONS = ["Single", "Married", "Divorced", "Widowed", "Separated", "Prefer not to say"]

# Options for children dropdown - Now includes '0'
CHILDREN_OPTIONS = ["Unknown", 0] + list(range(1, 11)) # Unknown, 0, 1, 2, ..., 10

# New Tiering Options
TIERING_OPTIONS = ["A+", "A", "B", "C", "Untiered"]

# --- Define Protocol Order for Categories (Still useful for filters/categorization) ---
PROTOCOL_ORDER_CATEGORIES = [
    "Chief",
    "Dy Chief",
    "Local Rep",
    "Overseas Rep",
    "ID",
    "Others"
]

# --- NEW: Define Protocol Order for Designations ---
DESIGNATION_PROTOCOL_RANKS = {
    # Keywords are case-insensitive. Lower rank number means higher protocol.
    "chief": 1,
    "deputy chief": 2,
    "director": 3,
    "head of": 4,
    "manager": 5,
    "lead": 6,
    "officer": 7,
    "consultant": 8,
    "business development": 9,
    "marketing lead": 10,
    "specialist": 11,
    "executive": 12,
    "writer": 13,
    "organizer": 14,
    "tester": 15,
}
# Default rank for designations not matching any keyword (put them at the bottom)
DEFAULT_DESIGNATION_RANK = 99

# Global variable for fields that can be bulk updated
BULK_UPDATE_FIELDS = [
    "Office Address",
    "Festivities",
    "Vehicle",
    "Reception",
    "Tiering"
]

# --- 1. User Authentication ---
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username == "admin" and password == "adminpass":
            st.session_state.user_role = "admin"
            st.sidebar.success("Logged in as Admin!")
            st.rerun()
        elif username == "user" and password == "userpass":
            st.session_state.user_role = "user"
            st.sidebar.success("Logged in as User!")
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password")

def logout():
    if st.sidebar.button("Logout"):
        st.session_state.user_role = None
        st.rerun()

# --- Helper function to process multi-select and custom text inputs ---
def process_multi_text_input(selected_options, custom_text, existing_values_str):
    combined = []

    # Start with selected options from the multiselect
    if selected_options:
        combined.extend(selected_options)

    # Add custom text entries
    if custom_text:
        new_entries = [item.strip() for item in custom_text.split(',') if item.strip()]
        for entry in new_entries:
            if entry not in combined:
                combined.append(entry)

    # Add any existing entries from the contact's data that weren't in selected_options or custom_text
    # This handles cases where a value was in the data but not in the standard list or custom input
    if pd.notna(existing_values_str) and isinstance(existing_values_str, str):
        existing_list = [item.strip() for item in existing_values_str.split(',') if item.strip()]
        for entry in existing_list:
            if entry not in combined:
                combined.append(entry)

    # Sort and return as a comma-separated string for consistency with existing data
    combined.sort()
    return ", ".join(combined)

# --- Helper function to calculate age ---
def calculate_age(dob, known_age_current_year):
    today = date.today()
    if pd.notna(dob) and isinstance(dob, (date, datetime)):
        # Calculate precise age from Date of Birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    elif pd.notna(known_age_current_year) and isinstance(known_age_current_year, (int, float)):
        # Calculate approximate age from Known Age (Current Year)
        return int(known_age_current_year)
    return None # Return None if no valid birth info

# --- NEW: Helper function to get the numerical rank of a designation ---
def get_designation_protocol_rank(designation_str):
    if not isinstance(designation_str, str):
        return DEFAULT_DESIGNATION_RANK # Return default for non-string or NaN

    designation_lower = designation_str.lower()
    for keyword, rank in DESIGNATION_PROTOCOL_RANKS.items():
        if keyword in designation_lower:
            return rank
    return DEFAULT_DESIGNATION_RANK # If no keyword matches


# --- 2. Contact Card Display and Editing ---
def edit_contact_form(contact, index):
    st.markdown("<h4>Edit Contact</h4>", unsafe_allow_html=True)

    # Pre-calculate counts of other contacts in the same company
    other_contacts_in_company = st.session_state.contacts_df[
        (st.session_state.contacts_df["Company"] == contact["Company"]) &
        (st.session_state.contacts_df.index != index)
    ]

    with st.form(key=f"edit_form_{index}"):
        name = st.text_input("Name*", value=contact["Name"], key=f"edit_name_{index}")

        # New fields for Date of Birth / Known Age (Current Year) - MOVED UP
        col_dob, col_known_age = st.columns(2)
        with col_dob:
            current_dob_value = contact.get("Date of Birth")
            if isinstance(current_dob_value, (date, datetime)): # Check for date or datetime objects
                dob_value = current_dob_value
            elif pd.notna(current_dob_value): # If not null but not a date/datetime, try parsing
                try:
                    dob_value = pd.to_datetime(current_dob_value).date()
                except ValueError: # If parsing fails, set to None
                    dob_value = None
            else: # If NaN or None, set to None
                dob_value = None

            date_of_birth = st.date_input(
                "Date of Birth (Optional)",
                value=dob_value,
                key=f"edit_dob_{index}",
                min_value=date(1900,1,1), # Prevent overly old dates
                max_value=date.today() # Prevent future dates
            )
            # If user selects the default minimum date, treat it as unset for DOB
            final_date_of_birth = date_of_birth if pd.notna(date_of_birth) and date_of_birth != date(1900,1,1) else None


        with col_known_age:
            current_known_age_value = contact.get("Known Age (Current Year)")
            # Convert to int then str for display if it's a number, else empty string
            known_age_str = str(int(current_known_age_value)) if pd.notna(current_known_age_value) else ""
            known_age_input = st.text_input(
                f"Age (as of {date.today().year}, Optional)", # Display current year in label
                value=known_age_str,
                key=f"edit_known_age_{index}",
                help="Enter the contact's current age if their exact Date of Birth is unknown. This will auto-update yearly."
            )
            known_age_current_year = None
            if known_age_input.strip():
                try:
                    known_age_current_year = int(known_age_input.strip())
                    if not (0 <= known_age_current_year <= 120): # Reasonable age range
                        st.error("Age must be between 0 and 120.")
                        known_age_current_year = None # Invalidate if outside range
                except ValueError:
                    st.error("Invalid Age. Please enter a whole number.")

            final_known_age_current_year = known_age_current_year


        designation = st.text_input("Designation*", value=contact["Designation"], key=f"edit_designation_{index}")

        # Country Dropdown
        current_country_index = STANDARD_COUNTRIES.index(contact["Country"]) if contact["Country"] in STANDARD_COUNTRIES else 0
        country = st.selectbox("Country*", options=STANDARD_COUNTRIES, index=current_country_index, key=f"edit_country_{index}")

        company = st.text_input("Company*", value=contact["Company"], key=f"edit_company_{index}")
        phone_number = st.text_input("Phone Number", value=contact["Phone Number"], key=f"edit_phone_number_{index}")
        office_number = st.text_input("Office Number", value=contact["Office Number"], key=f"edit_office_number_{index}")

        # Access 'Email Address' safely using .get() for robustness during initial runs
        email_address_value = contact.get("Email Address", "") # Default to empty string if missing
        email_address = st.text_input("Email Address", value=email_address_value, key=f"edit_email_{index}")

        # === START BULK UPDATE FIELD SECTION ===
        bulk_apply_states = {} # Dictionary to store checkbox states for bulk updates

        # MODIFIED add_bulk_checkboxes function to combine question and checkbox, always display names
        def add_bulk_checkboxes(field_name, field_label_for_display):
            if not other_contacts_in_company.empty:
                bulk_apply_states[f"{field_name}_company"] = st.checkbox(
                    f"Apply this **{field_label_for_display}** to {len(other_contacts_in_company)} other(s) in {contact['Company']}?",
                    key=f"apply_{field_name}_company_{index}",
                    help=f"Tick this to update this {field_label_for_display} for all listed contacts in {contact['Company']}."
                )
                st.markdown("###### Affected Contacts:")
                for i, other_contact in enumerate(other_contacts_in_company.iterrows()):
                    st.write(f"{i+1}. {other_contact[1]['Name']} ({other_contact[1]['Designation']})")
            else:
                st.info(f"No other contacts in {contact['Company']} to apply {field_label_for_display} to.")


        initial_posting_date = contact["Posting Date"]
        formatted_posting_date_value = None
        if isinstance(initial_posting_date, (datetime, date)):
            formatted_posting_date_value = initial_posting_date
        elif pd.notnull(initial_posting_date) and initial_posting_date != 'N/A':
            try:
                dt_obj = pd.to_datetime(initial_posting_date)
                formatted_posting_date_value = dt_obj.date()
            except ValueError:
                formatted_posting_date_value = None
            except TypeError: # Handle cases where it might be a list or other unexpected type
                formatted_posting_date_value = None
        else:
            formatted_posting_date_value = None

        posting_date = st.date_input("Posting Date", value=formatted_posting_date_value, key=f"edit_posting_date_{index}")
        # Not in BULK_UPDATE_FIELDS: add_bulk_checkboxes("Posting Date", "Posting Date")


        initial_deposted_date = contact["Deposted Date"]
        formatted_deposted_date_value = None
        if isinstance(initial_deposted_date, (datetime, date)):
            formatted_deposted_date_value = initial_deposted_date
        elif pd.notnull(initial_deposted_date) and initial_deposted_date != 'N/A':
            try:
                dt_obj = pd.to_datetime(initial_deposted_date)
                formatted_deposted_date_value = dt_obj.date()
            except ValueError:
                formatted_deposted_date_value = None
            except TypeError:
                formatted_deposted_date_value = None
        else:
            formatted_deposted_date_value = None

        deposted_date = st.date_input("Deposted Date", value=formatted_deposted_date_value, key=f"edit_deposted_date_{index}")
        # Not in BULK_UPDATE_FIELDS: add_bulk_checkboxes("Deposted Date", "De-posted Date")


        office_address = st.text_area("Office Address", value=contact["Office Address"], key=f"edit_office_address_{index}")
        add_bulk_checkboxes("Office Address", "Office Address")

        home_address = st.text_area("Home Address", value=contact["Home Address"], key=f"edit_home_address_{index}")
        # Not in BULK_UPDATE_FIELDS: add_bulk_checkboxes("Home Address", "Home Address")

        hobbies = st.text_input("Hobbies", value=contact["Hobbies"], key=f"edit_hobbies_{index}")
        # Not in BULK_UPDATE_FIELDS: add_bulk_checkboxes("Hobbies", "Hobbies")

        dietary_restrictions = st.text_input("Dietary Restrictions", value=contact["Dietary Restrictions"], key=f"edit_dietary_restrictions_{index}")
        # Not in BULK_UPDATE_FIELDS: add_bulk_checkboxes("Dietary Restrictions", "Dietary Restrictions")

        # Festivities Multiselect + Text Area - UPDATED
        current_festivities_list = [f.strip() for f in str(contact["Festivities"]).split(',') if f.strip()] if pd.notna(contact["Festivities"]) else []

        # Determine default selected options for multiselect: only those in COMMON_FESTIVITIES
        default_selected_festivities = [f for f in current_festivities_list if f in COMMON_FESTIVITIES]

        # Determine custom text part: anything NOT in COMMON_FESTIVITIES
        custom_festivities_text = ", ".join([f for f in current_festivities_list if f not in COMMON_FESTIVITIES])

        selected_festivities = st.multiselect(
            "Festivities (select all that apply)",
            options=COMMON_FESTIVITIES,
            default=default_selected_festivities,
            key=f"edit_festivities_select_{index}"
        )
        custom_festivities_input = st.text_area(
            "Or enter custom festivities (comma-separated):",
            value=custom_festivities_text,
            key=f"edit_festivities_custom_{index}"
        )
        # Use the updated process_multi_text_input
        festivities_combined = process_multi_text_input(selected_festivities, custom_festivities_input, contact["Festivities"])
        add_bulk_checkboxes("Festivities", "Festivities") # Bulk checkbox for Festivities

        vehicle = st.text_input("Vehicle", value=contact["Vehicle"], key=f"edit_vehicle_{index}")
        add_bulk_checkboxes("Vehicle", "Vehicle")

        # Golf selection field - Always visible
        golf = st.selectbox("Golf",["Yes", "No"], index=0 if contact["Golf"] == "Yes" else 1, key=f"edit_golf_{index}")
        # Not in BULK_UPDATE_FIELDS: add_bulk_checkboxes("Golf", "Golf")

        # Golf Handicap - Always visible
        handicap = st.text_input("Golf Handicap", value=contact["Golf Handicap"], key=f"edit_golf_handicap_{index}")
        # Not in BULK_UPDATE_FIELDS: add_bulk_checkboxes("Golf Handicap", "Golf Handicap")

        # Reception Multiselect + Text Area - UPDATED
        current_reception_list = [r.strip() for r in str(contact["Reception"]).split(',') if r.strip()] if pd.notna(contact["Reception"]) else []

        # We'll use a dynamic list for the multiselect options for Reception.
        # This will include standard options and any unique options already in the data.
        all_reception_options_for_multiselect = sorted(list(set(RECEPTION_OPTIONS_MASTER + current_reception_list))) # Use the MASTER list

        # Determine default selected options for multiselect
        default_selected_reception = [r for r in current_reception_list if r in RECEPTION_OPTIONS_MASTER]

        # Determine custom text part
        custom_reception_text = ", ".join([r for r in current_reception_list if r not in RECEPTION_OPTIONS_MASTER])


        selected_reception = st.multiselect(
            "Reception (select all that apply)",
            options=RECEPTION_OPTIONS_MASTER, # Provide the fixed, master list
            default=default_selected_reception,
            key=f"edit_reception_select_{index}"
        )
        custom_reception_input = st.text_area(
            "Or enter custom reception types (comma-separated):",
            value=custom_reception_text,
            key=f"edit_reception_custom_{index}"
        )
        # Use the updated process_multi_text_input
        reception_combined = process_multi_text_input(selected_reception, custom_reception_input, contact["Reception"])
        add_bulk_checkboxes("Reception", "Reception") # Bulk checkbox for Reception

        # Marital Status Dropdown (New Field) - NOT IN BULK_UPDATE_FIELDS, so no checkboxes
        marital_status_value = contact.get("Marital Status", MARITAL_STATUS_OPTIONS[0]) # Default to first option
        current_marital_status_index = MARITAL_STATUS_OPTIONS.index(marital_status_value) if marital_status_value in MARITAL_STATUS_OPTIONS else 0
        marital_status = st.selectbox(
            "Marital Status",
            options=MARITAL_STATUS_OPTIONS,
            index=current_marital_status_index,
            key=f"edit_marital_status_{index}"
        )

        # Children Quantity (UPDATED TO SELECTBOX) - NOT IN BULK_UPDATE_FIELDS
        col_son, col_daughter = st.columns(2)
        with col_son:
            current_sons_value = contact.get("Children (Son)")
            if pd.isna(current_sons_value) or current_sons_value is None:
                default_sons_index = CHILDREN_OPTIONS.index("Unknown")
            elif int(current_sons_value) == 0:
                default_sons_index = CHILDREN_OPTIONS.index(0)
            elif int(current_sons_value) in CHILDREN_OPTIONS:
                default_sons_index = CHILDREN_OPTIONS.index(int(current_sons_value))
            else:
                default_sons_index = CHILDREN_OPTIONS.index("Unknown")

            children_son_input = st.selectbox(
                "Children (Sons)",
                options=CHILDREN_OPTIONS,
                index=default_sons_index,
                key=f"edit_children_son_{index}"
            )
            children_son = None if children_son_input == "Unknown" else children_son_input

        with col_daughter:
            current_daughters_value = contact.get("Children (Daughter)")
            if pd.isna(current_daughters_value) or current_daughters_value is None:
                default_daughters_index = CHILDREN_OPTIONS.index("Unknown")
            elif int(current_daughters_value) == 0:
                default_daughters_index = CHILDREN_OPTIONS.index(0)
            elif int(current_daughters_value) in CHILDREN_OPTIONS:
                default_daughters_index = CHILDREN_OPTIONS.index(int(current_daughters_value))
            else:
                default_daughters_index = CHILDREN_OPTIONS.index("Unknown")

            children_daughter_input = st.selectbox(
                "Children (Daughters)",
                options=CHILDREN_OPTIONS,
                index=default_daughters_index,
                key=f"edit_children_daughter_{index}"
            )
            children_daughter = None if children_daughter_input == "Unknown" else children_daughter_input

        status = st.selectbox("Status", ["Active", "Inactive"], index=["Active", "Inactive"].index(contact["Status"]), key=f"edit_status_{index}")
        # Not in BULK_UPDATE_FIELDS: add_bulk_checkboxes("Status", "Status")

        tiering = st.selectbox("Tiering", options=TIERING_OPTIONS, index=TIERING_OPTIONS.index(contact["Tiering"]) if contact["Tiering"] in TIERING_OPTIONS else TIERING_OPTIONS.index("Untiered"), key=f"edit_tiering_{index}")
        add_bulk_checkboxes("Tiering", "Tiering")

        # UPDATED: Sort category options in the selectbox
        category_options_sorted = sorted(valid_categories)
        current_category_index = category_options_sorted.index(contact["Category"]) if contact["Category"] in category_options_sorted else category_options_sorted.index("Others")
        category = st.selectbox("Category", options=category_options_sorted, index=current_category_index, key=f"edit_category_{index}")
        # Not in BULK_UPDATE_FIELDS: add_bulk_checkboxes("Category", "Category")

        # === END BULK UPDATE FIELD SECTION ===

        # Comments (display only in edit form, actual adding done in view)
        st.markdown("---")
        st.markdown("#### Comments")
        if contact["Comments"]:
            for i, comment_entry in enumerate(contact["Comments"]):
                st.markdown(f"- {comment_entry}")
        else:
            st.write("No comments yet.")
        # No direct edit for comments here, they are added via the "Add Comment" button in view mode

        uploaded_file_photo = st.file_uploader("Upload new profile picture", type=["png", "jpg", "jpeg"], key=f"edit_pic_{index}")

        col_update, col_cancel = st.columns(2)
        with col_update:
            submitted = st.form_submit_button("Update Contact")
        with col_cancel:
            if st.form_submit_button("Cancel"):
                st.session_state.editing_contact_index = None
                st.rerun()

        if submitted:
            if name and designation and country and company:
                updated_contact = contact.copy() # Make a copy to hold potential changes

                changes_for_primary_contact = [] # Track changes for the currently edited contact
                bulk_updates_to_apply = [] # Store bulk update instructions

                # Helper to track changes for the primary contact and prepare bulk updates
                def track_and_prepare_change(field_name, field_label, old_val, new_val):
                    # Convert to comparable types for consistency (handle None/pd.NA)
                    old_val_to_compare = old_val if pd.notna(old_val) else None
                    new_val_to_compare = new_val if pd.notna(new_val) else None

                    # Special handling for display in history, particularly for "Unknown" vs None
                    old_val_str = str(old_val_to_compare) if old_val_to_compare is not None else "N/A"
                    new_val_str = str(new_val_to_compare) if new_val_to_compare is not None else "N/A"

                    if field_name.startswith("Children"):
                        old_val_str = "Unknown" if old_val_to_compare is None else str(int(old_val_to_compare))
                        new_val_str = "Unknown" if new_val_to_compare is None else str(int(new_val_to_compare))
                    elif field_name == "Date of Birth":
                        old_val_str = old_val_to_compare.strftime("%Y-%m-%d") if isinstance(old_val_to_compare, (date, datetime)) else "Unknown"
                        new_val_str = new_val_to_compare.strftime("%Y-%m-%d") if isinstance(new_val_to_compare, (date, datetime)) else "Unknown"
                    elif field_name == "Known Age (Current Year)":
                        old_val_str = str(int(old_val_to_compare)) if pd.notna(old_val_to_compare) else "N/A"
                        new_val_str = str(int(new_val_to_compare)) if pd.notna(new_val_to_compare) else "N/A"
                    elif field_name == "Comments": # Comments are handled separately, not changed here
                        pass
                    # For list-like fields (Festivities, Reception), compare string representation
                    elif field_name in ["Festivities", "Reception"]:
                        # Ensure comparison is done on processed string values
                        old_val_str = str(old_val_to_compare)
                        new_val_str = str(new_val_to_compare)
                    else:
                        # For other fields, direct comparison for change
                        old_val_str = str(old_val_to_compare) if old_val_to_compare is not None else "N/A"
                        new_val_str = str(new_val_to_compare) if new_val_to_compare is not None else "N/A"


                    if old_val_str != new_val_str: # Check if values are different for history/bulk
                        changes_for_primary_contact.append(f"{field_label} changed from '{old_val_str}' to '{new_val_str}'")

                        # If this field is eligible for bulk update and a checkbox was ticked
                        if field_name in BULK_UPDATE_FIELDS:
                            if bulk_apply_states.get(f"{field_name}_company"):
                                bulk_updates_to_apply.append({"field": field_name, "value": new_val, "scope": "company"})
                    return new_val


                # --- Apply changes to the PRIMARY contact being edited ---
                updated_contact["Name"] = track_and_prepare_change("Name", "Name", contact["Name"], name)
                updated_contact["Date of Birth"] = track_and_prepare_change("Date of Birth", "Date of Birth", contact.get("Date of Birth", None), final_date_of_birth)
                updated_contact["Known Age (Current Year)"] = track_and_prepare_change("Known Age (Current Year)", "Known Age (Current Year)", contact.get("Known Age (Current Year)", None), final_known_age_current_year)
                updated_contact["Designation"] = track_and_prepare_change("Designation", "Designation", contact["Designation"], designation)
                updated_contact["Country"] = track_and_prepare_change("Country", "Country", contact["Country"], country)
                updated_contact["Company"] = track_and_prepare_change("Company", "Company", contact["Company"], company)
                updated_contact["Phone Number"] = track_and_prepare_change("Phone Number", "Phone Number", contact["Phone Number"], phone_number)
                updated_contact["Office Number"] = track_and_prepare_change("Office Number", "Office Number", contact["Office Number"], office_number)
                updated_contact["Email Address"] = track_and_prepare_change("Email Address", "Email Address", contact.get("Email Address", None), email_address)
                updated_contact["Posting Date"] = track_and_prepare_change("Posting Date", "Posting Date", contact["Posting Date"], posting_date)
                updated_contact["Deposted Date"] = track_and_prepare_change("Deposted Date", "De-posted Date", contact["Deposted Date"], deposted_date)
                updated_contact["Office Address"] = track_and_prepare_change("Office Address", "Office Address", contact["Office Address"], office_address)
                updated_contact["Home Address"] = track_and_prepare_change("Home Address", "Home Address", contact["Home Address"], home_address)
                updated_contact["Hobbies"] = track_and_prepare_change("Hobbies", "Hobbies", contact["Hobbies"], hobbies)
                updated_contact["Dietary Restrictions"] = track_and_prepare_change("Dietary Restrictions", "Dietary Restrictions", contact["Dietary Restrictions"], dietary_restrictions)
                updated_contact["Festivities"] = track_and_prepare_change("Festivities", "Festivities", contact["Festivities"], festivities_combined)
                updated_contact["Vehicle"] = track_and_prepare_change("Vehicle", "Vehicle", contact["Vehicle"], vehicle)
                updated_contact["Golf"] = track_and_prepare_change("Golf", "Golf", contact["Golf"], golf)
                updated_contact["Golf Handicap"] = track_and_prepare_change("Golf Handicap", "Golf Handicap", contact["Golf Handicap"], handicap)
                updated_contact["Reception"] = track_and_prepare_change("Reception", "Reception", contact["Reception"], reception_combined)
                updated_contact["Marital Status"] = track_and_prepare_change("Marital Status", "Marital Status", contact.get("Marital Status", None), marital_status)
                updated_contact["Children (Son)"] = track_and_prepare_change("Children (Son)", "Children (Sons)", contact.get("Children (Son)", None), children_son)
                updated_contact["Children (Daughter)"] = track_and_prepare_change("Children (Daughter)", "Children (Daughters)", contact.get("Children (Daughter)", None), children_daughter)
                updated_contact["Status"] = track_and_prepare_change("Status", "Status", contact["Status"], status)
                updated_contact["Tiering"] = track_and_prepare_change("Tiering", "Tiering", contact["Tiering"], tiering)
                updated_contact["Category"] = track_and_prepare_change("Category", "Category", contact["Category"], category)


                # Handle photo upload
                new_pic_bytes = None
                if uploaded_file_photo is not None:
                    new_pic_bytes = uploaded_file_photo.read()
                    if contact["Photo"] is None:
                        changes_for_primary_contact.append("Profile picture added")
                    elif new_pic_bytes != contact["Photo"]:
                        changes_for_primary_contact.append("Profile picture updated")
                    updated_contact["Photo"] = new_pic_bytes

                # --- Update Primary Contact's History and Data ---
                if changes_for_primary_contact:
                    update_info = (f"Updated by {st.session_state.user_role} at {get_gmt8_now().strftime('%d %b %y, %I:%M %p')}.<br>"
                                   + "<br>".join(changes_for_primary_contact))
                    updated_contact["Last Updated By"] = st.session_state.user_role
                    updated_contact["Last Updated On"] = get_gmt8_now().strftime("%d %b %y, %I:%M %p")
                    updated_contact["History"].append(update_info)

                st.session_state.contacts_df.loc[index] = updated_contact # Apply changes to primary contact


                # --- Apply BULK UPDATES ---
                for bulk_update_item in bulk_updates_to_apply:
                    field_name = bulk_update_item["field"]
                    new_value = bulk_update_item["value"]
                    scope = bulk_update_item["scope"] # This will always be "company" now

                    target_indices = pd.Index([]) # Initialize as empty index
                    if scope == "company":
                        target_indices = other_contacts_in_company.index
                        scope_label = f"same company ({contact['Company']})"
                    else:
                        continue # Should not happen, but good for robustness

                    if not target_indices.empty:
                        for target_idx in target_indices:
                            target_contact_row = st.session_state.contacts_df.loc[target_idx]
                            old_value = target_contact_row[field_name]

                            # Format old_value for history consistently
                            old_value_for_history = str(old_value) if pd.notna(old_value) else "N/A"
                            if field_name == "Date of Birth":
                                old_value_for_history = old_value.strftime("%Y-%m-%d") if isinstance(old_value, (date, datetime)) else "Unknown"
                            elif field_name == "Known Age (Current Year)":
                                old_value_for_history = str(int(old_value)) if pd.notna(old_value) else "N/A"


                            if old_value != new_value: # Only update if value is different
                                st.session_state.contacts_df.loc[target_idx, field_name] = new_value

                                # Add history entry for the bulk updated contact
                                update_info_bulk = (
                                    f"Bulk updated by {st.session_state.user_role} (from {contact['Name']}'s edit) "
                                    f"at {get_gmt8_now().strftime('%d %b %y, %I:%M %p')}: "
                                    f"'{field_name}' changed from '{old_value_for_history}' to '{new_value}' "
                                    f"for {scope_label}."
                                )
                                st.session_state.contacts_df.loc[target_idx, "Last Updated By"] = st.session_state.user_role
                                st.session_state.contacts_df.loc[target_idx, "Last Updated On"] = get_gmt8_now().strftime("%d %b %y, %I:%M %p")
                                # Ensure History column is a list, append if it is
                                if isinstance(st.session_state.contacts_df.loc[target_idx, "History"], list):
                                    st.session_state.contacts_df.loc[target_idx, "History"].append(update_info_bulk)
                                else: # If for some reason it's not a list, initialize and append
                                    st.session_state.contacts_df.loc[target_idx, "History"] = [update_info_bulk]

                st.success("Contact(s) updated successfully!")
                st.session_state.editing_contact_index = None
                st.rerun()
            else:
                st.error("Please fill in all required fields (Name, Designation, Country, Company).")

def get_tier_color(Tiering):
    tier_colors = {
        "A+": "darkgreen",
        "A": "blue",
        "B": "purple",
        "C": "orange",
        "Untiered": "gray"
    }
    return tier_colors.get(Tiering, "gray") # Default to gray if tiering is not recognized

def get_status_color(status):
     return "green" if status == "Active" else "red"

def display_contact_card(contact, index):
    # If this contact is currently being edited, display the full edit form directly.
    # This form is intentionally outside the container for clarity during editing.
    if st.session_state.editing_contact_index == index:
        edit_contact_form(contact, index)
    else:
        # Wrap the entire contact card display and action buttons within a single st.container()
        with st.container(border=True):

            # --- Contact Card HTML Display (unchanged from original) ---
            posting_date_display = contact['Posting Date']
            formatted_posting_date = ""
            if pd.notnull(posting_date_display) and posting_date_display != 'N/A':
                if isinstance(posting_date_display, str):
                    try:
                        dt_obj = pd.to_datetime(posting_date_display)
                        formatted_posting_date = dt_obj.strftime('%d %b %y')
                    except ValueError:
                        formatted_posting_date = "Invalid Date"
                elif isinstance(posting_date_display, (datetime, date)):
                    formatted_posting_date = posting_date_display.strftime('%d %b %y')
            else:
                formatted_posting_date = "N/A"


            deposted_date_display = contact['Deposted Date']
            formatted_deposted_date = ""
            if pd.notnull(deposted_date_display) and deposted_date_display != 'N/A':
                if isinstance(deposted_date_display, str):
                    try:
                        dt_obj = pd.to_datetime(deposted_date_display)
                        formatted_deposted_date = dt_obj.strftime('%d %b %y')
                    except ValueError:
                        formatted_deposted_date = "Invalid Date"
                elif isinstance(deposted_date_display, (datetime, date)):
                    formatted_deposted_date = deposted_date_display.strftime('%d %b %y')
            else:
                formatted_deposted_date = "N/A"

            # Format Date of Birth for display - UPDATED TO SHOW "UNKNOWN"
            dob_display = contact.get("Date of Birth")
            formatted_dob = "Unknown" # Default to "Unknown"
            if pd.notnull(dob_display) and dob_display != 'N/A': # Still check N/A for legacy data
                if isinstance(dob_display, str):
                    try:
                        dt_obj = pd.to_datetime(dob_display)
                        formatted_dob = dt_obj.strftime('%d %b %y')
                    except ValueError:
                        pass # Keep "Unknown" if parsing fails
                elif isinstance(dob_display, (datetime, date)):
                    formatted_dob = dob_display.strftime('%d %b %y')


            image_bytes = contact['Photo']
            if image_bytes is not None and isinstance(image_bytes, bytes):
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            else:
                try:
                    # Use a default placeholder image if "placeholder.jpg" is present in the assets folder
                    # Otherwise, use a tiny transparent base64 image
                    with open(Path(__file__).parent / "placeholder.jpg", "rb") as f: # Adjusted path for robustness
                        placeholder_bytes = f.read()
                        image_base64 = base64.b64encode(placeholder_bytes).decode("utf-8")
                except FileNotFoundError:
                    image_base64 = "iVBORw0KGgoAAAANgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="


            # Determine children display string (UPDATED LOGIC)
            num_sons_raw = contact.get('Children (Son)')
            num_daughters_raw = contact.get('Children (Daughter)')

            children_parts = []

            # Process sons
            # Only add to parts if the number is greater than 0
            if pd.notnull(num_sons_raw) and num_sons_raw is not None and int(num_sons_raw) > 0:
                num_sons = int(num_sons_raw)
                children_parts.append(f"{num_sons} Son{'s' if num_sons > 1 else ''}")

            # Process daughters
            # Only add to parts if the number is greater than 0
            if pd.notnull(num_daughters_raw) and num_daughters_raw is not None and int(num_daughters_raw) > 0:
                num_daughters = int(num_daughters_raw)
                children_parts.append(f"{num_daughters} Daughter{'s' if num_daughters > 1 else ''}")

            # Determine final display string
            # If both are None/NaN, display "Unknown"
            if (pd.isnull(num_sons_raw) or num_sons_raw is None) and \
               (pd.isnull(num_daughters_raw) or num_daughters_raw is None):
                children_display = "Unknown"
            # If no children parts (meaning both are 0 or one is 0 and other is unknown/None)
            elif not children_parts:
                children_display = "None"
            else:
                children_display = ", ".join(children_parts)

            # Calculate age for display
            age = calculate_age(contact.get("Date of Birth"), contact.get("Known Age (Current Year)"))
            # Age display format
            age_display = f"(Age {age} years)" if age is not None else "(Age unknown)"


            # Define the gradient background for the card
            # Going from white to silver
            card_background_gradient = "linear-gradient(to right, #ffffff, #d0d0d0)"
            # The border color should still match one of the gradient colors
            card_border_color = "#e0e0e0" # A very light gray/silver for the border

            st.markdown(
                f"""
                <div style="
                    border-radius: 10px;
                    border: 1px solid {card_border_color};
                    padding: 15px;
                    background: {card_background_gradient};
                    box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2);
                ">
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <img src="data:image/png;base64,{image_base64}" style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover;">
                        <div style="flex: 1;">
                            <h3 style="margin: 0; font-size: 20px; color: #000000;">
                                {contact['Name']} {age_display}
                            </h3>
                            <i><h4 style="margin: 0; font-size: 16px; color: #000000;">
                                {contact['Designation']} , {contact['Company']}
                            </h4></i>
                        </div>
                        <div style="background-color: {get_tier_color(contact['Tiering'])}; color: white; padding: 5px 10px; border-radius: 5px; text-align: center;">
                            <b>Tier:</b> {contact['Tiering']}
                        </div>
                        <div style="background-color: {get_status_color(contact['Status'])}; color: white; padding: 5px 10px; border-radius: 5px; text-align: center;">
                            {contact['Status']}
                        </div>
                        <div style="background-color: #6a0dad; color: white; padding: 5px 10px; border-radius: 5px; text-align: center;">
                            {contact['Category']}
                        </div>
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 15px;">
                        <div style="flex: 1; min-width: 200px; color: #000000">
                            <p><b>Date of Birth:</b> {formatted_dob}</p>
                            <p><b>Country:</b> {contact['Country']}</p>
                            <p><b>Phone Number:</b> {contact['Phone Number']}</p>
                            <p><b>Office Number:</b> {contact['Office Number']}</p>
                            <p><b>Email Address:</b> {contact.get('Email Address', 'N/A')}</p>
                            <p><b>Address:</b> {contact['Office Address']}</p>
                            <p><b>Home Address:</b> {contact['Home Address']}</p>
                        </div>
                        <div style="flex: 1; min-width: 200px; color: #000000">
                            <p><b>Posting Date:</b> {formatted_posting_date}</p>
                            <p><b>De-posted Date:</b> {formatted_deposted_date}</p>
                            <p><b>Marital Status:</b> {contact.get('Marital Status', 'N/A')}</p>
                            <p><b>Children:</b> {children_display}</p>
                            <p><b>Vehicle(s):</b> {contact['Vehicle']}</p>
                            <p><b>Golf:</b> {contact['Golf']}</p>
                            <p><b>Golf Handicap:</b> {contact['Golf Handicap']}</p>
                        </div>
                        <div style="flex: 1; min-width: 200px; color: #000000">
                            <p><b>Hobbies:</b> {contact['Hobbies']}</p>
                            <p><b>Dietary Restrictions:</b> {contact['Dietary Restrictions']}</p>
                            <p><b>Reception:</b> {contact['Reception']}</p>
                            <p><b>Festivity:</b> {contact['Festivities']}</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Add a small vertical space here
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

            # --- Last Updated Info (unchanged from original) ---
            if contact["Last Updated On"]:
                    st.info(f"Last updated by {contact['Last Updated By']} at {contact['Last Updated On']}")

            # --- New Comment and History Sections (side-by-side) ---
            col_comment, col_history = st.columns(2)

            with col_comment:
                with st.expander("Add/View Comments"):
                    comment_input = st.text_area("Add a new comment", key=f"comment_input_{index}")
                    if st.button("Add Comment", key=f"add_comment_button_{index}"):
                        if comment_input.strip():
                            new_comment_entry = (
                                f"**{st.session_state.user_role.capitalize()}** "
                                f"on {get_gmt8_now().strftime('%d %b %y, %I:%M %p')}: "
                                f"{comment_input.strip()}"
                            )
                            # Ensure comments field is a list
                            if not isinstance(contact["Comments"], list):
                                contact["Comments"] = []
                            contact["Comments"].append(new_comment_entry)

                            # Update last updated info and history for comments as well
                            update_info = (f"Updated by {st.session_state.user_role} at {get_gmt8_now().strftime('%d %b %y, %I:%M %p')}. "
                                           f"New comment added: '{comment_input.strip()}'")
                            contact["Last Updated By"] = st.session_state.user_role
                            contact["Last Updated On"] = get_gmt8_now().strftime("%d %b %y, %I:%M %p")
                            contact["History"].append(update_info)

                            st.session_state.contacts_df.loc[index] = contact
                            st.success("Comment added!")
                            st.rerun() # Rerun to clear the text area and show new comment
                        else:
                            st.warning("Please enter a comment to add.")

                    if contact["Comments"]:
                        st.markdown("---")
                        st.markdown("##### Existing Comments:")
                        for i, comment_entry in enumerate(contact["Comments"]):
                            st.markdown(f"- {comment_entry}")
                    else:
                        st.write("No comments yet for this contact.")

            with col_history:
                with st.expander("**View Change History**"): # Changed label here
                    if contact["History"]:
                        for i, history_entry in enumerate(contact["History"]):
                            st.markdown(f"**{i+1}.** {history_entry}", unsafe_allow_html=True)
                    else:
                        st.write("No history available.")

            # --- Edit Button (admin only) ---
            if st.session_state.user_role == "admin":
                if st.button(f"Edit {contact['Name']}'s Info", key=f"edit_button_{index}"):
                    st.session_state.editing_contact_index = index
                    st.rerun()

# --- Add New Contact ➕ ---
def add_new_contact_form():
    st.sidebar.title("Add New Contact")

    with st.form(key="add_contact_form"):
        name = st.text_input("Name*")

        # New fields for Date of Birth / Known Age (Current Year) - MOVED UP
        col_add_dob, col_add_known_age = st.columns(2)
        with col_add_dob:
            date_of_birth_add = st.date_input(
                "Date of Birth (Optional)",
                value=None, # Default to None for new contacts
                key="add_dob",
                min_value=date(1900,1,1),
                max_value=date.today()
            )
            # If user selects the default minimum date, treat it as unset for DOB
            final_date_of_birth_add = date_of_birth_add if pd.notna(date_of_birth_add) and date_of_birth_add != date(1900,1,1) else None

        with col_add_known_age:
            known_age_input_add = st.text_input(
                f"Age (as of {date.today().year}, Optional)", # Display current year in label
                value="",
                key="add_known_age",
                help="Enter the contact's current age if their exact Date of Birth is unknown. This will auto-update yearly."
            )
            known_age_current_year_add = None
            if known_age_input_add.strip():
                try:
                    known_age_current_year_add = int(known_age_input_add.strip())
                    if not (0 <= known_age_current_year_add <= 120): # Reasonable age range
                        st.error("Age must be between 0 and 120.")
                        known_age_current_year_add = None
                except ValueError:
                    st.error("Invalid Age. Please enter a whole number.")

            final_known_age_current_year_add = known_age_current_year_add


        designation = st.text_input("Designation*")

        # Country Dropdown
        country = st.selectbox("Country*", options=STANDARD_COUNTRIES, index=0)

        company = st.text_input("Company*")
        phone_number = st.text_input("Phone Number")
        office_number = st.text_input("Office Number")
        email_address = st.text_input("Email Address")
        posting_date = st.date_input("Posting Date", value=datetime.today().date())
        deposted_date = st.date_input("De-posted Date", value=None)
        office_address = st.text_area("Office Address")
        home_address = st.text_area("Home Address")
        hobbies = st.text_input("Hobbies")
        dietary_restrictions = st.text_input("Dietary Restrictions")

        # Festivities Multiselect + Text Area
        selected_festivities = st.multiselect(
            "Festivities (select all that apply)",
            options=COMMON_FESTIVITIES,
            default=[]
        )
        custom_festivities_input = st.text_area(
            "Or enter custom festivities (comma-separated):",
            value=""
        )
        festivities_combined = process_multi_text_input(selected_festivities, custom_festivities_input, "") # Pass empty string for new contact


        # Reception Multiselect + Text Area
        selected_reception = st.multiselect(
            "Reception (select all that apply)",
            options=RECEPTION_OPTIONS_MASTER,
            default=[]
        )
        custom_reception_input = st.text_area(
            "Or enter custom reception types (comma-separated):",
            value=""
        )
        reception_combined = process_multi_text_input(selected_reception, custom_reception_input, "") # Pass empty string for new contact


        vehicle = st.text_input("Vehicle")

        # Golf selection field - Always visible
        golf = st.selectbox("Golf", ["Yes", "No"], index=1) # Default to No

        # Golf Handicap - Always visible
        golf_handicap = st.text_input("Golf Handicap")

        # Marital Status Dropdown
        marital_status = st.selectbox(
            "Marital Status",
            options=MARITAL_STATUS_OPTIONS,
            index=0 # Default to "Single" or the first option
        )

        # Children Quantity (UPDATED TO SELECTBOX)
        col_son_add, col_daughter_add = st.columns(2)
        with col_son_add:
            children_son_input = st.selectbox(
                "Children (Sons)",
                options=CHILDREN_OPTIONS,
                index=CHILDREN_OPTIONS.index("Unknown") # Default to 'Unknown'
            )
            children_son = None if children_son_input == "Unknown" else children_son_input
        with col_daughter_add:
            children_daughter_input = st.selectbox(
                "Children (Daughters)",
                options=CHILDREN_OPTIONS,
                index=CHILDREN_OPTIONS.index("Unknown") # Default to 'Unknown'
            )
            children_daughter = None if children_daughter_input == "Unknown" else children_daughter_input

        status = st.selectbox("Status", ["Active", "Inactive"], index=0)
        # Updated Tiering selectbox
        tiering = st.selectbox("Tiering", options=TIERING_OPTIONS, index=TIERING_OPTIONS.index("Untiered")) # Default to Untiered
        # UPDATED: Category options now include new categories, with "Others" as default
        # Sort valid_categories before using in selectbox
        category_options_sorted = sorted(valid_categories)
        category = st.selectbox("Category", options=category_options_sorted, index=category_options_sorted.index("Others"))
        profile_picture = st.file_uploader("Upload Profile Picture", type=["png", "jpg", "jpeg"])

        col_add, col_cancel = st.columns(2)
        with col_add:
            submitted = st.form_submit_button("Add Contact")
        with col_cancel:
            if st.form_submit_button("Cancel"):
                st.session_state.show_add_form = False
                st.rerun()

        if submitted:
            if name and designation and country and company:
                new_profile_pic_bytes = None
                if profile_picture:
                    new_profile_pic_bytes = profile_picture.read()

                new_contact = {
                    "Name": name,
                    "Designation": designation,
                    "Country": country,
                    "Company": company,
                    "Phone Number": phone_number,
                    "Office Number": office_number,
                    "Email Address": email_address,
                    "Posting Date": posting_date,
                    "Deposted Date": deposted_date,
                    "Office Address": office_address,
                    "Home Address": home_address,
                    "Hobbies": hobbies,
                    "Dietary Restrictions": dietary_restrictions,
                    "Festivities": festivities_combined,
                    "Vehicle": vehicle,
                    "Golf": golf,
                    "Golf Handicap": golf_handicap,
                    "Reception": reception_combined,
                    "Marital Status": marital_status,
                    # Store None if the user selected "Unknown", or the integer value
                    "Children (Son)": children_son,
                    "Children (Daughter)": children_daughter,
                    "Date of Birth": final_date_of_birth_add,
                    "Known Age (Current Year)": final_known_age_current_year_add,
                    "Status": status,
                    "Tiering": tiering,
                    "Category": category,
                    "Photo": new_profile_pic_bytes,
                    "Comments": [], # New contacts start with no comments
                    "Last Updated By": st.session_state.user_role if st.session_state.user_role else "Unknown",
                    "Last Updated On": get_gmt8_now().strftime("%d %b %y, %I:%M %p"),
                    "History": [f"Created by {st.session_state.user_role if st.session_state.user_role else 'Unknown'} at {get_gmt8_now().strftime('%d %b %y, %I:%M %p')}"]
                }
                st.session_state.contacts_df = pd.concat([st.session_state.contacts_df, pd.DataFrame([new_contact])], ignore_index=True)
                st.sidebar.success("Contact added successfully!")
                st.session_state.show_add_form = False
                st.rerun()
            else:
                st.sidebar.error("Please fill in all required fields (Name, Designation, Country, Company).")

# --- 4. Admin Actions (Download & Upload) ---
def admin_actions():
    if st.session_state.user_role == "admin":
        st.sidebar.title("Admin Actions")

        # --- Manual Add Contact button (moved to top of admin section) ---
        if st.sidebar.button("Add New Contact (Manual)"):
            st.session_state.show_add_form = True
            st.rerun()

        # --- Download All Data (CSV only) ---
        df_for_download = st.session_state.contacts_df.copy()

        # Ensure all EXPECTED_COLUMNS are present before converting to CSV
        for col in EXPECTED_COLUMNS:
            if col not in df_for_download.columns:
                df_for_download[col] = None

        for col in ["Posting Date", "Deposted Date"]:
            if col in df_for_download.columns:
                df_for_download[col] = df_for_download[col].apply(
                    lambda x: x.strftime("%Y-%m-%d") if isinstance(x, (datetime, date)) else ""
                )
        # Special handling for Date of Birth to export "Unknown"
        if "Date of Birth" in df_for_download.columns:
            df_for_download["Date of Birth"] = df_for_download["Date of Birth"].apply(
                lambda x: x.strftime("%Y-%m-%d") if isinstance(x, (datetime, date)) else "Unknown"
            )


        # Convert children columns to string for download, handling None as "Unknown" and 0 as "0"
        for col in ["Children (Son)", "Children (Daughter)"]:
            if col in df_for_download.columns:
                df_for_download[col] = df_for_download[col].apply(
                    lambda x: "Unknown" if pd.isna(x) or x is None else str(int(x))
                )

        # Convert Known Age (Current Year) to string for download
        if "Known Age (Current Year)" in df_for_download.columns:
            df_for_download["Known Age (Current Year)"] = df_for_download["Known Age (Current Year)"].apply(
                lambda x: str(int(x)) if pd.notna(x) else ''
            )

        # Handle 'History' and 'Comments' for CSV export
        df_for_download['History'] = df_for_download['History'].apply(
            lambda x: "\n".join(x) if isinstance(x, list) else ""
        )
        df_for_download['Comments'] = df_for_download['Comments'].apply(
            lambda x: "\n".join(x) if isinstance(x, list) else ""
        )


        df_for_download['Profile Picture (Base64)'] = df_for_download['Photo'].apply(
            lambda x: base64.b64encode(x).decode('utf-8') if x is not None and isinstance(x, bytes) else ''
        )

        # Remove 'Photo' column as it's now Base64 encoded
        df_for_download = df_for_download.drop(columns=["Photo"], errors='ignore')

        csv_full_data = df_for_download.to_csv(index=False).encode('utf-8')

        st.sidebar.download_button(
            label="Download All Contacts (CSV)",
            data=csv_full_data,
            file_name="all_contacts_data.csv",
            mime="text/csv",
            help="Downloads all contact data, including Base64 encoded profile pictures."
        )


        # --- Download Template within an expander ---
        with st.sidebar.expander("Download Template"):
            st.write("Download a CSV template to fill in new contact data.")
            # Create a blank DataFrame with just the EXPECTED_COLUMNS
            template_df = pd.DataFrame(columns=EXPECTED_COLUMNS)
            # Drop columns that are typically not filled in by user for template
            template_df = template_df.drop(columns=["Photo", "Last Updated By", "Last Updated On", "History"], errors='ignore')

            # Add some example values to guide the user (optional, but very helpful)
            example_row = {
                "Name": "John Doe",
                "Designation": "Software Engineer",
                "Country": "Singapore",
                "Company": "Tech Solutions",
                "Phone Number": "6512345678",
                "Office Number": "6587654321",
                "Email Address": "john.doe@example.com",
                "Posting Date": "YYYY-MM-DD", # Guide for date format
                "Deposted Date": "YYYY-MM-DD (optional)",
                "Office Address": "1 Tech Park Drive",
                "Home Address": "123 Main Street",
                "Hobbies": "Reading, Hiking",
                "Dietary Restrictions": "None",
                "Festivities": "Chinese New Year, Christmas",
                "Vehicle": "Car",
                "Golf": "Yes",
                "Golf Handicap": "18",
                "Reception": "NYR, ALSE",
                "Marital Status": "Single",
                "Children (Son)": "1 or 0 or Unknown",
                "Children (Daughter)": "1 or 0 or Unknown",
                "Date of Birth": "YYYY-MM-DD or Unknown (optional)", # Updated template guidance
                "Known Age (Current Year)": "Age in current year (optional)",
                "Status": "Active",
                "Tiering": "A+",
                # UPDATED: Template now includes new categories for guidance
                "Category": "Local Rep, Overseas Rep, Chief, Dy Chief, ID, Others",
                "Comments": "Initial comment or leave blank" # Added comment guidance
            }
            # Append the example row to the template
            template_df = pd.concat([template_df, pd.DataFrame([example_row])], ignore_index=True)


            csv_template = template_df.to_csv(index=False).encode('utf-8')

            st.download_button( # Note: use st.download_button directly inside expander
                label="Download CSV Template",
                data=csv_template,
                file_name="contacts_template.csv",
                mime="text/csv",
                help="Download a CSV template to fill in new contact data."
            )

        # --- File Upload for Template (CSV only) within its own expander ---
        with st.sidebar.expander("Upload Contacts"):
            st.write("Upload your filled template (.csv) to add new contacts.")
            uploaded_file = st.file_uploader( # Note: use st.file_uploader directly inside expander
                "Upload your filled template (.csv)",
                type=["csv"],
                key="upload_filled_template_file",
                help="Upload the template file after you have filled it with new contacts."
            )

            if uploaded_file is not None:
                if st.button("Load Uploaded Template"): # Note: use st.button directly inside expander
                    try:
                        new_contacts_df = pd.read_csv(uploaded_file)

                        # --- Data Cleaning and Harmonization for Uploaded Template ---
                        # 1. Standardize column names (optional, but good practice)
                        new_contacts_df.columns = [col.strip() for col in new_contacts_df.columns]

                        harmonized_df = pd.DataFrame(columns=EXPECTED_COLUMNS)
                        for col in EXPECTED_COLUMNS:
                            if col in new_contacts_df.columns:
                                harmonized_df[col] = new_contacts_df[col]
                            else:
                                # Set appropriate defaults for columns not in the template or expected from user
                                if col in ["Children (Son)", "Children (Daughter)", "Known Age (Current Year)"]:
                                    harmonized_df[col] = None # Default to None for upload
                                elif col == "Date of Birth": # For DOB, ensure it handles "Unknown" from template
                                    harmonized_df[col] = None
                                elif col in ["Last Updated By", "Last Updated On"]:
                                    harmonized_df[col] = None # Will be filled later
                                elif col == "History":
                                    harmonized_df[col] = [[] for _ in range(len(new_contacts_df))]
                                elif col == "Comments": # Initialize comments as empty list for upload
                                    harmonized_df[col] = [[] for _ in range(len(new_contacts_df))]
                                elif col == "Photo":
                                    harmonized_df[col] = None
                                else:
                                    harmonized_df[col] = None # Or "" for strings

                        # Convert specific columns to appropriate types
                        for date_col in ["Posting Date", "Deposted Date"]:
                            if date_col in harmonized_df.columns:
                                harmonized_df[date_col] = pd.to_datetime(harmonized_df[date_col], errors='coerce').dt.date

                        # Handle Date of Birth specifically for upload: "Unknown" or empty becomes None
                        if "Date of Birth" in harmonized_df.columns:
                            harmonized_df["Date of Birth"] = harmonized_df["Date of Birth"].astype(str).apply(
                                lambda x: pd.to_datetime(x, errors='coerce').date() if x.strip().lower() not in ['unknown', 'nan', ''] else None
                            )


                        # Handle children columns specifically for upload: '0' becomes 0, numbers becomes int, 'unknown' becomes None
                        for child_col in ["Children (Son)", "Children (Daughter)"]:
                            if child_col in harmonized_df.columns:
                                harmonized_df[child_col] = harmonized_df[child_col].astype(str).apply(
                                    # Convert to None if 'unknown' or empty, otherwise try to convert to number
                                    lambda x: None if x.strip().lower() in ['unknown', 'nan', ''] else pd.to_numeric(x, errors='coerce')
                                )
                                # Convert to int if not None, otherwise keep as None
                                harmonized_df[child_col] = harmonized_df[child_col].apply(lambda x: int(x) if pd.notna(x) else None)

                        # Handle Known Age (Current Year) specifically for upload
                        if "Known Age (Current Year)" in harmonized_df.columns:
                            harmonized_df["Known Age (Current Year)"] = harmonized_df["Known Age (Current Year)"].astype(str).apply(
                                lambda x: pd.to_numeric(x, errors='coerce') if x.strip() and x.strip().lower() not in ['nan', ''] else None
                            )
                            harmonized_df["Known Age (Current Year)"] = harmonized_df["Known Age (Current Year)"].apply(lambda x: int(x) if pd.notna(x) else None)


                        for list_col in ["Festivities", "Reception"]:
                            if list_col in harmonized_df.columns:
                                harmonized_df[list_col] = harmonized_df[list_col].astype(str).replace('nan', '').apply(
                                    lambda x: ", ".join(sorted([item.strip() for item in x.split(',') if item.strip()])) if x else ""
                                )

                        # Handle 'Comments' column from upload: split by newline if string, ensure list
                        if "Comments" in harmonized_df.columns:
                            harmonized_df["Comments"] = harmonized_df["Comments"].astype(str).replace('nan', '').apply(
                                lambda x: [item.strip() for item in x.split('\n') if item.strip()] if x else []
                            )


                        # Ensure essential columns are not null for new entries
                        required_cols = ["Name", "Designation", "Country", "Company"]
                        # Check if any of the required columns have nulls in the uploaded DataFrame
                        if harmonized_df[required_cols].isnull().any().any():
                            st.error("Uploaded template contains rows with missing essential information (Name, Designation, Country, Company). Please fill these fields.")
                        else:
                            # Set Last Updated fields and add initial history entry
                            harmonized_df["Last Updated By"] = st.session_state.user_role if st.session_state.user_role else "Unknown (Template Upload)"
                            harmonized_df["Last Updated On"] = get_gmt8_now().strftime("%d %b %y, %I:%M %p")

                            harmonized_df["History"] = harmonized_df.apply(
                                lambda row: row["History"] + [f"Imported by {st.session_state.user_role if st.session_state.user_role else 'Unknown'} via template upload on {get_gmt8_now().strftime('%d %b %y, %I:%M %p')}"] , axis=1
                            )

                            st.session_state.contacts_df = pd.concat([st.session_state.contacts_df, harmonized_df], ignore_index=True)
                            st.success(f"Successfully loaded {len(harmonized_df)} contacts from the template!")
                            st.rerun()

                    except Exception as e:
                        st.error(f"Error reading file: {e}")
                        st.info("Please ensure your template is correctly filled and saved as .csv.")

# --- 5. Search and Filter Functionality ---
def search_and_filter(selected_category):
    st.sidebar.title("Other Filters")
    search_query = st.sidebar.text_input("Search (any field)")

    show_inactive = st.sidebar.checkbox("Show Inactive Contacts", value=False)

    all_designations = sorted(st.session_state.contacts_df["Designation"].dropna().unique().tolist())
    all_countries = sorted(st.session_state.contacts_df["Country"].dropna().unique().tolist())
    all_companies = sorted(st.session_state.contacts_df["Company"].dropna().unique().tolist())

    # Use the new TIERING_OPTIONS for filtering
    all_tierings = TIERING_OPTIONS

    all_golf_options = ["Yes", "No"]

    # Get ALL unique reception options from data for filtering, including custom ones
    all_reception_options_from_data = []
    for reception_str in st.session_state.contacts_df["Reception"].dropna().unique():
        all_reception_options_from_data.extend([r.strip() for r in str(reception_str).split(',') if r.strip()])
    # Combine with master list and sort
    # Now that RECEPTION_OPTIONS_MASTER is defined globally, we can use it here
    all_reception_options_for_filter = sorted(list(set(RECEPTION_OPTIONS_MASTER + all_reception_options_from_data)))


    # Get ALL unique festivities options from data for filtering, including custom ones
    all_festivities_options_from_data = []
    for festivity_str in st.session_state.contacts_df["Festivities"].dropna().unique():
        all_festivities_options_from_data.extend([f.strip() for f in str(festivity_str).split(',') if f.strip()])
    # Combine with common list and sort
    all_festivities_options_for_filter = sorted(list(set(COMMON_FESTIVITIES + all_festivities_options_from_data)))


    selected_designations = st.sidebar.multiselect("Designation", options=all_designations, default=[])
    selected_countries = st.sidebar.multiselect("Country", options=all_countries, default=[])
    selected_companies = st.sidebar.multiselect("Company", options=all_companies, default=[])
    selected_tierings = st.sidebar.multiselect("Tiering", options=all_tierings, default=[])
    selected_golf = st.sidebar.multiselect("Golf", options=all_golf_options, default=[])

    # New filters for Reception and Festivities, using the dynamically generated options
    selected_reception = st.sidebar.multiselect("Reception", options=all_reception_options_for_filter, default=[])
    selected_festivities = st.sidebar.multiselect("Festivities", options=all_festivities_options_for_filter, default=[])


    filtered_df = st.session_state.contacts_df.copy()

    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["Category"] == selected_category]

    if not show_inactive:
        filtered_df = filtered_df[filtered_df["Status"] == "Active"]

    if selected_designations:
        filtered_df = filtered_df[filtered_df["Designation"].isin(selected_designations)]
    if selected_countries:
        filtered_df = filtered_df[filtered_df["Country"].isin(selected_countries)]
    if selected_companies:
        filtered_df = filtered_df[filtered_df["Company"].isin(selected_companies)]
    if selected_tierings:
        filtered_df = filtered_df[filtered_df["Tiering"].isin(selected_tierings)]
    if selected_golf:
        filtered_df = filtered_df[filtered_df["Golf"].isin(selected_golf)]

    # Apply Reception filter
    if selected_reception:
        filtered_df = filtered_df[
            filtered_df["Reception"].astype(str).apply(
                lambda x: any(item in x.split(', ') for item in selected_reception)
            )
        ]

    # Apply Festivities filter
    if selected_festivities:
        filtered_df = filtered_df[
            filtered_df["Festivities"].astype(str).apply(
                lambda x: any(item in x.split(', ') for item in selected_festivities)
            )
        ]


    if search_query:
        search_query_lower = search_query.lower()
        # Ensure all columns exist before searching, handle potential missing ones gracefully
        searchable_df = filtered_df.copy()
        for col in EXPECTED_COLUMNS: # Use EXPECTED_COLUMNS to be comprehensive
            if col not in searchable_df.columns:
                searchable_df[col] = '' # Add missing column as empty string for search

        mask = searchable_df.drop(columns=["Photo"], errors='ignore').apply(
            lambda row: row.astype(str).str.lower().str.contains(search_query_lower, na=False).any(), axis=1
        )
        filtered_df = filtered_df[mask]

    # --- NEW SORTING LOGIC ---
    # 1. Create a temporary column for Designation Protocol Rank
    filtered_df['Designation_Rank'] = filtered_df['Designation'].apply(get_designation_protocol_rank)

    # 2. Sort by Country (alphabetical), then Company (alphabetical),
    #    then Designation Rank (numerical protocol), then Designation (alphabetical for ties)
    filtered_df = filtered_df.sort_values(
        by=["Country", "Company", "Designation_Rank", "Designation"],
        ascending=[True, True, True, True]
    ).drop(columns=['Designation_Rank']) # Drop the helper column after sorting

    return filtered_df

# --- 6. Main App Logic ---
def main():
    # Define RECEPTION_OPTIONS_MASTER globally here, as it depends on initial data load
    # Initialize RECEPTION_OPTIONS_MASTER with some common options
    # This list will be the *fixed* set of options presented in the multiselect for editing/adding
    global RECEPTION_OPTIONS_MASTER
    RECEPTION_OPTIONS_MASTER = ["ALSE", "NYR", "Client Event", "Networking Mixer", "Industry Fair", "Board Meeting", "Investor Call", "Tech Conference", "Project Review", "Book Launch", "Charity Event", "Parliament Session", "Review", "Others"]
    RECEPTION_OPTIONS_MASTER.sort()

    if st.session_state.user_role is None:
        st.title("Welcome to the Contact Card App 👋")
        login()
    else:
        st.sidebar.write(f"Logged in as: **{st.session_state.user_role.capitalize()}**")
        logout()

        st.title("Contact Cards 📇")

        # --- Category Buttons on Main Page ---
        col1, col2 = st.columns([0.5,2])
        with col1:
            st.write("#### Filter by Category:")

        with col2:
            # UPDATED: Category options for buttons on main page
            category_options = ["All", "Chief", "Dy Chief", "ID", "Local Rep", "Overseas Rep", "Others"] # Manually sorted for button display
            cols = st.columns(len(category_options))

            for i, category_name in enumerate(category_options):
                with cols[i]:
                    # Apply conditional styling for the selected button
                    button_style = ""
                    if category_name == st.session_state.selected_category_button:
                        button_style = "background-color: #6a0dad; color: white; border-color: #6a0dad;"

                    # Using markdown to create buttons with custom style
                    if st.button(category_name, key=f"cat_btn_{category_name}"):
                        st.session_state.selected_category_button = category_name
                        st.rerun()
        st.markdown("---")

        if st.session_state.user_role == "admin":
            admin_actions() # Call the new admin_actions function

            # The 'Add New Contact (Manual)' button is now handled INSIDE admin_actions()
            if st.session_state.show_add_form:
                add_new_contact_form()

        elif st.session_state.user_role == "user":
            if st.sidebar.button("Add New Contact"):
                st.session_state.show_add_form = True
                st.rerun()

            if st.session_state.show_add_form:
                add_new_contact_form()

        st.sidebar.markdown("---")
        filtered_contacts = search_and_filter(st.session_state.selected_category_button)

        st.markdown(f"**Currently displaying {len(filtered_contacts)} contacts.**")

        if not filtered_contacts.empty:
            for index, contact in filtered_contacts.iterrows():
                display_contact_card(contact, index)
        else:
            st.info("No contacts found matching your criteria for the selected category.")

if __name__ == "__main__":
    main()