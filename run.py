import streamlit as st
import json
import httpx
from PIL import Image
from io import BytesIO
import time
import certifi
import os
from fpdf import FPDF
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. HTTP CLIENT SETUP
# -----------------------------------------------------------------------------
client = httpx.Client(
    verify=certifi.where(),
    headers={
        "x-ig-app-id": "936619743392459",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
    }
)

# -----------------------------------------------------------------------------
# 2. DATA SCRAPING FUNCTION
# -----------------------------------------------------------------------------
@st.cache_data
def scrape_user(username: str):
    """Scrape Instagram user's data and extract relevant info, fetching only image posts."""
    error_message = None
    user_info = {}
    images = []

    try:
        result = client.get(f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}")

        if result.status_code != 200:
            error_message = f"Failed to retrieve data for user {username}. Status code: {result.status_code}"
            return error_message, user_info, images

        try:
            data = json.loads(result.content)
        except json.JSONDecodeError:
            error_message = "Error decoding JSON response from the server."
            return error_message, user_info, images

        user_info_raw = data.get("data", {}).get("user", {})
        if not user_info_raw:
            error_message = "User not found or unable to retrieve data."
            return error_message, user_info, images

        is_private = user_info_raw.get("is_private", False)

        user_info = {
            "Username": user_info_raw.get("username", "N/A"),
            "Full Name": user_info_raw.get("full_name", "N/A"),
            "ID": user_info_raw.get("id", "N/A"),
            "Category": user_info_raw.get("category_name", "N/A"),
            "Business Category": user_info_raw.get("business_category_name", "N/A"),
            "Phone": user_info_raw.get("business_phone_number", "N/A"),
            "Email": user_info_raw.get("business_email", "N/A"),
            "Biography": user_info_raw.get("biography", "N/A"),
            "Bio Links": [link.get("url") for link in user_info_raw.get("bio_links", []) if link.get("url")],
            "Homepage": user_info_raw.get("external_url", "N/A"),
            "Followers": f"{user_info_raw.get('edge_followed_by', {}).get('count', 0):,}",
            "Following": f"{user_info_raw.get('edge_follow', {}).get('count', 0):,}",
            "Facebook ID": user_info_raw.get("fbid", "N/A"),
            "Is Private": is_private,
            "Is Verified": user_info_raw.get("is_verified", "N/A"),
            "Profile Image": user_info_raw.get("profile_pic_url_hd", "N/A"),
            "Video Count": user_info_raw.get("edge_felix_video_timeline", {}).get("count", 0),
            "Image Count": user_info_raw.get("edge_owner_to_timeline_media", {}).get("count", 0),
            "Saved Count": user_info_raw.get("edge_saved_media", {}).get("count", 0),
            "Collections Count": user_info_raw.get("edge_saved_media", {}).get("count", 0),
            "Related Profiles": [profile.get("node", {}).get("username", "N/A") for profile in user_info_raw.get("edge_related_profiles", {}).get("edges", [])],
        }

        if is_private:
            error_message = f"Account '{username}' is private. Cannot fetch posts."
            return error_message, user_info, images

        media_edges = user_info_raw.get("edge_owner_to_timeline_media", {}).get("edges", [])

        for media_edge in media_edges:
            node = media_edge.get("node", {})
            if not node:
                continue

            if not node.get("is_video", False):
                
                # Safer Caption Logic
                caption_data = node.get("edge_media_to_caption")
                caption_edges = caption_data.get("edges", []) if caption_data else []
                
                if caption_edges:
                    first_caption_node = caption_edges[0].get("node")
                    caption_text = first_caption_node.get("text", "N/A") if first_caption_node else "N/A"
                else:
                    caption_text = "N/A"

                # Safer Location Logic
                location_data = node.get("location")
                location_name = location_data.get("name", "N/A") if location_data else "N/A"

                post_data = {
                    "ID": node.get("id", "N/A"),
                    "Shortcode": node.get("shortcode", "N/A"),
                    "Display URL": node.get("display_url", "N/A"),
                    "Thumbnail": node.get("thumbnail_src", "N/A"),
                    "Caption": caption_text,
                    "Comments Count": node.get("edge_media_to_comment", {}).get("count", 0),
                    "Likes": node.get("edge_liked_by", {}).get("count", 0),
                    "Taken At": node.get("taken_at_timestamp", "N/A"),
                    "Location": location_name,
                    "Accessibility Caption": node.get("accessibility_caption", "N/A"),
                }
                images.append(post_data)

        return error_message, user_info, images
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        return error_message, user_info, images

