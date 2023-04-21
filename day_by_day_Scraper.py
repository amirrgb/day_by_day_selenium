import time
import mysql.connector
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.service import Service
from datetime import datetime
from datetime import timedelta
faceMatchTable="face_matches"
filePaths="D://python/SofaWorker/Include/allLeaguesOfEveryDay"
executablePath=("D://python/sofaWorker/Include/chromeDriver/chromeDriver.exe")


def workOption(option):  # chromeDriverOptions
    option.add_argument("--start-maximized")
    option.add_argument("disable-infobars")
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("--disable-gpu")
    option.add_argument("--no-sandbox")
    option.add_experimental_option('excludeSwitches', ['enable-logging'])
    chromePrefers = {}
    option.experimental_options["prefs"] = chromePrefers
    chromePrefers["profile.default_content_settings"] = {"images": 2}
    # chromePrefers["profile.managed_default_content_settings"] = {"images": 2}
    return option


def isMatchForMenAndAdults(text):
    lines = text.splitlines()
    if "Women" in text:
        return 0
    if "U17" in text or "U19" in text or "U21" in text or "U22" in text or "U23" in text:
        return 0
    if ("France" in lines[0]) and ("National 2" in lines[1]):
        return 0
    if ("Germany" in lines[0]) and ("Junioren" in lines[1]):
        return 0
    if ("England" in lines[0]) and ("Premier League Cup" in lines[1]):
        return 0
    if ("England" in lines[0]) and ("Premier League 2" in lines[1]):
        return 0
    if ("England" in lines[0]) and ("Northern Premier League" in lines[1]):
        return 0
    if ("England" in lines[0]) and ("Southern Football League" in lines[1]):
        return 0
    if ("Spain" in lines[0]) and ("Primera División Femenina" in lines[1]):
        return 0
    return 1


def isLeagueAlreadyPinned(pin_button_txt):
    if 'rotate(' in pin_button_txt:
        return 0
    elif 'translate' in pin_button_txt:
        return 1


def isLeagueMustBePinned(currentCountry, currentLeague, list_file):
    for i in list_file:
        fileCountry = i.split("<=>")[0]
        fileLeague = i.split("<=>")[1]
        if ((fileCountry in currentCountry) and (fileLeague in currentLeague)):
            return 1
    return 0


def pinner(mainPageLeagueAndCountry, list_file):
    mainPageLeagueAndCountryText = mainPageLeagueAndCountry.text
    try:
        pin_button = mainPageLeagueAndCountry.find_element(By.XPATH, './/button')
    except:
        pin_button = None
    if pin_button != None:
        pin_button_txt = pin_button.find_element(By.XPATH, './/*').get_attribute('innerHTML')
        lines = mainPageLeagueAndCountryText.splitlines()
        item = lines[0] + '<=>' + lines[1]
        if ((isLeagueMustBePinned(currentCountry=lines[0], currentLeague=lines[1], list_file=list_file)) and (not isLeagueAlreadyPinned(pin_button_txt))):
            if (isMatchForMenAndAdults(mainPageLeagueAndCountryText)):
                bool = True
                while (bool):
                    pin_button.click()
                    bool = False
                print(item + " >>> pinned")
                time.sleep(2)
        if (not isLeagueMustBePinned(lines[0], lines[1], list_file)) and (isLeagueAlreadyPinned(pin_button_txt)):
            bool = True
            while bool:
                pin_button.click()
                bool = False
            print(item + " >>> unpinned")
            time.sleep(2)
        elif (not isMatchForMenAndAdults(mainPageLeagueAndCountryText)) and (isLeagueAlreadyPinned(pin_button_txt)):
            bool = True
            while bool:
                pin_button.click()
                bool = False
            print(item + " >>> Exception Leagues unpinned")
            time.sleep(2)


def pagePin(driver, filePath):
    list_file = []
    screen = ''
    with open(filePath, 'r+', encoding="utf-8") as f:
        for j in f.readlines():
            list_file.append(j.strip())
    driver, screen = openAllMatch(driver)
    xCountries = '/html/body/div[1]/main/div/div[2]/div[1]/div[3]/div[2]/div/div[2]/div/div[@role="rowgroup"]//div[div[div[2][a[div]]]]'
    for j in range(0, int(screen / 420)):
        if j >= 1:
            driver = scrollDown(driver, 500)
        countries = driver.find_elements(By.XPATH, xCountries)
        if len(countries)==0:
            xCountries = '/html/body/div[1]/main/div/div[2]/div[1]/div[3]/div[2]/div/div[3]/div/div[@role="rowgroup"]//div[div[div[2][a[div]]]]'
            driver = scrollDown(driver,-1200)
        for h in range(len(countries)):
            for l in range(1, 3):
                try:
                    pinner(countries[h], list_file)
                except:
                    ""
    return driver


