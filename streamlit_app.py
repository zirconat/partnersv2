import streamlit as st
import pandas as pd
from datetime import datetime, date
from PIL import Image
import io
import base64
from pathlib import Path
import os

# --- MUST BE THE FIRST STREAMLIT COMMAND ---
st.set_page_config(layout="wide", page_title="Contact Card App 📞")

# --- 0. Data Initialization and Session State Management ---
if 'contacts_df' not in st.session_state:
    st.session_state.contacts_df = pd.DataFrame(
        columns=[
            "Name", "Designation", "Country", "Company", "Phone Number",
            "Office Number", "Posting Date", "Deposted Date","Office Address", "Home Address", "Hobbies",
            "Dietary Restrictions", "Festivities", "Vehicle", "Golf", "Golf Handicap",
            "Reception", "Status", "Tiering", "Category", "Photo",
            "Last Updated By", "Last Updated On", "History"
        ]
    )
    # Updated 'Category' to initial data
    st.session_state.contacts_df.loc[0] = [
        "Albert", "SC", "Australia", "CompanyA", "98765432",
        "9876544321", date(2025, 8, 12), None, "123 bsdlk slhf", "456 Home Rd, Perth", "sleeping",
        "NIL", "Deepavali", "s1234cd", "Yes", "20",
        "NYR, ALSE", "Active", "A", "Local Rep", None, # Changed to "Local Rep"
        "System", datetime.now().strftime("%d %b %y, %I:%M %p"), []
    ]
    st.session_state.contacts_df.loc[1] = [
        "Bob The Builder", "Project Manager", "Canada", "BuildCo","987-654-3210",
        "654-321-0987", date(2025, 8, 12), None, "789 Construction Blvd, Toronto", "101 Maple Lane, Toronto", "Gardening, Cycling",
        "None", "Canada Day", "s1234cd", "Yes", "20",
        "Client Meeting", "Active", "B", "Overseas Rep", None, # Changed to "Overseas Rep"
        "System", datetime.now().strftime("%d %b %y, %I:%M %p"), []
    ]
    st.session_state.contacts_df.loc[2] = [
        "Charlie Chaplin", "Actor", "UK", "Comedy Gold Studios", "555-123-4567",
        "555-987-6543", date(2025, 8, 12), None, "Studio 5, London", "1 Baker Street, London", "Filmmaking, Chess",
        "Vegan", "Halloween", "s1234cd", "Yes", "20",
        "Film Premiere", "Inactive", "C", "Chief", None,
        "System", datetime.now().strftime("%d %b %y, %I:%M %p"), []
    ]
    st.session_state.contacts_df.loc[3] = [
        "David Lee", "Engineer", "Singapore", "TechCorp", "65123456",
        "65789012", date(2024, 1, 15), None, "Science Park Dr", "Holland Village", "Hiking",
        "Gluten-free", "Chinese New Year", "sedan", "No", "N/A",
        "Project Review", "Active", "A", "ID", None, # Changed to "ID"
        "System", datetime.now().strftime("%d %b %y, %I:%M %p"), []
    ]
    st.session_state.contacts_df.loc[4] = [
        "Eve Adams", "CEO", "USA", "Global Solutions", "123-456-7890",
        "987-654-3210", date(2023, 10, 20), None, "Wall Street, NYC", "5th Avenue, NYC", "Reading, Yoga",
        "None", "Thanksgiving", "SUV", "Yes", "15",
        "Board Meeting", "Active", "A", "Chief", None,
        "System", datetime.now().strftime("%d %b %y, %I:%M %p"), []
    ]


# --- IMPORTANT: Ensure 'Category' column exists in existing DataFrame ---
if 'contacts_df' in st.session_state and 'Category' not in st.session_state.contacts_df.columns:
    st.session_state.contacts_df['Category'] = "N/A"

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