# -----------------------------------------------------------------------------
# 3. PDF EVIDENCE REPORT FUNCTION
# -----------------------------------------------------------------------------
def create_evidence_report(user_info, images):
    """Generates a formal PDF report for investigative purposes."""
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def safe_text(text):
        """Encodes text to latin-1 to prevent FPDF errors with special characters."""
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    # --- Report Header ---
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 10, "CONFIDENTIAL: Digital Profile Report", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Report Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(10)

    # --- Subject Information ---
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "I. Subject Profile Details", ln=True)
    pdf.set_font("Arial", size=11)
    
    report_details = {
        "Username": user_info.get('Username'),
        "Full Name": user_info.get('Full Name'),
        "User ID": user_info.get('ID'),
        "Facebook ID": user_info.get('Facebook ID'),
        "Biography": user_info.get('Biography'),
        "Followers": user_info.get('Followers'),
        "Following": user_info.get('Following'),
        "Contact Phone": user_info.get('Phone'),
        "Contact Email": user_info.get('Email'),
        "External Homepage": user_info.get('Homepage'),
        "Is Private": user_info.get('Is Private'),
        "Is Verified": user_info.get('Is Verified'),
        "Total Posts": user_info.get('Image Count')
    }

    for key, value in report_details.items():
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(45, 8, safe_text(key) + ":")
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, safe_text(value), ln=True)
    
    pdf.ln(5)

    # --- Media / Post Evidence ---
    if not images:
        # If no images, just return the PDF with the user info
        return bytes(pdf.output(dest='S')) 

    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "II. Recent Post Analysis (Images)", ln=True)
    pdf.ln(5)

    for i, post in enumerate(images):
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, f"Evidence Item #{i+1} (Post ID: {safe_text(post.get('ID'))})", ln=True)
        pdf.set_font("Arial", size=11)
        
        post_url = f"https://www.instagram.com/p/{post.get('Shortcode')}/"
        pdf.set_font("Arial", 'U', 11)
        pdf.set_text_color(0, 0, 255)
        pdf.cell(0, 6, safe_text(post_url), ln=True, link=post_url)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=11)
        
        post_details = {
            "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(post.get('Taken At'))) if post.get('Taken At') != 'N/A' else 'N/A',
            "Location": post.get('Location', 'N/A'),
            "Likes Count": f"{post.get('Likes', 0):,}",
            "Comments Count": f"{post.get('Comments Count', 0):,}",
        }
        
        for key, value in post_details.items():
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(40, 6, f"  {safe_text(key)}:")
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 6, safe_text(value), ln=True)
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(40, 6, "  Caption:")
        pdf.set_font("Arial", 'I', 10) # Italic for caption
        pdf.multi_cell(0, 6, f'"{safe_text(post.get("Caption", ""))}"', ln=True)
        
        pdf.ln(3)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y()) # Separator
        pdf.ln(5)

    # Return the PDF as a byte string
    return bytes(pdf.output(dest='S'))


# -----------------------------------------------------------------------------
# 4. STREAMLIT DISPLAY FUNCTIONS
# -----------------------------------------------------------------------------
def display_user_info(user_info):
    """Display the user's information."""
    st.subheader("User Information")
    if isinstance(user_info, str):
        st.error(user_info)
        return
    else:
        with st.container():
            col1, col2 = st.columns([2, 3])
            with col1:
                st.write(f"**Username:** {user_info.get('Username')}")
                st.write(f"**Full Name:** {user_info.get('Full Name')}")
                st.write(f"**ID:** {user_info.get('ID')}")
                st.write(f"**Category:** {user_info.get('Category')}")
                st.write(f"**Business Category:** {user_info.get('Business Category')}")
                st.write(f"**Phone:** {user_info.get('Phone')}")
                st.write(f"**Email:** {user_info.get('Email')}")
                st.write(f"**Biography:** {user_info.get('Biography')}")
                st.write(f"**Bio Links:** {', '.join([f'[Link]({url})' for url in user_info.get('Bio Links', [])])}")
                st.write(f"**Homepage:** [Homepage Link]({user_info.get('Homepage')})")
                st.write(f"**Followers:** {user_info.get('Followers')}")
                st.write(f"**Following:** {user_info.get('Following')}")
                st.write(f"**Facebook ID:** {user_info.get('Facebook ID')}")
                st.write(f"**Private Account:** {'Yes' if user_info.get('Is Private') else 'No'}")
                st.write(f"**Verified Account:** {'Yes' if user_info.get('Is Verified') else 'No'}")
                st.write(f"**Video Count:** {user_info.get('Video Count')}")
                st.write(f"**Image Count:** {user_info.get('Image Count')}")
                st.write(f"**Saved Count:** {user_info.get('Saved Count')}")
                st.write(f"**Collections Count:** {user_info.get('Collections Count')}")
                st.write(f"**Related Profiles:** {', '.join(user_info.get('Related Profiles', []))}")

            with col2:
                if user_info.get('Profile Image'):
                    try:
                        response = client.get(user_info.get('Profile Image'))
                        img = Image.open(BytesIO(response.content))
                        st.image(img, caption="Profile Picture", use_column_width=True)
                    except Exception as e:
                        st.error(f"Error loading profile image: {e}")
            
        st.markdown("---") # Visual separator