def oneDayPin(driver, url, filePath):
    b = True
    while (b):
        try:
            driver.refresh()
            time.sleep(2)
            driver.get(url)
            time.sleep(2)
            b = False
        except:
            b = True
    print("\nPinnig >>> %s\n" % url)
    pagePin(driver, filePath)
    return driver


#collecting


def openPinnedLeagues(driver):
    try:
        xPinnedLeagues = '/html/body/div[1]/main/div/div[2]/div[1]/div[3]/div[2]/div/div[1]/div[1]/div[1]/div[2]'
        pinnedLeagues = driver.find_element(By.XPATH, xPinnedLeagues)
        pinnedLeaguesHtml = pinnedLeagues.find_element(By.XPATH, './/*').get_attribute('innerHTML')
        if 'rotate(0deg)' in pinnedLeaguesHtml:
            pinnedLeagues.click()
            time.sleep(2)
    except:
        ''
    return driver


def date_namesSqlCheck(user, password, host, database, rowText):
    cnx = mysql.connector.connect(user=user,host=host, password=password,  database=database)
    con = cnx.cursor(buffered=True)
    v = rowText.splitlines()
    t1 = v[0].split('/')
    date=('20' + t1[2] + '-' + t1[1] + '-' + t1[0] )
    sql = ('SELECT *  FROM primary_references_data.%s WHERE  Date = "%s" and HomeTeam = "%s" and AwayTeam = "%s";' % (faceMatchTable,date,v[2], v[3]))
    con.execute(sql)
    for x in con:
        return 0
    return 1


def names_score_date_positionGetter(output, rowText):
    t = rowText.splitlines()
    t1 = t[0].split('/')
    output += '<=>' + t[2] + '<=>' + t[3] + '<=>' + t[4] + '<=>' + t[5] + '<=>20' + t1[2] + '-' + t1[1] + '-' + t1[0] + '<=>' + t[1]
    return output


def popupCheck(popupText, output):
    homeTeamName, awayTeamName = "zzzz", "zzzz"
    if (popupText != None):
        lines = popupText.splitlines()
        try:
            if 'Created' not in lines[0]:
                b = lines[2].split(" - ")
                homeTeamName, awayTeamName = b[0], b[1]
            elif 'Created' in lines[0]:
                b = lines[3].split(" - ")
                homeTeamName, awayTeamName = b[0], b[1]
        except:
            ""
    t = output.split("<=>")
    # t[2]=home_name
    if t[2] in homeTeamName:
        return 1
    elif t[3] in awayTeamName:
        return 1
    elif homeTeamName in t[2]:
        return 1
    elif awayTeamName in t[3]:
        return 1
    return 0


def country_leagueGetter(output, popupText):
    if (popupText != None):
        lines = popupText.splitlines()
        try:
            if 'Created' not in lines[0]:
                output += lines[0] + '<=>' + lines[1]
                return output
            elif 'Created' in lines[0]:
                output += lines[1] + '<=>' + lines[2]
                return output
        except:
            output += "null<=>null"
            return output


def pregameScoreCheck(pregameFormLines, output):
    time.sleep(1)
    firstLine = pregameFormLines[0].get_attribute('innerHTML')
    t = output.split("<=>")
    # t[2]=homeName
    if t[2] in firstLine:
        return 1
    elif t[3] in firstLine:
        return -1
    elif firstLine in t[2]:
        return 1
    elif firstLine in t[3]:
        return -1
    return 0


def pregameScoreGetter(output, pregameForm):
    if pregameForm is not None:
        pregameFormNames = pregameForm.find_elements(By.XPATH, './/div[2]/div[3]/div')
        pregameFormScores = pregameForm.find_elements(By.XPATH, './div//div/div[6]/div')
        if (len(pregameFormNames) >= 1):
            if (len(pregameFormScores) == 2):
                for i in range(2):
                    if (pregameScoreCheck(pregameFormNames, output) > 0):
                        for scores in pregameFormScores:
                            score = scores.get_attribute('innerHTML')
                            output += '<=>' + score
                        return output
                    elif (pregameScoreCheck(pregameFormNames, output) < 0):
                        for scores in reversed(pregameFormScores):
                            score = scores.get_attribute('innerHTML')
                            output += '<=>' + score
                        return output
                    time.sleep(2)
                else:
                    output += "<=>-1<=>-1"
                return output
    else:
        output += "<=>-1<=>-1"
        return output


