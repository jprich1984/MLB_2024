from  selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import pandas as pd
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def main():

    url = 'https://www.fangraphs.com/roster-resource/opening-day-tracker'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    webdriver_service = Service(ChromeDriverManager().install())
    webdriver_service.start()

    # initialize Driver
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    D={'Name':[],'Team':[],'Pos':[], "Status":[]} #Dictionary where we will insert the data from the website.
    driver.get(url)
    entry='div.table-page-control:nth-child(2) > input:nth-child(3)'
    first=True
    for i in range(1,22):
        if not first:
            try:
                WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, entry))).clear()
                WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, entry))).send_keys(i)
                time.sleep(1)
            except:
                print('it did not work')
                df = pd.DataFrame(D)
                df.to_csv('PlayerTeams_first'+str(i)+'rows'+'.csv')
        table = driver.find_elements(By.TAG_NAME, 'tr')
        for element in table:
            E=element.find_elements(By.TAG_NAME,'td')
            try:
                team=E[0].text
                name=E[1].text
                pos=E[2].text
                status=E[8].text
                print("pos: ", pos, "team: ", team, "Name: ", name, "status: ", status)
                D['Team'].append(team)
                D['Pos'].append(pos)
                D['Name'].append(name)
                D['Status'].append(status)
            except:
                print("Something failed")
        first=False
    driver.quit()
    print(D)
    df=pd.DataFrame(D)
    df=df[df['Team']!=""]
    print(len(df))
    df=df.drop_duplicates()
    print(len(df))
    df.to_csv('data/PlayerTeamsAll.csv')


if __name__=='__main__':
    main()
