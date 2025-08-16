import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from PIL import Image
import io
import base64
from pathlib import Path
import os

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
    "Status", "Tiering", "Category", "Photo",
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
        ["Albert", "SC", "Australia", "CompanyA", "98765432", "9876544321", "albert@company.com", date(2025, 8, 12), None, "123 bsdlk slhf", "456 Home Rd, Perth", "sleeping", "NIL", "Deepavali", "s1234cd", "Yes", "20", "NYR, ALSE", "Married", 1, 1, "Active", "A", "Local Rep", None, "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"), []], # Use get_gmt8_now()
        ["Bob The Builder", "Project Manager", "Canada", "BuildCo","987-654-3210", "654-321-0987", "bob@buildco.ca", date(2025, 8, 12), None, "789 Construction Blvd, Toronto", "101 Maple Lane, Toronto", "Gardening, Cycling", "None", "Canada Day", "s1234cd", "Yes", "20", "Client Meeting", "Single", 0, 0, "Active", "B", "Overseas Rep", None, "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"), []], # Use get_gmt8_now()
        ["Charlie Chaplin", "Actor", "UK", "Comedy Gold Studios", "555-123-4567", "555-987-6543", "charlie@comedy.co.uk", date(2025, 8, 12), None, "Studio 5, London", "1 Baker Street, London", "Filmmaking, Chess", "Vegan", "Halloween", "s1234cd", "Yes", "20", "Film Premiere", "Divorced", 1, 0, "Inactive", "C", "Chief", None, "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"), []], # Use get_gmt8_now()
        ["David Lee", "Engineer", "Singapore", "TechCorp", "65123456", "65789012", "david.lee@techcorp.sg", date(2024, 1, 15), None, "Science Park Dr", "Holland Village", "Hiking", "Gluten-free", "Chinese New Year", "sedan", "No", "N/A", "Project Review", "Married", 0, 2, "Active", "A", "ID", None, "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"), []], # Use get_gmt8_now()
        ["Eve Adams", "CEO", "USA", "Global Solutions", "123-456-7890", "987-654-3210", "eve@globalsolutions.com", date(2023, 10, 20), None, "Wall Street, NYC", "5th Avenue, NYC", "Reading, Yoga", "None", "Thanksgiving", "SUV", "Yes", "15", "Board Meeting", "Single", 0, 0, "Active", "A", "Chief", None, "System", get_gmt8_now().strftime("%d %b %y, %I:%M %p"), []] # Use get_gmt8_now()
    ]
    
    # Create the initial DataFrame from the sample data
    st.session_state.contacts_df = pd.DataFrame(initial_data, columns=EXPECTED_COLUMNS)


# Ensure all EXPECTED_COLUMNS are present in the DataFrame, adding them if missing
for col in EXPECTED_COLUMNS:
    if col not in st.session_state.contacts_df.columns:
        # For numerical columns like children, initialize with 0
        if col in ["Children (Son)", "Children (Daughter)"]:
            st.session_state.contacts_df[col] = 0
        else:
            st.session_state.contacts_df[col] = None # Or an appropriate default value like ""