def teamHrefGetter(output, teamsLink):
    for teamLink in teamsLink:
        link = teamLink.get_attribute('href')
        output += '<=>' + link
    return output


def collect(driver):
    counter = 1
    xRowGroup = '/html/body/div[1]/main/div/div[2]/div[1]/div[3]/div[2]/div/div[1]/div[1]/div[@id="pinned-list-fade-target"]/div/div/div[@role="rowgroup"]'
    xPopup = '/html/body/div[1]/main/div/div[2]/div[1]/div[5]'
    xPregameForm = '/html/body/div[1]/main/div/div[2]/div[1]/div[5]/div/div[1]/div/div[2]/div[2]/div/div//div[h3[text() = "Pregame form"]]'
    xTeamsLink = '/html/body/div[1]/main/div/div[2]/div[1]/div[5]/div/div[1]/div/div[1]/div[2]/div//a'
    driver, screen = openAllMatch(driver)
    driver = openPinnedLeagues(driver)
    for j in range(0, 60):
        if (counter >= 4):
            break
        if (j >= 1):  # scroll
            driver = scrollDown(driver, 330)
            counter += 1
        try:
            rowGroup = driver.find_element(By.XPATH, xRowGroup)
            print("")
        except:
            rowGroup = None
            j = 62
            break
        if (rowGroup != None):
            rows = rowGroup.find_elements(By.XPATH, './div/a')
            p = False
            for c in range(0, min(12, len(rows))):
                if (len(rows) >= 1):
                    row = rows[c]
                    output = ""
                    guser, gpassword = 'root', '@Aa6660416404'
                    ghost, gdatabase = 'localhost', 'primary_references_data'
                    user, password, host, database = guser, gpassword, ghost, gdatabase
                    if (row.text.find('FT') > 0):
                        if (date_namesSqlCheck(user, password, host, database, row.text)):
                            bool = True
                            connectionCheck = True
                            while (bool):
                                row.click()
                                p = True
                                # collecting_data:
                                time.sleep(3)  # script_load
                                popupText = driver.find_element(By.XPATH, xPopup).text
                                output = country_leagueGetter(output, popupText)
                                output = names_score_date_positionGetter(output, row.text)
                                if (popupCheck(popupText, output)):
                                    if (not connectionCheck):
                                        print("connected >>> OK")
                                    try:
                                        pregameForm = driver.find_element(By.XPATH, xPregameForm)
                                    except:
                                        pregameForm = None
                                    output = pregameScoreGetter(output, pregameForm)
                                    teamsLink = driver.find_elements(By.XPATH, xTeamsLink)
                                    output = teamHrefGetter(output, teamsLink)
                                    print(output)
                                    InsertToFaceMatchDataBase(user, password, host, database, output)
                                    bool = False
                                    connectionCheck = True
                                else:
                                    print("connecting . . . . . . . . . . ")
                                    connectionCheck = False
                                    output = ""
                                    time.sleep(3)
                else:
                    print("empty")
            if (p):
                counter -= 1
    return driver


def oneDayPinAndCollect(driver, url, filePath):
    b = True
    while (b):
        try:
            driver.refresh()
            time.sleep(2)
            driver.get(url)
            time.sleep(2)
            b = False
        except:
            print("refreshing ....")
            b = True
    print("\nPinnig >>> %s\n" % url)
    driver = pagePin(driver, filePath)
    driver.refresh()
    time.sleep(6)
    driver.find_element(By.XPATH, '/html/body').send_keys(Keys.HOME)
    screen = int(driver.execute_script("return document.documentElement.scrollHeight"))
    time.sleep(2)
    print("\ncollecting >>> %s\n" % url)
    driver = collect(driver)
    return driver


def collectAllDays(driver, urlsList,filePaths):
    for i in urlsList:
        url = i.strip()
        date = i[-11:].strip()
        filePath = filePaths + "/%s Leagues.txt" % date
        driver = oneDayPinAndCollect(driver, url, filePath)
    return driver


#sql / /. . .  . . .. .  .


