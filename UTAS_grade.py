from time import sleep

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


class UTAS_grade:
    def __init__(self,browser,student_number,password):
        self.browser = browser
        self.student_number = student_number
        self.password = password

    def get_tables(self):
        if self.browser == 'Chrome':
            options = webdriver.ChromeOptions()
            driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
        elif self.browser == 'Firefox':
            options = webdriver.FirefoxOptions()
            driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
        else:
            raise ValueError("browser must be either Chrome or Firefox")
        # without opening a browser
        # options.add_argument('--headless')

        url = 'https://utas.adm.u-tokyo.ac.jp/campusweb/campusportal.do'
        driver.get(url)
        sleep(1)

        elem_login_btn1 = driver.find_elements_by_class_name('ui-button')
        elem_login_btn1[2].click()
        sleep(2)

        driver.find_element(By.ID,'userNameInput').send_keys(self.student_number)
        driver.find_element(By.ID,'passwordInput').send_keys(self.password)
        sleep(2)

        driver.find_element(By.ID,'submitButton').click()
        sleep(2)

        driver.find_element(By.ID,'tab-si').click()
        sleep(2)

        iframe = driver.find_element(By.ID,'main-frame-if')
        driver.switch_to.frame(iframe)

        btns = driver.find_elements(By.XPATH,"//*[contains(@id, 'shozokuCd')]")
        for btn in btns:
            btn.click()
        sleep(2)

        driver.find_element(By.XPATH,"//*[@id='rishuSeisekiReferListForm']/table/tfoot/tr/td/input[1]").click()
        sleep(1)

        driver.switch_to.default_content()
        sleep(1)

        iframe = driver.find_element(By.ID,'main-frame-if')
        driver.switch_to.frame(iframe)

        res = driver.page_source


        soup = BeautifulSoup(res, "html.parser")

        tables = soup.find_all('table')

        self.dfs = []

        for table in tables:
            head = table.find('thead')
            body = table.find('tbody')

            if head == None:
                continue
            else:
                pass

            head_row = head.find_all('th', {'class':'seiseki-head'})
            body_rows = body.find_all('tr')

            if len(head_row) < 9:# magic number
                continue
            else:
                pass

            if len(body_rows) < 5:# magic number
                continue
            else:
                pass

            columns = [head_row[i].text for i in range(9)]

            df = pd.DataFrame(columns=columns)

            for i in range(len(body_rows)):
                tds = body_rows[i].find_all('td')

                if len(tds) < 9:# magic number
                    continue
                else:
                    pass

                values = [tds[i].text.replace(' ','').replace('\n','') for i in range(9)]
                df = pd.concat([df, pd.DataFrame([pd.Series(values, index=columns)])], ignore_index= True)

            self.dfs.append(df)

        driver.switch_to.default_content()
        driver.quit()

    def print_results(self):
        for df in self.dfs:
            df['単位数'] = df['単位数'].astype(float)

        self.grades = []

        for df in self.dfs:
            huka = df[df['評語'] == "不可"]
            ka = df[df['評語'] == "可"]
            ryo = df[df['評語'] == "良"]
            yu = df[df['評語'] == "優"]
            yujo = df[df['評語'] == "優上"]

            nhuka = huka['単位数'].sum()
            nka = ka['単位数'].sum()
            nryo = ryo['単位数'].sum()
            nyu = yu['単位数'].sum()
            nyujo = yujo['単位数'].sum()

            total = nhuka + nka + nryo + nyu + nyujo

            self.grades.append([nhuka,nka,nryo,nyu,nyujo])

        for i,grade in enumerate(self.grades):
            print(f"{i}-th table")
            print(f"不可 {grade[0]}: 可: {grade[1]}, 良: {grade[2]}, 優: {grade[3]}, 優上: {grade[4]}, 合計: {sum(grade)}")
            print("--------------------------------------------------------------------------------")