# Ensure all 'Category' values are valid based on your options
valid_categories = ["Local Rep", "Overseas Rep", "Chief", "ID", "N/A"]
if 'contacts_df' in st.session_state:
    st.session_state.contacts_df['Category'] = st.session_state.contacts_df['Category'].apply(
        lambda x: x if x in valid_categories else "N/A"
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

RECEPTION_OPTIONS = ["ALSE", "NYR", "Others"]

COMMON_FESTIVITIES = [
    "Chinese New Year", "Deepavali", "Christmas", "Hari Raya Puasa", "Eid al-Fitr",
    "Eid al-Adha", "Halloween", "Thanksgiving", "Diwali", "New Year's Day",
    "Easter", "Ramadan", "Hanukkah", "Oktoberfest", "Carnival",
    "St. Patrick's Day", "Independence Day (US)", "Canada Day", "Bastille Day"
    # Add more common festivities
]
COMMON_FESTIVITIES.sort() # Keep them sorted

MARITAL_STATUS_OPTIONS = ["Single", "Married", "Divorced", "Widowed", "Separated", "Prefer not to say"]


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
def process_multi_text_input(selected_options, custom_text):
    combined = []
    if selected_options:
        combined.extend(selected_options)
    
    if custom_text:
        # Split by comma and clean up spaces, then add to combined
        new_entries = [item.strip() for item in custom_text.split(',') if item.strip()]
        for entry in new_entries:
            if entry not in combined:
                combined.append(entry)
    
    # Sort and return as a comma-separated string for consistency with existing data
    combined.sort()
    return ", ".join(combined)

# --- 2. Contact Card Display and Editing ---
def edit_contact_form(contact, index):
    st.markdown("<h4>Edit Contact</h4>", unsafe_allow_html=True)
    with st.form(key=f"edit_form_{index}"):
        name = st.text_input("Name*", value=contact["Name"], key=f"edit_name_{index}")
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

        initial_posting_date = contact["Posting Date"]
        if isinstance(initial_posting_date, (datetime, date)):
            posting_date_value = initial_posting_date
        elif pd.notna(initial_posting_date) and initial_posting_date != 'N/A':
            try:
                posting_date_value = pd.to_datetime(initial_posting_date).date()
            except ValueError:
                posting_date_value = None
        else:
            posting_date_value = None

        posting_date = st.date_input("Posting Date", value=posting_date_value, key=f"edit_posting_date_{index}")

        initial_deposted_date = contact["Deposted Date"]
        if isinstance(initial_deposted_date, (datetime, date)):
            deposted_date_value = initial_deposted_date
        elif pd.notna(initial_deposted_date) and initial_deposted_date != 'N/A':
            try:
                deposted_date_value = pd.to_datetime(initial_deposted_date).date()
            except ValueError:
                deposted_date_value = None
        else:
            deposted_date_value = None

        deposted_date = st.date_input("Deposted Date", value=deposted_date_value, key=f"edit_deposted_date_{index}")


        office_address = st.text_area("Office Address", value=contact["Office Address"], key=f"edit_office_address_{index}")
        home_address = st.text_area("Home Address", value=contact["Home Address"], key=f"edit_home_address_{index}")
        hobbies = st.text_input("Hobbies", value=contact["Hobbies"], key=f"edit_hobbies_{index}")
        dietary_restrictions = st.text_input("Dietary Restrictions", value=contact["Dietary Restrictions"], key=f"edit_dietary_restrictions_{index}")
        
        # Festivities Multiselect + Text Area
        current_festivities_list = [f.strip() for f in str(contact["Festivities"]).split(',') if f.strip()] if pd.notna(contact["Festivities"]) else []
        
        # Determine default selected options for multiselect
        default_selected_festivities = [f for f in current_festivities_list if f in COMMON_FESTIVITIES]
        
        # Determine custom text part
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
        festivities_combined = process_multi_text_input(selected_festivities, custom_festivities_input)


        vehicle = st.text_input("Vehicle", value=contact["Vehicle"], key=f"edit_vehicle_{index}")

        # Golf selection field - Always visible
        golf = st.selectbox("Golf",["Yes", "No"], index=0 if contact["Golf"] == "Yes" else 1, key=f"edit_golf_{index}")

        # Golf Handicap - Always visible
        handicap = st.text_input("Golf Handicap", value=contact["Golf Handicap"], key=f"edit_golf_handicap_{index}")

        # Reception Multiselect
        current_reception_list = [r.strip() for r in str(contact["Reception"]).split(',') if r.strip()] if pd.notna(contact["Reception"]) else []
        
        reception = st.multiselect(
            "Reception",
            options=RECEPTION_OPTIONS,
            default=current_reception_list,
            key=f"edit_reception_{index}"
        )
        reception_combined = ", ".join(sorted(reception)) if reception else "" # Ensure sorted for consistent string

        # Marital Status Dropdown (New Field)
        # Access 'Marital Status' safely
        marital_status_value = contact.get("Marital Status", MARITAL_STATUS_OPTIONS[0]) # Default to first option
        current_marital_status_index = MARITAL_STATUS_OPTIONS.index(marital_status_value) if marital_status_value in MARITAL_STATUS_OPTIONS else 0
        marital_status = st.selectbox(
            "Marital Status",
            options=MARITAL_STATUS_OPTIONS,
            index=current_marital_status_index,
            key=f"edit_marital_status_{index}"
        )

        # Children Quantity (New Fields)
        col_son, col_daughter = st.columns(2)
        with col_son:
            # Safely get the value for children_son, defaulting to 0 if None/NaN
            children_son_value = int(contact.get("Children (Son)", 0)) if pd.notna(contact.get("Children (Son)", 0)) else 0
            children_son = st.number_input(
                "Children (Sons)",
                min_value=0,
                value=children_son_value, # Use the safely determined value
                step=1,
                key=f"edit_children_son_{index}"
            )
        with col_daughter:
            # Safely get the value for children_daughter, defaulting to 0 if None/NaN
            children_daughter_value = int(contact.get("Children (Daughter)", 0)) if pd.notna(contact.get("Children (Daughter)", 0)) else 0
            children_daughter = st.number_input(
                "Children (Daughters)",
                min_value=0,
                value=children_daughter_value, # Use the safely determined value
                step=1,
                key=f"edit_children_daughter_{index}"
            )


        status = st.selectbox("Status", ["Active", "Inactive"], index=["Active", "Inactive"].index(contact["Status"]), key=f"edit_status_{index}")
        tiering = st.selectbox("Tiering", ["A", "B", "C", "Untiered"], index=["A", "B", "C", "Untiered"].index(contact["Tiering"]), key=f"edit_tiering_{index}")
        category_options = ["Local Rep", "Overseas Rep", "Chief", "ID", "N/A"]
        current_category_index = category_options.index(contact["Category"]) if contact["Category"] in category_options else category_options.index("N/A")
        category = st.selectbox("Category", options=category_options, index=current_category_index, key=f"edit_category_{index}")


        uploaded_file = st.file_uploader("Upload new profile picture", type=["png", "jpg", "jpeg"], key=f"edit_pic_{index}")

        col_update, col_cancel = st.columns(2)
        with col_update:
            submitted = st.form_submit_button("Update Contact")
        with col_cancel:
            if st.form_submit_button("Cancel"):
                st.session_state.editing_contact_index = None
                st.rerun()

        if submitted:
            if name and designation and country and company:
                updated_contact = contact.copy()

                changes = []
                def track_change(field_name, old_val, new_val):
                    # Safely get old_val, especially if it was missing before the column addition
                    old_val_to_compare = old_val if pd.notna(old_val) else None
                    new_val_to_compare = new_val if pd.notna(new_val) else None

                    if isinstance(old_val_to_compare, (datetime, date)):
                        old_val_str = old_val_to_compare.strftime("%Y-%m-%d") if old_val_to_compare else "N/A"
                    else:
                        old_val_str = str(old_val_to_compare) if old_val_to_compare is not None else "N/A"

                    if isinstance(new_val_to_compare, (datetime, date)):
                        new_val_str = new_val_to_compare.strftime("%Y-%m-%d") if new_val_to_compare else "N/A"
                    else:
                        new_val_str = str(new_val_to_compare) if new_val_to_compare is not None else "N/A"

                    if old_val_str != new_val_str:
                        changes.append(f"{field_name} changed from '{old_val_str}' to '{new_val_str}'")
                        return new_val
                    return old_val # Return original old_val for unchanged fields

                updated_contact["Name"] = track_change("Name", contact["Name"], name)
                updated_contact["Designation"] = track_change("Designation", contact["Designation"], designation)
                updated_contact["Country"] = track_change("Country", contact["Country"], country)
                updated_contact["Company"] = track_change("Company", contact["Company"], company)
                updated_contact["Phone Number"] = track_change("Phone Number", contact["Phone Number"], phone_number)
                updated_contact["Office Number"] = track_change("Office Number", contact["Office Number"], office_number)
                # Safely track change for Email Address
                updated_contact["Email Address"] = track_change("Email Address", contact.get("Email Address", None), email_address)
                updated_contact["Posting Date"] = track_change("Posting Date", contact["Posting Date"], posting_date)
                updated_contact["Deposted Date"] = track_change("Deposted Date", contact["Deposted Date"], deposted_date)
                updated_contact["Office Address"] = track_change("Office Address", contact["Office Address"], office_address)
                updated_contact["Home Address"] = track_change("Home Address", contact["Home Address"], home_address)
                updated_contact["Hobbies"] = track_change("Hobbies", contact["Hobbies"], hobbies)
                updated_contact["Dietary Restrictions"] = track_change("Dietary Restrictions", contact["Dietary Restrictions"], dietary_restrictions)
                updated_contact["Festivities"] = track_change("Festivities", contact["Festivities"], festivities_combined) # Use combined value
                updated_contact["Vehicle"] = track_change("Vehicle", contact["Vehicle"], vehicle)
                updated_contact["Golf"] = track_change("Golf", contact["Golf"], golf)
                updated_contact["Golf Handicap"] = track_change("Golf Handicap", contact["Golf Handicap"], handicap)
                updated_contact["Reception"] = track_change("Reception", contact["Reception"], reception_combined) # Use combined value
                # Safely track change for Marital Status and Children
                updated_contact["Marital Status"] = track_change("Marital Status", contact.get("Marital Status", None), marital_status)
                # Ensure children values are tracked as integers
                updated_contact["Children (Son)"] = track_change("Children (Son)", contact.get("Children (Son)", 0), children_son)
                updated_contact["Children (Daughter)"] = track_change("Children (Daughter)", contact.get("Children (Daughter)", 0), children_daughter)
                updated_contact["Status"] = track_change("Status", contact["Status"], status)
                updated_contact["Tiering"] = track_change("Tiering", contact["Tiering"], tiering)
                updated_contact["Category"] = track_change("Category", contact["Category"], category)

                new_pic_bytes = None
                if uploaded_file is not None:
                    new_pic_bytes = uploaded_file.read()
                    if contact["Photo"] is None:
                        changes.append("Profile picture added")
                    elif new_pic_bytes != contact["Photo"]:
                        changes.append("Profile picture updated")
                    updated_contact["Photo"] = new_pic_bytes

                if changes:
                    update_info = (f"Updated by {st.session_state.user_role} at {get_gmt8_now().strftime('%d %b %y, %I:%M %p')}.<br>" # Use get_gmt8_now()
                                   + "<br>".join(changes))
                    updated_contact["Last Updated By"] = st.session_state.user_role
                    updated_contact["Last Updated On"] = get_gmt8_now().strftime("%d %b %y, %I:%M %p") # Use get_gmt8_now()
                    updated_contact["History"].append(update_info)

                st.session_state.contacts_df.loc[index] = updated_contact
                st.success("Contact updated successfully!")
                st.session_state.editing_contact_index = None
                st.rerun()
            else:
                st.error("Please fill in all required fields (Name, Designation, Country, Company).")


def get_tier_color(Tiering):
    tier_colors = {
        "A+": "green",
        "A": "blue",
        "B": "purple",
        "C": "orange",
        "Untiered": "gray"
    }
    return tier_colors.get(Tiering, "gray")

def get_status_color(status):
     return "green" if status == "Active" else "red"

def display_contact_card(contact, index):
    employee_data = contact.fillna('Nil')
    with st.container():

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
                image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="


        if st.session_state.editing_contact_index == index:
            edit_contact_form(contact, index)

        else:
            # Determine children display string
            # Get values safely and ensure they are numbers, converting None to 0
            num_sons_raw = contact.get('Children (Son)', 0)
            num_daughters_raw = contact.get('Children (Daughter)', 0)

            # Explicitly handle None by converting to 0 before int()
            num_sons = int(num_sons_raw) if num_sons_raw is not None else 0
            num_daughters = int(num_daughters_raw) if num_daughters_raw is not None else 0
            
            if num_sons == 0 and num_daughters == 0:
                children_display = "N/A"
            else:
                children_parts = []
                if num_sons > 0:
                    children_parts.append(f"{num_sons} Son{'s' if num_sons > 1 else ''}")
                if num_daughters > 0:
                    children_parts.append(f"{num_daughters} Daughter{'s' if num_daughters > 1 else ''}")
                children_display = ", ".join(children_parts)

            st.markdown(
                f"""
                <div style="border-radius: 10px; border: 1px solid #000000; padding: 15px; background-color: #ffe0b2;">
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <img src="data:image/png;base64,{image_base64}" style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover;">
                        <div style="flex: 1;">
                            <h3 style="margin: 0; font-size: 20px; color: #000000;">
                                {contact['Name']}
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
                        <div style="flex: 1; min-width: 150px; color: #000000">
                            <p><b>Country:</b> {contact['Country']}</p>
                            <p><b>Phone Number.:</b> {contact['Phone Number']}</p>
                            <p><b>Office Number.:</b> {contact['Office Number']}</p>
                            <p><b>Email Address:</b> {contact.get('Email Address', 'N/A')}</p>
                            <p><b>Vehicle(s):</b> {contact['Vehicle']}</p>
                            <p><b>Address:</b> {contact['Office Address']}</p>
                        </div>
                        <div style="flex: 1; min-width: 150px; color: #000000">
                            <p><b>Posting Date:</b> {formatted_posting_date}</p>
                            <p><b>De-posted Date:</b> {formatted_deposted_date}</p>
                            <p><b>Golf:</b> {contact['Golf']}</p>
                            <p><b>Golf Handicap:</b> {contact['Golf Handicap']}</p>
                            <p><b>Marital Status:</b> {contact.get('Marital Status', 'N/A')}</p>
                            <p><b>Children:</b> {children_display}</p>
                        </div>
                        <div style="flex: 1; min-width: 150px; color: #000000">
                            <p><b>Dietary Restrictions:</b> {contact['Dietary Restrictions']}</p>
                            <p><b>Reception:</b> {contact['Reception']}</p>
                            <p><b>Festivity:</b> {contact['Festivities']}</p>
                        </div>
                        <div style="flex: 1; min-width: 150px; color: #000000">
                            <p><b>Interest(s):</b> {contact['Hobbies']}</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        if contact["Last Updated On"]:
                st.info(f"Last updated by {contact['Last Updated By']} at {contact['Last Updated On']}")

        if st.session_state.user_role == "admin":
            col_edit, col_history = st.columns(2)
            with col_edit:
                if st.button(f"Edit {contact['Name']}", key=f"edit_button_{index}"):
                    st.session_state.editing_contact_index = index
                    st.rerun()
            with col_history:
                with st.expander("View History"):
                    if contact["History"]:
                        for i, history_entry in enumerate(contact["History"]):
                            st.markdown(f"**{i+1}.** {history_entry}", unsafe_allow_html=True)
                    else:
                        st.write("No history available.")


# --- Add New Contact ➕ ---
def add_new_contact_form():
    st.sidebar.title("Add New Contact")

    with st.form(key="add_contact_form"):
        name = st.text_input("Name*")
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
        festivities_combined = process_multi_text_input(selected_festivities, custom_festivities_input)


        # Reception Multiselect
        reception = st.multiselect(
            "Reception",
            options=RECEPTION_OPTIONS,
            default=[]
        )
        reception_combined = ", ".join(sorted(reception)) if reception else ""


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

        # Children Quantity
        col_son_add, col_daughter_add = st.columns(2)
        with col_son_add:
            children_son = st.number_input(
                "Children (Sons)",
                min_value=0,
                value=0, # Ensure default value is an int
                step=1
            )
        with col_daughter_add:
            children_daughter = st.number_input(
                "Children (Daughters)",
                min_value=0,
                value=0, # Ensure default value is an int
                step=1
            )


        status = st.selectbox("Status", ["Active", "Inactive"], index=0)
        tiering = st.selectbox("Tiering", ["A", "B", "C", "Untiered"], index=3)
        category = st.selectbox("Category", options=["Local Rep", "Overseas Rep", "Chief", "ID", "N/A"], index=4) # Default to N/A
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
                    "Children (Son)": children_son, # These are already ints from st.number_input
                    "Children (Daughter)": children_daughter, # These are already ints from st.number_input
                    "Status": status,
                    "Tiering": tiering,
                    "Category": category,
                    "Photo": new_profile_pic_bytes,
                    "Last Updated By": st.session_state.user_role if st.session_state.user_role else "Unknown",
                    "Last Updated On": get_gmt8_now().strftime("%d %b %y, %I:%M %p"), # Use get_gmt8_now()
                    "History": [f"Created by {st.session_state.user_role if st.session_state.user_role else 'Unknown'} at {get_gmt8_now().strftime('%d %b %y, %I:%M %p')}"] # Use get_gmt8_now()
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
        st.sidebar.markdown("---")
        st.sidebar.title("Admin Actions")

        # --- Download All Data ---
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

        df_for_download['History'] = df_for_download['History'].apply(
            lambda x: "\n".join(x) if isinstance(x, list) else ""
        )

        df_for_download['Profile Picture (Base64)'] = df_for_download['Photo'].apply(
            lambda x: base64.b64encode(x).decode('utf-8') if x is not None and isinstance(x, bytes) else ''
        )

        # Remove 'Photo' column as it's now Base64 encoded
        df_for_download = df_for_download.drop(columns=["Photo"], errors='ignore')

        csv_full_data = df_for_download.to_csv(index=False).encode('utf-8')
        excel_full_data = io.BytesIO()
        df_for_download.to_excel(excel_full_data, index=False, engine='xlsxwriter')
        excel_full_data.seek(0)

        st.sidebar.download_button(
            label="Download All Contacts (CSV)",
            data=csv_full_data,
            file_name="all_contacts_data.csv",
            mime="text/csv",
            help="Downloads all contact data, including Base64 encoded profile pictures and change history."
        )
        st.sidebar.download_button(
            label="Download All Contacts (Excel)",
            data=excel_full_data,
            file_name="all_contacts_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Downloads all contact data in Excel format."
        )

        st.sidebar.markdown("---")
        st.sidebar.subheader("Upload Contacts using Template")

        # --- Download Template ---
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
            "Children (Son)": "0",
            "Children (Daughter)": "0",
            "Status": "Active", # Guide for expected values
            "Tiering": "A",
            "Category": "Local Rep"
        }
        # Append the example row to the template
        template_df = pd.concat([template_df, pd.DataFrame([example_row])], ignore_index=True)


        csv_template = template_df.to_csv(index=False).encode('utf-8')
        excel_template = io.BytesIO()
        template_df.to_excel(excel_template, index=False, engine='xlsxwriter')
        excel_template.seek(0)

        st.sidebar.download_button(
            label="Download CSV Template",
            data=csv_template,
            file_name="contacts_template.csv",
            mime="text/csv",
            help="Download a CSV template to fill in new contact data."
        )
        st.sidebar.download_button(
            label="Download Excel Template",
            data=excel_template,
            file_name="contacts_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download an Excel template to fill in new contact data."
        )

        # --- File Upload for Template ---
        uploaded_file = st.sidebar.file_uploader(
            "Upload your filled template (.xlsx or .csv)",
            type=["xlsx", "csv"],
            key="upload_filled_template_file",
            help="Upload the template file after you have filled it with new contacts."
        )

        if uploaded_file is not None:
            if st.sidebar.button("Load Uploaded Template"):
                try:
                    if uploaded_file.name.endswith('.csv'):
                        new_contacts_df = pd.read_csv(uploaded_file)
                    elif uploaded_file.name.endswith('.xlsx'):
                        new_contacts_df = pd.read_excel(uploaded_file)
                    
                    # --- Data Cleaning and Harmonization for Uploaded Template ---
                    # 1. Standardize column names (optional, but good practice)
                    new_contacts_df.columns = [col.strip() for col in new_contacts_df.columns]
                    
                    harmonized_df = pd.DataFrame(columns=EXPECTED_COLUMNS)
                    for col in EXPECTED_COLUMNS:
                        if col in new_contacts_df.columns:
                            harmonized_df[col] = new_contacts_df[col]
                        else:
                            # Set appropriate defaults for columns not in the template or expected from user
                            if col in ["Children (Son)", "Children (Daughter)"]:
                                harmonized_df[col] = 0
                            elif col in ["Last Updated By", "Last Updated On"]:
                                harmonized_df[col] = None # Will be filled later
                            elif col == "History":
                                harmonized_df[col] = [[] for _ in range(len(new_contacts_df))]
                            elif col == "Photo":
                                harmonized_df[col] = None
                            else:
                                harmonized_df[col] = None # Or "" for strings

                    # Convert specific columns to appropriate types
                    for date_col in ["Posting Date", "Deposted Date"]:
                        if date_col in harmonized_df.columns:
                            harmonized_df[date_col] = pd.to_datetime(harmonized_df[date_col], errors='coerce').dt.date

                    for child_col in ["Children (Son)", "Children (Daughter)"]:
                        if child_col in harmonized_df.columns:
                            harmonized_df[child_col] = pd.to_numeric(harmonized_df[child_col], errors='coerce').fillna(0).astype(int)

                    for list_col in ["Festivities", "Reception"]:
                        if list_col in harmonized_df.columns:
                            harmonized_df[list_col] = harmonized_df[list_col].astype(str).replace('nan', '').apply(
                                lambda x: ", ".join(sorted([item.strip() for item in x.split(',') if item.strip()])) if x else ""
                            )
                    
                    # Ensure essential columns are not null for new entries
                    required_cols = ["Name", "Designation", "Country", "Company"]
                    if not harmonized_df[required_cols].isnull().all(axis=1).any(): # Check if any row is entirely null for required cols
                        # Set Last Updated fields and add initial history entry
                        harmonized_df["Last Updated By"] = st.session_state.user_role if st.session_state.user_role else "Unknown (Template Upload)"
                        harmonized_df["Last Updated On"] = get_gmt8_now().strftime("%d %b %y, %I:%M %p")
                        
                        harmonized_df["History"] = harmonized_df.apply(
                            lambda row: row["History"] + [f"Imported by {st.session_state.user_role if st.session_state.user_role else 'Unknown'} via template upload on {get_gmt8_now().strftime('%d %b %y, %I:%M %p')}"] , axis=1
                        )
                        
                        st.session_state.contacts_df = pd.concat([st.session_state.contacts_df, harmonized_df], ignore_index=True)
                        st.success(f"Successfully loaded {len(harmonized_df)} contacts from the template!")
                        st.rerun()
                    else:
                        st.error("Uploaded template contains rows with missing essential information (Name, Designation, Country, Company). Please fill these fields.")

                except Exception as e:
                    st.error(f"Error reading file: {e}")
                    st.info("Please ensure your template is correctly filled and saved as .xlsx or .csv.")


# --- 5. Search and Filter Functionality ---
def search_and_filter(selected_category):
    st.sidebar.title("Other Filters")
    search_query = st.sidebar.text_input("Search (any field)")

    show_inactive = st.sidebar.checkbox("Show Inactive Contacts", value=False)

    all_designations = sorted(st.session_state.contacts_df["Designation"].dropna().unique().tolist())
    all_countries = sorted(st.session_state.contacts_df["Country"].dropna().unique().tolist())
    all_companies = sorted(st.session_state.contacts_df["Company"].dropna().unique().tolist())
    all_tierings = ["A", "B", "C", "Untiered"]
    all_golf_options = ["Yes", "No"]

    # Get all unique reception options from data
    all_reception_options = []
    # Iterate through each contact's 'Reception' string and split by comma
    for reception_str in st.session_state.contacts_df["Reception"].dropna().unique():
        all_reception_options.extend([r.strip() for r in str(reception_str).split(',') if r.strip()])
    all_reception_options = sorted(list(set(all_reception_options))) # Get unique and sort

    # Get all unique festivities options from data
    all_festivities_options = []
    # Iterate through each contact's 'Festivities' string and split by comma
    for festivity_str in st.session_state.contacts_df["Festivities"].dropna().unique():
        all_festivities_options.extend([f.strip() for f in str(festivity_str).split(',') if f.strip()])
    all_festivities_options = sorted(list(set(all_festivities_options))) # Get unique and sort


    selected_designations = st.sidebar.multiselect("Designation", options=all_designations, default=[])
    selected_countries = st.sidebar.multiselect("Country", options=all_countries, default=[])
    selected_companies = st.sidebar.multiselect("Company", options=all_companies, default=[])
    selected_tierings = st.sidebar.multiselect("Tiering", options=all_tierings, default=[])
    selected_golf = st.sidebar.multiselect("Golf", options=all_golf_options, default=[])
    
    # New filters for Reception and Festivities
    selected_reception = st.sidebar.multiselect("Reception", options=all_reception_options, default=[])
    selected_festivities = st.sidebar.multiselect("Festivities", options=all_festivities_options, default=[])


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

    filtered_df = filtered_df.sort_values(by="Name", ascending=True)
    return filtered_df

# --- 6. Main App Logic ---
def main():
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
            # Updated category_options for buttons - 'N/A' removed
            category_options = ["All", "Local Rep", "Overseas Rep", "Chief", "ID"]
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

            # Manual Add Contact button (moved below admin actions for better flow)
            if st.sidebar.button("Add New Contact (Manual)"):
                st.session_state.show_add_form = True
                st.rerun()

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