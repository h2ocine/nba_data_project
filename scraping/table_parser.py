import pandas as pd
import bs4
from urllib import request
from selenium import webdriver
import time
from selenium.webdriver.common.by import By

def parse_schedule(url : str, title : str) -> pd.DataFrame:
    # Open the URL and read the HTML content
    response = request.urlopen(url)
    html = response.read()

    # Create BeautifulSoup object to parse the HTML
    soup = bs4.BeautifulSoup(html, "lxml")

    # Find the <table> tag
    table_tag = soup.find('table')
    table_soup = bs4.BeautifulSoup(str(table_tag), features="lxml")

    # Get the table lines
    lines_list = table_soup.find_all('tr')

    # Get the column names
    if(len(lines_list[0]) == len(lines_list[1])):
        names_ligne_position = 0
    else:
        names_ligne_position = 1

    tr_soup = bs4.BeautifulSoup(str(lines_list[names_ligne_position]), features="lxml")
    td_tags = tr_soup.find_all('td')
    columns_name = []
    for td in td_tags:
        attribute = td.get_text()
        columns_name.append(attribute)

    columns_name.append('Home_Away') # Add the home away column

    # Get the data
    data = [] 
    for tr in lines_list[names_ligne_position+1:]:
        tr_soup = bs4.BeautifulSoup(str(tr), features="lxml")
        td_tags = tr_soup.find_all('td')

        if len(td_tags) < len(columns_name) - 1: # Get only the information we want
            continue

        attributes = []
        for td in td_tags:
            attribute = td.get_text()
            attributes.append(attribute)

        home_away = attributes[1][:3] # Get if the match played in home or away
        oppenent_name = attributes[1][2:]
        
        # Add the home_away attribute
        if(attributes[1][-1] == '*'):
            attributes[1] = oppenent_name[:-2]
            home_away = 'N' # Neutral
        else: 
            if attributes[1][:2] == 'vs':
                home_away = 'A' # Away
            else:
                home_away = 'H' # Home
            attributes[1] = oppenent_name

        attributes.append(home_away) 
        
        data.append(attributes)

    # Get the data into a dataframe
    df = pd.DataFrame(data, columns=columns_name)

    # Add the Title of the dataframe 
    df['Title'] = title

    return df

def parse_standings(url : str, title : str) -> pd.DataFrame:
    """
    Parses the HTML content of a given URL representing an NBA team's schedule,
    extracts the schedule data, and stores it in a pandas DataFrame.

    Args:
        url (str): The URL of the webpage containing the schedule.
        title (str): The title to be assigned to the DataFrame.

    Returns:
        pandas.DataFrame: A DataFrame containing the parsed schedule data,
        with each column representing a different attribute of the games
        (e.g., opponent, result, date), and the 'Title' column containing
        the specified title for reference.
    """
    # Open the URL and read the HTML content
    response = request.urlopen(url)
    html = response.read()

    # Create BeautifulSoup object to parse the HTML
    soup = bs4.BeautifulSoup(html, "lxml")

    # Get the teams name table 
    names_table_tag = soup.find('table')
    names_table_soup = bs4.BeautifulSoup(str(names_table_tag), features="lxml")

    # Get the info table 
    info_table_tag = soup.find('div', {"class":"Table__Scroller"})
    info_table_soup = bs4.BeautifulSoup(str(info_table_tag), features="lxml")


    # Get the tables lines
    name_lines_list = names_table_soup.find_all('tr')
    info_lines_list = info_table_soup.find_all('tr')

    # Get the column names
    tr_tag = info_table_soup.find('tr', {"class":"Table__sub-header Table__TR Table__even"})
    columns_name = [column.get_text() for column in tr_tag]
    columns_name = ['Team Name'] + columns_name

    data = [] 
    for i in range(len(name_lines_list)):

        # Get the team name
        tr_soup_name = bs4.BeautifulSoup(str(name_lines_list[i]), features="lxml")
        tr_soup_info = bs4.BeautifulSoup(str(info_lines_list[i]), features="lxml")
        
        # Get the team informations
        td_tags = tr_soup_name.find_all('td') + tr_soup_info.find_all('td')

        attributes = []
        for td in td_tags:
            attribute = td.get_text()
            if(attributes == []):
                offset = 3
                if(attribute[3] == '-'):
                    offset += 1
                attributes.append(attribute[offset:])
            else:
                attributes.append(attribute)
        data.append(attributes)

    # Get the data into a dataframe
    df = pd.DataFrame(data[1:], columns=columns_name)

    # Add the Title of the dataframe 
    df['Title'] = title

    return df