def InsertToFaceMatchDataBase(user, password, host, database, output):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
    con = cnx.cursor(buffered=True)
    output = output.replace('`', '``')
    t = output.split("<=>")
    ex="England<=>Premier League, Round 21<=>Everton<=>Leicester City<=>0<=>1<=>2019-01-01<=>FT<=>27<=>28<=>https://www.sofa<=>https://www.sofasc"
    if (len(t) == 12):
        if (t[7] == 'FT'):
            Date, Position, Country, League, HomeTeam, AwayTeam, HomeResult, AwayResult, HomePreGameScore, AwayPreGameScore, HomeTeamLink, AwayTeamLink=(
            t[6], t[7],t[0], t[1], t[2], t[3], t[4], t[5], t[8], t[9], t[10], t[11])
            sql = "INSERT INTO primary_references_data.face_matches (Date,Position,Country,League,HomeTeam,AwayTeam,HomeResult,AwayResult,HomePreGameScore,AwayPreGameScore,HomeTeamLink,AwayTeamLink) VALUES (%s, %s,%s, %s, %s,%s, %s,%s, %s, %s,%s, %s)"
            val = (Date, Position, Country, League, HomeTeam, AwayTeam, HomeResult, AwayResult, HomePreGameScore,
                   AwayPreGameScore, HomeTeamLink, AwayTeamLink)
            con.execute(sql, val)
            cnx.commit()
    cnx.close()


def linkMaker(start, end):
    format = '%Y-%m-%d'
    first1,end1 = start,end
    urlsList=[]
    one_day = timedelta(1)
    first = datetime.strptime(first1, format).date()
    end = datetime.strptime(end1, format).date()
    while (first <= end):
        urlsList.append("https://www.sofascore.com/football/%s" % str(first))
        first += one_day
    return urlsList


def start(url):
    option = webdriver.ChromeOptions()
    s=Service(executablePath)
    driver = webdriver.Chrome(service=s,options=workOption(option))
    driver.maximize_window()
    driver.get(url)
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
    w = True
    if (1):  # accept all cookies  button
        try:
            accept = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
            if (accept.is_displayed):
                accept.click()
        except:
            print("accept button click error")
    return driver


def timer(n):
    for x in reversed(range(0, n)):
        print(x + 1)
        time.sleep(1)


def scrollDown(driver, length):
    driver.execute_script("window.scrollTo(0,window.scrollY + %s );" % length)
    time.sleep(2)
    return driver


def openAllMatch(driver):
    for l in range(1, 3):
        try:
            xAllMatchButton = '/html/body/div[1]/main/div/div[2]/div[1]/div[@style="max-width:100%"]/div[2]/div[1]/button'
            allMatchButton = driver.find_element(By.XPATH, xAllMatchButton)
            allMatchButton.send_keys(Keys.ENTER)
            time.sleep(6)
            driver.find_element(By.XPATH, '/html/body').send_keys(Keys.PAGE_UP)
            time.sleep(1)
            driver.find_element(By.XPATH, '/html/body').send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            driver.find_element(By.XPATH, '/html/body').send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            driver.find_element(By.XPATH, '/html/body').send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            driver.find_element(By.XPATH, '/html/body').send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            driver.find_element(By.XPATH, '/html/body').send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            driver.find_element(By.XPATH, '/html/body').send_keys(Keys.END)
            time.sleep(2)
            driver.find_element(By.XPATH, '/html/body').send_keys(Keys.HOME)
            time.sleep(1)
            driver.find_element(By.XPATH, '/html/body').send_keys(Keys.HOME)
            time.sleep(1)
        except:
            ""
    screen = int(driver.execute_script("return document.documentElement.scrollHeight"))
    return driver, screen


def use(filePath):
    w = True
    driver = start("https://www.sofascore.com/football/2020-02-02")
    driver.find_element(By.XPATH, '/html/body').send_keys(Keys.HOME)
    screen = int(driver.execute_script("return document.documentElement.scrollHeight"))
    while (w):
        n = input("what i do ?\n1.pin one day\n2.collect one day\n3.collect all days\n4.Exit\n")
        if (n == '1'):
            date = input("what's date ? ex=(2020-02-02)\nb = back\n")
            if "b" not in date:
                driver = oneDayPin(driver, "https://www.sofascore.com/football/%s" % date,
                                   filePath + "/%s Leagues.txt" % date)
        if (n == '2'):
            date = input("what's date ? ex=(2020-02-02)\nb = back\n")
            if "b" not in date:
                driver.get("https://www.sofascore.com/football/%s" % date)
                time.sleep(2)
                driver = collect(driver)
        if (n == '3'):
            start_day = input("start_date =? ex(2022-02-20)\n")
            end_day = input("end_date =? ex(2022-02-20)\n")
            urlsList=linkMaker(start_day, end_day)
            driver = collectAllDays(driver, urlsList, filePath)
        if (n == '4'):
            driver.close()
            w = False
            print("bye")


# main
use(filePaths)