def display_media(media_list, media_type):
    """Display user's media (images)."""
    st.subheader(f"{media_type.capitalize()}s")

    if not media_list:
        st.write(f"No {media_type}s found.")
        return

    sort_by_key = f"sort_by_{media_type}"
    thumbnail_size_key = f"thumbnail_size_{media_type}"

    sort_by = st.selectbox(f"Sort {media_type}s by:", ["Likes", "Comments", "Date"], key=sort_by_key)

    if sort_by == "Likes":
        media_list = sorted(media_list, key=lambda x: x.get('Likes', 0), reverse=True)
    elif sort_by == "Comments":
        media_list = sorted(media_list, key=lambda x: x.get('Comments Count', 0), reverse=True)
    elif sort_by == "Date":
        media_list = sorted(media_list, key=lambda x: x.get('Taken At', 0), reverse=True)

    thumbnail_size = st.radio("Thumbnail Size:", ["Small", "Large"], key=thumbnail_size_key, horizontal=True)

    for i, media in enumerate(media_list):
        with st.expander(f"{media_type.capitalize()} {media.get('ID')} (Likes: {media.get('Likes',0):,})"):
            st.write(f"**Caption:** {media.get('Caption')}")
            st.write(f"**Shortcode:** {media.get('Shortcode')}")
            st.write(f"**Likes:** {media.get('Likes'):,}")
            st.write(f"**Comments:** {media.get('Comments Count'):,}")
            st.write(f"**Location:** {media.get('Location')}")
            if media.get('Taken At') != 'N/A':
                st.write(f"**Taken At:** {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(media.get('Taken At')))}")
            else:
                st.write(f"**Taken At:** N/A")

            if media.get("Display URL"):
                if thumbnail_size == "Small":
                    st.image(media.get("Display URL"), width=150)
                else:
                    st.image(media.get("Display URL"), width=300)
            else:
                st.write("No image URL available.")

            st.write(f"**Accessibility Caption:** {media.get('Accessibility Caption')}")
            
    json_data = json.dumps(media_list, indent=4, default=str) # Added default=str for safety
    st.download_button("Download Raw Media Data (JSON)", json_data, file_name=f"{media_type}_data.json", mime="application/json")


# -----------------------------------------------------------------------------
# 5. MAIN APPLICATION
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="TRACKGRAM", layout="wide")
    st.title("TRACKGRAM")
    
    st.write("Enter an Instagram username to scrape public profile information and image posts for documentation.")

    username = st.text_input("Enter Target Username", placeholder="e.g., target_username", key="username_input")

    if st.button("Analyze and Generate Report", key="scrape_button"):
        if username:
            with st.spinner(f"Analyzing profile: {username}..."):
                error_message, user_info, images = scrape_user(username)

            if error_message:
                st.error(error_message)
                if user_info and user_info.get("Is Private"):
                    display_user_info(user_info)
                else:
                    st.warning("No user information or images to display due to the error.")
            else:
                st.success(f"Analysis complete for {username}!")
                st.markdown("---")
                
                display_user_info(user_info)
                display_media(images, "image")

                st.markdown("---")
                st.subheader("Generate Formal Report")
                st.write("Click the button below to download all findings as a formal PDF document.")

                pdf_bytes = create_evidence_report(user_info, images)
                
                st.download_button(
                    label="Download PDF Evidence Report",
                    data=pdf_bytes,
                    file_name=f"{username}_evidence_report.pdf",
                    mime="application/pdf"
                )

        else:
            st.error("Please enter a username to analyze.")

if __name__ == "__main__":
    main()