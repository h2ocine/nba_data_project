import pandas as pd
import bs4
from urllib import request
import urllib.parse
import table_parser

def upload_schedule(schedule_url : str) -> list[pd.DataFrame]:
    # Open the URL and read the HTML content
    response = request.urlopen(schedule_url)
    html = response.read()

    # Create BeautifulSoup object to parse the HTML
    soup = bs4.BeautifulSoup(html, "lxml")

    # Get the <select> tags
    tag = soup.find_all('select')
    team_select_tag = tag[0] # Select tag for teams
    year_select_tag = tag[2] # Select tag for years

    # Get all the option tags for teams
    team_soup = bs4.BeautifulSoup(str(team_select_tag), "lxml")
    team_option_tag = team_soup.find_all('option')

    # Get all the option tags for years
    year_soup = bs4.BeautifulSoup(str(year_select_tag), "lxml")
    year_option_tag = year_soup.find_all('option')

    # Get the teams 
    teams = [('Atlanta Hawks', 'atl')]
    for i in team_option_tag[1:]:
        teams.append((i.get_text(),i['data-param-value']))

    # Get the years 
    years = []
    for i in year_option_tag:
        years.append((i.get_text(),i['data-param-value']))


    schedules = [] # Create a schedules list

    for (team,team_code) in teams:
        for (year,year_code) in years:
            # Get the URL of the team in the specified year
            team_url = schedule_url[:-3] + team_code + '/season/' + year_code
            response = urllib.request.urlopen(team_url)
            html_content = response.read()

            soup = bs4.BeautifulSoup(html_content, "lxml")

            # Get the <select> tags
            tag = soup.find_all('select')

            # Select tag for season types
            if(len(tag) <= 4):
                seasontype_tag = tag[-1] 
            else:
                seasontype_tag = tag[4] 

            seasontype_soup = bs4.BeautifulSoup(str(seasontype_tag), "lxml")
            seasontype_tag = seasontype_soup.find_all('option') # Get all the option tags for season types
            
            seasonstypes = []
            for i in seasontype_tag:
                try:
                    seasonstypes.append((i.get_text(), i['data-param-value']))
                except KeyError: # No Data Available
                    continue 
            
            for (seasontype,seasontype_code) in seasonstypes:

                url = team_url + '/seasontype/' + seasontype_code[:-1]
                title = f'{team} {year} {seasontype} NBA Schedule'

                df = table_parser.parse_schedule(url,title) # Parse the schedule and obtain a DataFrame
                
                schedules.append(df) # Append the DataFrame to the schedules list

                print(f'{title} uploaded successfully from {url}')

    return schedules

def upload_standings(standings_url : str) -> list[pd.DataFrame]:
    # Open the URL and read the HTML content
    response = request.urlopen(standings_url)
    html = response.read()

    # Create BeautifulSoup object to parse the HTML
    soup = bs4.BeautifulSoup(html, "lxml")

    # Get the <select> tags
    tag = soup.find_all('select')
    year_select_tag = tag[0] # Select tag for year

    # Get all the option tags for teams
    year_soup = bs4.BeautifulSoup(str(year_select_tag), "lxml")
    year_option_tag = year_soup.find_all('option')

    # Get the seasons years
    years = []
    for y in year_option_tag:
        years.append((y.get_text(),y['value']))

    standings = []
    for (year_label,year) in years:
        # Get the Regular Season data
        url = f'https://www.espn.com/nba/standings/_/season/{year}/group/league'
        title = f'NBA Standings Regular Season {year_label}'

        df = table_parser.parse_standings(url, title)
        standings.append(df)

        print(f'{title} uploaded successfully from {url}')

        # Get the Pre Season data
        url = f'https://www.espn.com/nba/standings/_/seasontype/pre/season/{year}/group/league'
        title = f'NBA Standings Pre Season {year_label}'

        df = table_parser.parse_standings(url, title)
        standings.append(df)

        print(f'{title} uploaded successfully from {url}')

    return standings

def upload_teams(teams_url : str) -> list[pd.DataFrame]:
    
    # Set the url if we want to get the oppenent stats or the differential stats
    add_to_url = ''
    len_opponent = len('/view/opponent')
    len_differential = len('/view/differential')
    if(teams_url[-len_opponent:] == '/view/opponent'):
        add_to_url =  teams_url[-len_opponent:]
    else:
        if(teams_url[-len_differential:] == '/view/differential'):
            add_to_url =  teams_url[-len_differential:]

    # Open the URL and read the HTML content
    response = request.urlopen(teams_url)
    html = response.read()

    # Create BeautifulSoup object to parse the HTML
    soup = bs4.BeautifulSoup(html, "lxml")

    # Get the <select> tags
    tag = soup.find_all('select')
    year_select_tag = tag[0] # Select tag for year

    # Get all the option tags for teams
    year_soup = bs4.BeautifulSoup(str(year_select_tag), "lxml")
    year_option_tag = year_soup.find_all('option')

    # Get the seasons year and the season type (Regular or Preseason)
    years_type = []
    for y in year_option_tag:
        year_label = y.get_text()[:7]
        type_label = y.get_text()[8:]
        year = y['value'][:4]
        type = y['value'][5:]
        years_type.append((year_label,type_label,year,type))

    teams = []
    for (year_label,type_label,year,type) in years_type:
        # Get the Regular Season data
        url = f'https://www.espn.com/nba/stats/team/_{add_to_url}/season/{year}/seasontype/{type}'
        title = f'NBA Team {type_label} Stats {year_label}'

        df = table_parser.parse_teams(url, title)
        teams.append(df)

        print(f'{title} uploaded successfully from {url}')

    return teams

def upload_player(teams_url : str) -> list[pd.DataFrame]:

    # Open the URL and read the HTML content
    response = request.urlopen(teams_url)
    html = response.read()

    # Create BeautifulSoup object to parse the HTML
    soup = bs4.BeautifulSoup(html, "lxml")

    # Get the <select> tags
    tag = soup.find('div',{'class' : 'flex flex-wrap'})
    year_select_tag = tag # Select tag for year
    
    # Get all the option tags for teams
    year_soup = bs4.BeautifulSoup(str(year_select_tag), "lxml")
    year_option_tag = year_soup.find_all('option')
    
    # Get the seasons year and the season type (Regular or Preseason)
 
    years_type = []
    for y in year_option_tag:
        if(y.has_attr('value') == False):
            continue
        year_label = y.get_text()[:7]
        type_label = y.get_text()[8:]
        year = y['value'][:4]
        type = y['value'][5:]
        years_type.append((year_label,type_label,year,type))
    
    players = []
    for (year_label,type_label,year,type) in years_type:
        # Get the Regular Season data
        url = f'https://www.espn.com/nba/stats/player/_/season/{year}/seasontype/{type}'
        title = f'NBA Team {type_label} Stats {year_label}'

        MAX_RETRIES=10
        for retry_df in range(MAX_RETRIES):
            try:
                df = table_parser.parse_players(url, title)
                players.append(df)

                print(f'{title} uploaded successfully from {url}')
                break  # Sort de la boucle si le parsing réussit

            except Exception as e:
                print(f'Error occurred: {str(e)}')
                if retry_df >= MAX_RETRIES - 1:
                    print(f'Maximum retries reached to parse {url}. Upload failed.')
                    raise e  # Déclenche à nouveau l'exception après le nombre maximum de tentatives

    return players