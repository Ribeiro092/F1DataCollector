import os
import csv
import sys
import logging
import requests
import traceback
from bs4 import BeautifulSoup
from datetime import datetime
from status_dict import status_dict
from logging.handlers import RotatingFileHandler
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

def agent(): #Gerar um user-agent aleatório para as requisições do scraper
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent


def capture_api(season_year): #Realizar a captura via api jolpica-f1
    output_dir = f"C:\\Resultados_F1"

    url_api = "https://api.jolpi.ca/ergast/f1/"
    race_data = []

    for attempt in range(0, 6):
        try:
            url_races = f"{url_api}{season_year}/races/"
            response = requests.get(url_races)

            if response.status_code != 200:
                raise Exception(f"Falha ao realizar requisição, Url: {response.url}, Status: {response.status_code}, Retorno: {response.text}")

            json_races = response.json()
            qtd_races = int(json_races["MRData"]["total"])

            for race in range(1, qtd_races+1):
                url_results = f"{url_api}{season_year}/{race}/results/"
                response = requests.get(url_results)

                if response.status_code != 200:
                    raise Exception(f"Falha ao realizar requisição, Url: {response.url}, Status: {response.status_code}, Retorno: {response.text}")

                lst_results = response.json()

                if lst_results["MRData"]["RaceTable"]["Races"]:
                    race_date = lst_results["MRData"]["RaceTable"]["Races"][0]["date"]
                    race_name = lst_results["MRData"]["RaceTable"]["Races"][0]["raceName"]
                    race_name = race_name.split(sep=' Grand')[0]
                    lst_results = lst_results["MRData"]["RaceTable"]["Races"][0]["Results"]

                    drivers_stats = []

                    for driver in lst_results:
                        driver_position = driver["position"] if driver.get("position") else ''
                        driver_number = driver["number"] if driver.get("number") else ''
                        driver_name = f'{driver["Driver"]["givenName"]} {driver["Driver"]["familyName"]}' if driver.get("Driver") else ''
                        driver_team = driver["Constructor"]["name"] if driver.get("Constructor") else ''
                        driver_status = driver["status"] if driver.get("status") else ''
                        race_laps = int(driver["laps"]) if driver.get("laps") else 0
                        driver_points = driver["points"] if driver.get("points") else 0
                        fastest_lap = int(driver["FastestLap"]["rank"]) if driver.get("FastestLap") and driver["FastestLap"].get("rank") else 0

                        if fastest_lap != 1:
                            fastest_lap = ''
                        else:
                            fastest_lap = "Sim"

                        if driver_status == "Finished":
                            race_time = driver["Time"]["time"] if driver.get("Time") else ''
                            if race_time:
                                if len(race_time) < 5:
                                    minutes_seconds = race_time.split(':')
                                    minutes = minutes_seconds[0].zfill(2)
                                    seconds = minutes_seconds[1].ljust(2)
                                    race_time = f"{minutes}:{seconds}.000"
                                elif len(race_time) < 8:
                                    minutes_seconds = race_time[1:].split('.')
                                    minutes = minutes_seconds[0].zfill(2)
                                    seconds = minutes_seconds[1].ljust(3, '0')
                                    race_time = f"+0:{minutes}.{seconds}"
                        elif "Lap" in driver_status:
                            race_time = driver_status
                        else:
                            race_time = "DNF"

                        driver_status = status_dict.get(driver_status, driver_status)

                        dict_driver = {
                            "ETAPA": race_name,
                            "DATA": race_date,
                            "COLOCAÇÃO": driver_position,
                            "NÚMERO": driver_number,
                            "NOME": driver_name,
                            "EQUIPE": driver_team,
                            "VOLTAS": race_laps,
                            "TEMPO": f"{race_time}",
                            "PONTOS": driver_points,
                            "STATUS": driver_status,
                            "MELHOR VOLTA": fastest_lap,
                        }
                        drivers_stats.append(dict_driver)

                    race_data.extend(drivers_stats)

                    file_path = os.path.join(output_dir, f"Temporada_{season_year}_API.csv")

                    if race_data:
                        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                            fieldnames = race_data[0].keys()
                            writer = csv.DictWriter(file, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(race_data)
                else:
                    continue
        except:
            trace = traceback.format_exc()
            logging.error(msg=trace)

            if attempt == 5:
                error = f"Error: Máximo de erros excedido por captura pela api\nÚltimo erro: {trace}"
                logging.error(msg=error)
                return error
        break


def capture_scraper(season_year): #Realizar a captura via web scraping do site oficial da F1
    output_dir = f"C:\\Resultados_F1"
    base_url = f"https://www.formula1.com/en/results/{season_year}"

    user_agent = agent()
    race_data = []

    for attempt in range(0, 6):
        try:
            session = requests.session()
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'pt-BR,pt;q=0.9',
                'priority': 'u=0, i',
                'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': user_agent,
            }

            response = session.get(f'{base_url}/races', headers=headers)

            if response.status_code != 200:
                raise Exception(f"Falha ao realizar requisição, Url: {response.url}, Status: {response.status_code}, Retorno: {response.text}")

            soup = BeautifulSoup(markup=response.text, features="html.parser")

            races_table = soup.select("tbody tr")

            for race in races_table:
                race_info = race.select("td")
                race_name = race_info[0].get_text()
                race_date = race_info[1].get_text()
                race_date = datetime.strptime(race_date, "%d %b %Y").strftime("%Y-%m-%d")

                race_link = race_info[0].find("a")["href"]
                race_link = f"{base_url}/{race_link}"

                drivers_stats = []
                headers = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'pt-BR,pt;q=0.9',
                    'priority': 'u=0, i',
                    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'none',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': user_agent,
                }

                response = session.get(url=race_link, headers=headers)

                if response.status_code != 200:
                    raise Exception(f"Falha ao realizar requisição, Url: {response.url}, Status: {response.status_code}, Retorno: {response.text}")
                soup = BeautifulSoup(markup=response.text, features="html.parser")

                fastest_url = None
                for a in soup.find_all("a"):
                    if "Fastest Laps" in a.get_text():
                        fastest_url = a["href"]
                        break

                results_table = soup.select("tbody tr")
                for driver in results_table:
                    driver_data = [td.get_text() for td in driver.select("td")] + [''] * 7
                    driver_position, driver_number, driver_name, driver_team, race_laps, race_time, driver_points = driver_data[:7]
                    driver_name = driver_name.replace("\xa0", " ")[:-3]

                    driver_status = ""
                    if "lap" in race_time:
                        qtd_laps = race_time.split(' ')[0]
                        if qtd_laps == "+1":
                            driver_status = f"{qtd_laps} Volta"
                        else:
                            driver_status = f"{qtd_laps} Voltas"

                    elif race_time.startswith('+') and 's' in race_time:
                        race_time = race_time.replace('s', '')
                        minutes_seconds = race_time[1:].split('.')
                        minutes = minutes_seconds[0].zfill(2)
                        seconds = minutes_seconds[1].ljust(3, '0')
                        race_time = f"+0:{minutes}.{seconds}"

                    else:
                        driver_status = "Finalizado" if race_time != "DNF" else race_time


                    dict_driver = {
                        "ETAPA": race_name,
                        "DATA": race_date,
                        "COLOCAÇÃO": driver_position,
                        "NÚMERO": driver_number,
                        "NOME": driver_name,
                        "EQUIPE": driver_team,
                        "VOLTAS": race_laps,
                        "TEMPO": f"{race_time}",
                        "PONTOS": driver_points,
                        "STATUS": driver_status,
                        "MELHOR VOLTA": '',
                    }

                    drivers_stats.append(dict_driver)

                if fastest_url:
                    headers = {
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-language': 'pt-BR,pt;q=0.9',
                        'priority': 'u=0, i',
                        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'document',
                        'sec-fetch-mode': 'navigate',
                        'sec-fetch-site': 'none',
                        'sec-fetch-user': '?1',
                        'upgrade-insecure-requests': '1',
                        'user-agent': user_agent,
                    }

                    response = session.get(
                        url=f"https://www.formula1.com{fastest_url}",
                        headers=headers,
                    )

                    if response.status_code != 200:
                        raise Exception(f"Falha ao realizar requisição, Url: {response.url}, Status: {response.status_code}, Retorno: {response.text}")

                    soup = BeautifulSoup(markup=response.text, features="html.parser")

                    fastest_table = soup.select("tbody tr")
                    fastest_data = fastest_table[0]
                    fastest_data = fastest_data.select("td")
                    driver_surname = fastest_data[2].get_text() if fastest_data[2] else ''
                    driver_surname = driver_surname.replace("\xa0", " ")[:-3]

                    for fastest_driver in drivers_stats:
                        if fastest_driver["NOME"] == driver_surname:
                            fastest_driver["MELHOR VOLTA"] = "Sim"
                            break

                race_data.extend(drivers_stats)

            file_path = os.path.join(output_dir, f"Temporada_{season_year}_Scraper.csv")

            if race_data:
                with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                    fieldnames = race_data[0].keys()
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(race_data)

        except:
            trace = traceback.format_exc()
            logging.error(msg=trace)

            if attempt == 5:
                error = f"Error: Máximo de erros excedido por captura pela api\nÚltimo erro: {trace}"
                logging.error(msg=error)
                return error
        break


def create_logger(project_name: str): #Cria a pasta de resultado do projeto e um arquivo de log rotativo.
    try:
        path = "C:/Resultados_F1/LOGS"
        os.makedirs(path, exist_ok=True)
        log_file = os.path.join(path, f'{project_name}.log')

        rotating_handler = RotatingFileHandler(
            filename=log_file, mode='a', maxBytes=5 * 1024 * 1024, encoding='utf-8'
        )

        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s - %(message)s',
            handlers=[logging.StreamHandler(), rotating_handler]
        )
    except:
        path = os.path.dirname(sys.executable)
        log_file = os.path.join(path, f'{project_name}.log')

        rotating_handler = RotatingFileHandler(
            filename=log_file, mode='a', maxBytes=5 * 1024 * 1024, encoding='utf-8'
        )

        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s - %(message)s',
            handlers=[logging.StreamHandler(), rotating_handler]
        )
