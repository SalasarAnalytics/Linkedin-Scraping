import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import quote
import time
import os
from io import BytesIO

# Selenium setup function
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    service = Service('Z:\\chromedriver-win64\\chromedriver.exe')  # Path to your ChromeDriver
    return webdriver.Chrome(service=service, options=chrome_options)

# Google search function
def google_search(query, num_pages=5):
    driver = setup_driver()
    results_data = []  # List to store results
    
    for page in range(num_pages):
        # Navigate to Google search results page
        driver.get(f"https://www.google.com/search?hl=en&q={quote(query)}&start={page * 10}")
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'g'))
            )
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            results = soup.find_all('div', class_='g')
            
            for result in results:
                title = result.find('h3')
                link = result.find('a', href=True)
                if title and link:
                    results_data.append({'Title': title.text, 'Link': link['href']})
            
            time.sleep(2)  # To avoid rate limiting
            
        except Exception as e:
            st.error(f"Error occurred: {e}")
    
    driver.quit()
    return results_data  # Return the results data

# Streamlit App
st.title("Google Search Automation")
st.header("Search for Positions in Industries")

# User inputs
positions = st.text_area("Enter Position (One Role at a Time):")
industries = st.text_area("Enter Industries (separate each industry with a comma):")
num_pages = st.slider("Number of pages to search:", min_value=1, max_value=10, value=5)

if st.button("Run Search"):
    if positions.strip() and industries.strip():
        position_list = [pos.strip() for pos in positions.split(",")]
        industry_list = [ind.strip() for ind in industries.split(",")]
        
        # Iterate through each position and industry combination
        for position in position_list:
            with BytesIO() as output:
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for industry in industry_list:
                        query = f'site:linkedin.com/in/ ({position}) India ({industry})'
                        st.write(f"Searching for: **{position}** in **{industry}**")
                        
                        # Fetch search results
                        results_data = google_search(query, num_pages)
                        if results_data:
                            df = pd.DataFrame(results_data)
                            sheet_name = industry[:30]  # Limit sheet name to 30 characters
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Save the Excel file
                output.seek(0)
                st.download_button(
                    label=f"Download Results for {position}",
                    data=output,
                    file_name=f"{position.replace(' ', '_')}_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.warning("Please enter both positions and industries.")