# --- 2. Contact Card Display and Editing ---
def edit_contact_form(contact, index):
    st.markdown("<h4>Edit Contact</h4>", unsafe_allow_html=True)
    with st.form(key=f"edit_form_{index}"):
        name = st.text_input("Name*", value=contact["Name"], key=f"edit_name_{index}")
        designation = st.text_input("Designation*", value=contact["Designation"], key=f"edit_designation_{index}")
        country = st.text_input("Country*", value=contact["Country"], key=f"edit_country_{index}")
        company = st.text_input("Company*", value=contact["Company"], key=f"edit_company_{index}")
        phone_number = st.text_input("Phone Number", value=contact["Phone Number"], key=f"edit_phone_number_{index}")
        office_number = st.text_input("Office Number", value=contact["Office Number"], key=f"edit_office_number_{index}")

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
        festivities = st.text_input("Festivities", value=contact["Festivities"], key=f"edit_festivities_{index}")
        vehicle = st.text_input("Vehicle", value=contact["Vehicle"], key=f"edit_vehicle_{index}")

        # Golf selection field
        golf = st.selectbox("Golf",["Yes", "No"], index=0 if contact["Golf"] == "Yes" else 1, key=f"edit_golf_{index}")

        # Conditional display of Golf Handicap
        golf_handicap_value = contact["Golf Handicap"] if contact["Golf"] == "Yes" else "N/A" # Preserve existing value if Yes, else set to N/A
        if golf == "Yes":
            handicap = st.text_input("Golf Handicap", value=golf_handicap_value, key=f"edit_golf_handicap_{index}")
        else:
            handicap = "N/A" # Set handicap to N/A if Golf is No


        reception = st.text_input("Reception", value=contact["Reception"], key=f"edit_reception_{index}")
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
                    if isinstance(old_val, (datetime, date)):
                        old_val_str = old_val.strftime("%Y-%m-%d") if old_val else "N/A"
                    else:
                        old_val_str = str(old_val) if pd.notna(old_val) and old_val != 'N/A' else "N/A"

                    if isinstance(new_val, (datetime, date)):
                        new_val_str = new_val.strftime("%Y-%m-%d") if new_val else "N/A"
                    else:
                        new_val_str = str(new_val) if pd.notna(new_val) and new_val != 'N/A' else "N/A"

                    if old_val_str != new_val_str:
                        changes.append(f"{field_name} changed from '{old_val_str}' to '{new_val_str}'")
                        return new_val
                    return old_val

                updated_contact["Name"] = track_change("Name", contact["Name"], name)
                updated_contact["Designation"] = track_change("Designation", contact["Designation"], designation)
                updated_contact["Country"] = track_change("Country", contact["Country"], country)
                updated_contact["Company"] = track_change("Company", contact["Company"], company)
                updated_contact["Phone Number"] = track_change("Phone Number", contact["Phone Number"], phone_number)
                updated_contact["Office Number"] = track_change("Office Number", contact["Office Number"], office_number)
                updated_contact["Posting Date"] = track_change("Posting Date", contact["Posting Date"], posting_date)
                updated_contact["Deposted Date"] = track_change("Deposted Date", contact["Deposted Date"], deposted_date)
                updated_contact["Office Address"] = track_change("Office Address", contact["Office Address"], office_address)
                updated_contact["Home Address"] = track_change("Home Address", contact["Home Address"], home_address)
                updated_contact["Hobbies"] = track_change("Hobbies", contact["Hobbies"], hobbies)
                updated_contact["Dietary Restrictions"] = track_change("Dietary Restrictions", contact["Dietary Restrictions"], dietary_restrictions)
                updated_contact["Festivities"] = track_change("Festivities", contact["Festivities"], festivities)
                updated_contact["Vehicle"] = track_change("Vehicle", contact["Vehicle"], vehicle)
                updated_contact["Golf"] = track_change("Golf", contact["Golf"], golf)
                updated_contact["Golf Handicap"] = track_change("Golf Handicap", contact["Golf Handicap"], handicap)
                updated_contact["Reception"] = track_change("Reception", contact["Reception"], reception)
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
                    update_info = (f"Updated by {st.session_state.user_role} at {datetime.now().strftime('%d %b %y, %I:%M %p')}.<br>"
                                   + "<br>".join(changes))
                    updated_contact["Last Updated By"] = st.session_state.user_role
                    updated_contact["Last Updated On"] = datetime.now().strftime("%d %b %y, %I:%M %p")
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
            st.markdown(
                f"""
                <div style="border-radius: 10px; border: 1px solid #ccc; padding: 15px; background-color: #f9f9f9;">
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <img src="data:image/png;base64,{image_base64}" style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover;">
                        <div style="flex: 1;">
                            <h3 style="margin: 0; font-size: 20px; color: #555;">
                                {contact['Name']}
                            </h3>
                            <i><h4 style="margin: 0; font-size: 16px; color: #555;">
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
                            <b>Category:</b> {contact['Category']}
                        </div>
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 15px;">
                        <div style="flex: 1; min-width: 150px; color: #555">
                            <p><b>Country:</b> {contact['Country']}</p>
                            <p><b>Phone Number.:</b> {contact['Phone Number']}</p>
                            <p><b>Office Number.:</b> {contact['Office Number']}</p>
                            <p><b>Vehicle(s):</b> {contact['Vehicle']}</p>
                            <p><b>Address:</b> {contact['Office Address']}</p>
                        </div>
                        <div style="flex: 1; min-width: 150px; color: #555">
                            <p><b>Posting Date:</b> {formatted_posting_date}</p>
                            <p><b>De-posted Date:</b> {formatted_deposted_date}</p>
                            <p><b>Golf:</b> {contact['Golf']}</p>
                            <p><b>Golf Handicap:</b> {contact['Golf Handicap']}</p>
                        </div>
                        <div style="flex: 1; min-width: 150px; color: #555">
                            <p><b>Dietary Restrictions:</b> {contact['Dietary Restrictions']}</p>
                            <p><b>Reception:</b> {contact['Reception']}</p>
                            <p><b>Festivity:</b> {contact['Festivities']}</p>
                        </div>
                        <div style="flex: 1; min-width: 150px; color: #555">
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
        country = st.text_input("Country*")
        company = st.text_input("Company*")
        phone_number = st.text_input("Phone Number")
        office_number = st.text_input("Office Number")
        posting_date = st.date_input("Posting Date", value=datetime.today().date())
        deposted_date = st.date_input("De-posted Date", value=None)
        office_address = st.text_area("Office Address")
        home_address = st.text_area("Home Address")
        hobbies = st.text_input("Hobbies")
        dietary_restrictions = st.text_input("Dietary Restrictions")
        festivities = st.text_input("Festivities")
        reception = st.text_input("Reception")
        vehicle = st.text_input("Vehicle")

        # Golf selection field
        golf = st.selectbox("Golf", ["Yes", "No"], index=1) # Default to No

        # Conditional display of Golf Handicap
        golf_handicap = "N/A" # Initialize
        if golf == "Yes":
            golf_handicap = st.text_input("Golf Handicap") # This will be empty if new contact
        else:
            golf_handicap = "N/A" # Ensure it's N/A if Golf is No


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
                    "Posting Date": posting_date,
                    "Deposted Date": deposted_date,
                    "Office Address": office_address,
                    "Home Address": home_address,
                    "Hobbies": hobbies,
                    "Dietary Restrictions": dietary_restrictions,
                    "Festivities": festivities,
                    "Vehicle": vehicle,
                    "Golf": golf,
                    "Golf Handicap": golf_handicap, # Use the conditionally set handicap
                    "Reception": reception,
                    "Status": status,
                    "Tiering": tiering,
                    "Category": category,
                    "Photo": new_profile_pic_bytes,
                    "Last Updated By": st.session_state.user_role if st.session_state.user_role else "Unknown",
                    "Last Updated On": datetime.now().strftime("%d %b %y, %I:%M %p"),
                    "History": [f"Created by {st.session_state.user_role if st.session_state.user_role else 'Unknown'} at {datetime.now().strftime('%d %b %y, %I:%M %p')}"]
                }
                st.session_state.contacts_df = pd.concat([st.session_state.contacts_df, pd.DataFrame([new_contact])], ignore_index=True)
                st.sidebar.success("Contact added successfully!")
                st.session_state.show_add_form = False
                st.rerun()
            else:
                st.sidebar.error("Please fill in all required fields (Name, Designation, Country, Company).")

# --- 3. Search and Filter Functionality ---
def search_and_filter(selected_category):
    st.sidebar.title("Other Filters")
    search_query = st.sidebar.text_input("Search (any field)")

    show_inactive = st.sidebar.checkbox("Show Inactive Contacts", value=False)

    all_designations = sorted(st.session_state.contacts_df["Designation"].dropna().unique().tolist())
    all_countries = sorted(st.session_state.contacts_df["Country"].dropna().unique().tolist())
    all_companies = sorted(st.session_state.contacts_df["Company"].dropna().unique().tolist())
    all_tierings = ["A", "B", "C", "Untiered"]
    all_golf_options = ["Yes", "No"]

    selected_designations = st.sidebar.multiselect("Designation", options=all_designations, default=[])
    selected_countries = st.sidebar.multiselect("Country", options=all_countries, default=[])
    selected_companies = st.sidebar.multiselect("Company", options=all_companies, default=[])
    selected_tierings = st.sidebar.multiselect("Tiering", options=all_tierings, default=[])
    selected_golf = st.sidebar.multiselect("Golf", options=all_golf_options, default=[])

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


    if search_query:
        search_query_lower = search_query.lower()
        mask = filtered_df.drop(columns=["Photo"], errors='ignore').apply(
            lambda row: row.astype(str).str.lower().str.contains(search_query_lower, na=False).any(), axis=1
        )
        filtered_df = filtered_df[mask]

    filtered_df = filtered_df.sort_values(by="Name", ascending=True)
    return filtered_df

# --- 4. Admin Download Functionality ---
def download_csv():
    if st.session_state.user_role == "admin":
        st.sidebar.markdown("---")
        st.sidebar.title("Admin Actions")

        df_for_download = st.session_state.contacts_df.copy()

        for col in ["Posting Date", "Deposted Date"]:
            if col in df_for_download.columns:
                df_for_download[col] = df_for_download[col].apply(
                    lambda x: x.strftime("%Y-%m-%d") if isinstance(x, (datetime, date)) else ""
                )

        # Convert list of history entries to a single string for CSV export
        # Each history entry will be on a new line within the cell
        df_for_download['History'] = df_for_download['History'].apply(
            lambda x: "\n".join(x) if isinstance(x, list) else ""
        )

        df_for_download['Profile Picture (Base64)'] = df_for_download['Photo'].apply(
            lambda x: base64.b64encode(x).decode('utf-8') if x is not None and isinstance(x, bytes) else ''
        )

        df_for_download = df_for_download.drop(columns=["Photo"], errors='ignore') # Removed "History" from drop list

        csv_export = df_for_download.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="Download Contact Data (CSV)",
            data=csv_export,
            file_name="contact_data_with_images_and_history.csv", # Changed filename
            mime="text/csv",
            help="Downloads all contact data, including Base64 encoded profile pictures and change history."
        )

# --- 5. Main App Logic ---
def main():
    if st.session_state.user_role is None:
        st.title("Welcome to the Contact Card App 👋")
        login()
    else:
        st.sidebar.write(f"Logged in as: **{st.session_state.user_role.capitalize()}**")
        logout()

        st.title("Contact Cards 📇")

        # --- Category Buttons on Main Page ---
        st.write("### Filter by Category:")
        # Updated category_options for buttons - 'N/A' removed
        category_options = ["All", "Local Rep", "Overseas Rep", "Chief", "ID"]
        cols = st.columns(len(category_options))

        for i, category_name in enumerate(category_options):
            with cols[i]:
                # Apply conditional styling for the selected button
                button_style = ""
                if category_name == st.session_state.selected_category_button:
                    button_style = "background-color: #6a0dad; color: white; border-color: #6a0dad;" # Highlight selected
                
                # Using markdown to create buttons with custom style
                if st.button(category_name, key=f"cat_btn_{category_name}"):
                    st.session_state.selected_category_button = category_name
                    st.rerun()
        st.markdown("---")


        if st.session_state.user_role == "admin":
            download_csv()

            if st.sidebar.button("Add New Contact"):
                st.session_state.show_add_form = True

            if st.session_state.show_add_form:
                add_new_contact_form()

        elif st.session_state.user_role == "user":
            if st.sidebar.button("Add New Contact"):
                st.session_state.show_add_form = True

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