def parse_teams(url : str, title : str) -> pd.DataFrame:
    # Create a new Chrome browser instance
    driver = webdriver.Chrome()

    # Open the URL in the browser
    driver.get(url)

    # Get the page source after JavaScript execution
    html = driver.page_source
    driver.quit()

    # Create BeautifulSoup object to parse the HTML
    soup = bs4.BeautifulSoup(html, "lxml")

    # Get the teams name
    names_table_tag = soup.find_all('a')
    teams = [tag.get_text() for tag in names_table_tag[15:-27] if tag.get_text()!='']

    # Get the info table 
    info_table_tag = soup.find('div', {"class":"Table__Scroller"})
    info_table_soup = bs4.BeautifulSoup(str(info_table_tag), "lxml")

    # Get the tables lines
    info_lines_list = info_table_soup.find_all('tr')

    # Get the column names
    tr_tag = info_table_soup.find('tr', {"class":"Table__sub-header Table__TR Table__even"})
    columns_name = [column.get_text() for column in tr_tag]
    columns_name = ['Rank','Team Name'] + columns_name

    data = [] 
    rank = 0
    for i in range(len(info_lines_list)-1):
        # Get the team name
        tr_soup_info = bs4.BeautifulSoup(str(info_lines_list[i+1]), "lxml")
        
        # Get the team informations
        td_tags = tr_soup_info.find_all('td')

        attributes = [str(rank+1),teams[rank]] # Initialise with the team name and its rank
        for td in td_tags:
            attribute = td.get_text()
            attributes.append(attribute)
        data.append(attributes)
        rank += 1

    # Get the data into a dataframe
    df = pd.DataFrame(data, columns=columns_name)

    # Add the Title of the dataframe 
    df['Title'] = title

    return df

def parse_players(url: str, title: str) -> pd.DataFrame:
    # Create a new Chrome browser instance
    driver = webdriver.Chrome()

    # Open the URL in the browser
    driver.get(url)

    # Close the cookie pop-up 
    try:
        close_button = driver.find_element(By.XPATH, '//button[text()="Continue without Accepting"]')
        close_button.click()
    except:
        pass

    # Click the "Show More" button to load all the content
    try:
        time.sleep(0.35)
        show_more_link = driver.find_element(By.XPATH, '//a[text()="Show More"]')
        while True:
            show_more_link = driver.find_element(By.XPATH, '//a[text()="Show More"]')
            show_more_link.click()
            time.sleep(0.35)  # Allow time for content to load
    except:
        pass

    # Get the page source after JavaScript execution
    html = driver.page_source
    driver.quit()

    # Create BeautifulSoup object to parse the HTML
    soup = bs4.BeautifulSoup(html, "html.parser")

    # Get the players name
    names_table_tag = soup.find_all('a')
    players = [tag.get_text() for tag in names_table_tag[27:-26]]

    # Get the info table
    info_table_tag = soup.find('div', {"class": "Table__Scroller"})
    info_table_soup = bs4.BeautifulSoup(str(info_table_tag), "html.parser")

    # Get the tables lines
    info_lines_list = info_table_soup.find_all('tr')
    # Get the column names
    tr_tag = info_table_soup.find('tr', {"class": "Table__sub-header Table__TR Table__even"})
    columns_name = [column.get_text() for column in tr_tag]
    columns_name = ['Player Name'] + columns_name

    data = []
    for i in range(len(info_lines_list)-1):
        # Get the player  name
        tr_soup_info = bs4.BeautifulSoup(str(info_lines_list[i+1]), "html.parser")

        # Get tplayer information
        td_tags = tr_soup_info.find_all('td')
        
        attributes = [players[i]]  # Initialize with tplayer name and its rank
        for td in td_tags:
            attribute = td.get_text()
            attributes.append(attribute)
        data.append(attributes)

    # Get the data into a dataframe
    df = pd.DataFrame(data, columns=columns_name)

    # Add the Title of the dataframe
    df['Title'] = title

    return df
