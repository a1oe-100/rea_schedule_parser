!pip install selenium openpyxl
!apt-get update
!apt install -y chromium-chromedriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import tempfile
import os
import time
import re

# Настройки Chrome
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--remote-debugging-port=9222')  # Уникальный порт

# Список групп для парсинга (название группы и URL)
groups_to_parse = {
    "1-BI01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B801%2F24%D0%B1",
    "1-BI02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B802%2F24%D0%B1",
    "1-BI03": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B803%2F24%D0%B1",
    "1-BI04": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B804%2F24%D0%B1",
    "1-BI05": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B805%2F24%D0%B1",
    "1-BI06": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B806%2F24%D0%B1",
    "1-IB01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B101%2F24%D0%B1",
    "1-IB02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B102%2F24%D0%B1",
    "1-IB03": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B103%2F24%D0%B1",
    "1-IB04": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B104%2F24%D0%B1",
    "1-IB05": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B105%D1%83%2F24%D0%B1",
    "1-IB06": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B106%D1%83%2F24%D0%B1",
    "1-IVT01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B2%D1%8201%2F24%D0%B1",
    "1-IVT02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B2%D1%8202%2F24%D0%B1",
    "1-IST01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D1%81%D1%8201%2F24%D0%B1",
    "1-IST02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D1%81%D1%8202%2F24%D0%B1",
    "1-IST03": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D1%81%D1%8203%2F24%D0%B1",
    "1-IST04": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D1%81%D1%8204%2F24%D0%B1",
    "1-MO01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BC%D0%BE01%2F24%D0%B1",
    "1-MO02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BC%D0%BE02%2F24%D0%B1",
    "1-MO03": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BC%D0%BE03%2F24%D0%B1",
    "1-PI01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B801%2F24%D0%B1",
    "1-PI02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B802%2F24%D0%B1",
    "1-PI03": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B803%2F24%D0%B1",
    "1-PI04": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B804%D1%83%2F24%D0%B1",
    "1-PI05": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B805%D1%83%2F24%D0%B1",
    "1-S01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D1%8101%2F24%D0%B1",
    "1-S02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D1%8102%2F24%D0%B1",
    "1-E01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D1%8D01%2F24%D0%B1",
    "1-E02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D1%8D02%2F24%D0%B1",
    "2-BI01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B801%2F23%D0%B1",
    "2-BI02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B802%2F23%D0%B1",
    "2-BI03": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B803%2F23%D0%B1",
    "2-BI04": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B804%2F23%D0%B1",
    "2-BI05": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B805%2F23%D0%B1",
    "2-BI06": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B806%2F23%D0%B1",
    "2-BI07": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B807%2F23%D0%B1",
    "2-BI08": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B808%2F23%D0%B1",
    "2-IB01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B101%2F23%D0%B1",
    "2-IB02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B102%2F23%D0%B1",
    "2-IB03": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B103%2F23%D0%B1",
    "2-IB04": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B104%2F23%D0%B1",
    "2-IB05": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B105%D1%83%2F23%D0%B1",
    "2-IB06": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B106%D1%83%2F23%D0%B1",
    "2-IVT01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B2%D1%8201%2F23%D0%B1",
    "2-IVT02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B2%D1%8202%2F23%D0%B1",
    "2-IST01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D1%81%D1%8201%2F23%D0%B1",
    "2-IST02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D1%81%D1%8202%2F23%D0%B1",
    "2-MO01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BC%D0%BE01%2F23%D0%B1",
    "2-MO02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BC%D0%BE02%2F23%D0%B1",
    "2-MO03": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BC%D0%BE03%2F23%D0%B1",
    "2-PI01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B801%2F23%D0%B1",
    "2-PI02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B802%2F23%D0%B1",
    "2-PI03": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B803%D1%83%2F23%D0%B1",
    "2-PI04": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B804%D1%83%2F23%D0%B1",
    "2-S01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D1%8101%2F23%D0%B1",
    "2-E01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D1%8D01%2F23%D0%B1",
    "2-E02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D1%8D02%2F23%D0%B1",
    "2-PM01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%BC01%2F23%D0%B1",
    "2-PM02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%BC02%2F23%D0%B1",
    "3-BI09": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B809%2F22%D0%B1",
    "3-BI10": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B810%2F22%D0%B1",
    "3-BI19": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B819%2F22%D0%B1",
    "3-BI20": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B1%D0%B820%2F22%D0%B1",
    "3-IB07": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B107%2F22%D0%B1",
    "3-IB08": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B108%2F22%D0%B1",
    "3-IB13": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B113%D1%83%2F22%D0%B1",
    "3-IB18": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D0%B118%2F22%D0%B1",
    "3-IST15": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D1%81%D1%8215%2F22%D0%B1",
    "3-IST21": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%B8%D1%81%D1%8221%2F22%D0%B1",
    "3-MO11": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BC%D0%BE11%2F22%D0%B1",
    "3-MO12": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BC%D0%BE12%2F22%D0%B1",
    "3-PI05": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B805%2F22%D0%B1",
    "3-PI06": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B806%2F22%D0%B1",
    "3-PI14": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B814%D1%83%2F22%D0%B1",
    "3-PI17": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B817%2F22%D0%B1",
    "3-PI22": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%B822%D1%83%2F22%D0%B1",
    "3-PM03": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%BC03%2F22%D0%B1",
    "3-PM04": "https://rasp.rea.ru/?q=15.27%D0%B4-%D0%BF%D0%BC04%2F22%D0%B1",
    "3-E01": "https://rasp.rea.ru/?q=15.27%D0%B4-%D1%8D01%2F22%D0%B1",
    "3-E02": "https://rasp.rea.ru/?q=15.27%D0%B4-%D1%8D02%2F22%D0%B1",
    "3-S16": "https://rasp.rea.ru/?q=15.27%D0%B4-%D1%8116%2F22%D0%B1",
    "4-BI09": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%B1%D0%B8%D1%86%D1%8209%2F21%D0%B1",
    "4-BI10": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%B1%D0%B8%D1%86%D1%8210%2F21%D0%B1",
    "4-BI17": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%B1%D0%B8%D1%86%D1%8217%2F21%D0%B1",
    "4-IB07": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%B8%D0%B1%D0%B1%D0%B0%D1%8107%2F21%D0%B1",
    "4-IB08": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%B8%D0%B1%D1%84%D0%BC08%2F21%D0%B1",
    "4-IB16": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%B8%D0%B1%D0%B1%D0%B0%D1%8116%2F21%D0%B1",
    "4-MO11": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%BC%D0%BE%D1%81%D0%B8%D0%BF11%2F21%D0%B1",
    "4-MO12": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%BC%D0%BE%D1%81%D0%B8%D0%BF12%2F21%D0%B1",
    "4-PI05": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%BF%D0%B8%D0%B8%D0%BF05%2F21%D0%B1",
    "4-PI06": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%BF%D0%B8%D0%BF%D1%8D06%2F21%D0%B1",
    "4-PI15": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%BF%D0%B8%D0%BF%D1%8D15%2F21%D0%B1",
    "4-PI18": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%BF%D0%B8%D0%B8%D0%BF18%2F21%D0%B1",
    "4-E01": "https://rasp.rea.ru/?q=15.11%D0%B4-%D1%8D%D0%B0%D1%8D01%2F21%D0%B1",
    "4-E02": "https://rasp.rea.ru/?q=15.11%D0%B4-%D1%8D%D0%B1%D1%8102%2F21%D0%B1",
    "4-PM03": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%BF%D0%BC%D0%BF%D0%BC%D0%B803%2F21%D0%B1",
    "4-PM04": "https://rasp.rea.ru/?q=15.11%D0%B4-%D0%BF%D0%BC%D0%B1%D0%B404%2F21%D0%B1",
    }

# Создаем функцию получения текущей недели с улучшенной обработкой ошибок
def get_current_week(driver):
    try:
        week_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "weekNumLabel")))
        week_text = week_element.text.strip()
        if not week_text:
            print("Предупреждение: номер недели пустой. Попытка получить значение из другого элемента.")
            week_element = driver.find_element(By.CSS_SELECTOR, ".week-num")
            week_text = week_element.text.strip()
        return int(week_text)
    except Exception as e:
        print(f"Ошибка при получении номера недели: {str(e)}")
        return -1

# Создаем функцию перехода к искомой неделе с улучшенной логикой
def navigate_to_week(driver, target_week):
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        try:
            current_week = get_current_week(driver)
            if current_week == -1:
                print("Не удалось определить текущую неделю. Обновляем страницу...")
                driver.refresh()
                time.sleep(3)
                attempts += 1
                continue

            print(f"Текущая неделя: {current_week}, Целевая неделя: {target_week}")

            if current_week == target_week:
                return True

            if current_week < target_week:
                button_id = "next"
                expected_week = current_week + 1
            else:
                button_id = "prev"
                expected_week = current_week - 1

            try:
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f"#{button_id}")))
                driver.execute_script("arguments[0].click();", button)
                time.sleep(1)

                new_week = get_current_week(driver)
                if new_week == expected_week:
                    attempts = 0
                else:
                    attempts += 1
                    print(f"Неделя не изменилась как ожидалось. Ожидалось: {expected_week}, получено: {new_week}")
            except Exception as e:
                print(f"Ошибка при клике на кнопку: {str(e)}")
                attempts += 1

        except Exception as e:
            print(f"Ошибка в navigate_to_week: {str(e)}")
            attempts += 1
            time.sleep(1)

    print(f"Не удалось перейти на неделю {target_week} после {max_attempts} попыток")
    return False

def extract_day_and_pair_number(soup):
    try:
        # Ищем div с информацией о времени
        time_div = soup.find('br').next_sibling.strip()

        # Извлекаем день недели (первое слово до запятой)
        day_match = re.search(r'^([а-яА-Я]+),\s*\d+\s+\w+\s+\d{4}', time_div, re.IGNORECASE)
        day = day_match.group(1).capitalize() if day_match else "Неизвестно"

        # Извлекаем номер пары (цифра перед словом "пара")
        pair_match = re.search(r'(\d+)\s+пара', time_div)
        pair_number = pair_match.group(1) if pair_match else "0"

        return day, pair_number
    except Exception as e:
        print(f"Ошибка при извлечении дня и номера пары: {str(e)}")
        return "Неизвестно", "0"

# Создаем функцию полного сканирования одной недели
def parse_current_week_schedule(driver, group_name):
    schedule_data = []
    pair_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'task') and (contains(.,'корпус') or contains(.,'подгруппы'))]")))
    print(f"Найдено {len(pair_elements)} пар для обработки")

    for index, pair in enumerate(pair_elements):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pair)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", pair)
            time.sleep(1)

            modal = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.modal-body")))
            modal_html = modal.get_attribute('innerHTML')
            soup = BeautifulSoup(modal_html, 'html.parser')

            Allowed_categories = {"Лекция", "Практическое занятие", "Лабораторная работа"}

            category = soup.find('strong').text.strip()
            if category not in Allowed_categories:
                print(f"Пропускаем пару типа: {category}")
                continue

            # Извлекаем информацию о дне и номере пары
            time_info = soup.find(text=re.compile(r'пара'))
            day, pair_number = extract_day_and_pair_number(soup) if time_info else ("Неизвестно", "0")

            subgroup_blocks = soup.find_all('div', class_='element-info-body')

            if len(subgroup_blocks) > 1:
                for subgroup in subgroup_blocks:
                    subgroup_num = subgroup.get('data-subgroup', 'x')
                    subject = subgroup.find('h5').text.strip()

                    teacher_tag = subgroup.find('a', href=lambda x: x and '?q=' in x)
                    for icon in teacher_tag.find_all('i'):
                        icon.decompose()
                    teacher = teacher_tag.get_text(strip=True)

                    location_text = [text for text in subgroup.stripped_strings if "Аудитория:" in text][0]
                    classroom = location_text.replace('Аудитория:', '').strip()

                    schedule_data.append({
                        'Группа': group_name,
                        'День недели': day,
                        'Номер пары': pair_number,
                        'Название пары': f"{subject} (подгруппа {subgroup_num})",
                        'Тип пары': category,
                        'Преподаватель': teacher,
                        'Аудитория': classroom,
                    })
            else:
                subject = soup.find('h5').text.strip()

                teacher_tag = soup.find('a', href=lambda x: x and '?q=' in x)
                for icon in teacher_tag.find_all('i'):
                    icon.decompose()
                teacher = teacher_tag.get_text(strip=True)

                location_text = [text for text in soup.stripped_strings if "Аудитория:" in text][0]
                classroom = location_text.replace('Аудитория:', '').strip()

                schedule_data.append({
                    'Группа': group_name,
                    'День недели': day,
                    'Номер пары': pair_number,
                    'Название пары': subject,
                    'Тип пары': category,
                    'Преподаватель': teacher,
                    'Аудитория': classroom
                })

            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.close[data-dismiss='modal']")))
            driver.execute_script("arguments[0].click();", close_button)
            time.sleep(0.3)

        except Exception as e:
            print(f"Ошибка при обработке пары #{index + 1}: {str(e)}")
            try:
                driver.execute_script("$('.modal').modal('hide');")
            except:
                pass
            continue

    return schedule_data

# Создаем функцию сканирования всего семестра для одной группы
def parse_group_schedule(group_name, group_url, start_week, end_week):
    print(f"\nНачинаем парсинг группы: {group_name}")

    driver = webdriver.Chrome(options=options)
    driver.get(group_url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.task, .pairs-list, .schedule-item")))
        print("Элементы найдены!")
    except:
        print("Элементы не загрузились. Проверьте селекторы или время ожидания.")

    all_schedule_data = []

    if not navigate_to_week(driver, start_week):
        print(f"Не удалось перейти на начальную неделю {start_week}")
        return all_schedule_data

    current_week = start_week
    while current_week <= end_week:
        print(f"\nОбработка {current_week} недели...")

        try:
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.task")))
                pairs_exist = True
            except:
                pairs_exist = False
                print(f"На {current_week} неделе пар не найдено")

            if pairs_exist:
                week_data = parse_current_week_schedule(driver, group_name)

                if week_data:
                    for item in week_data:
                        item['Неделя'] = current_week
                    all_schedule_data.extend(week_data)
                    print(f"Добавлено {len(week_data)} пар с {current_week} недели")
                else:
                    print(f"На {current_week} неделе нет подходящих пар")

            if current_week < end_week:
                print(f"Пытаемся перейти с недели {current_week} на {current_week + 1}")

                if navigate_to_week(driver, current_week + 1):
                    new_week = get_current_week(driver)
                    if new_week == current_week + 1:
                        current_week += 1
                    else:
                        print(f"Не удалось подтвердить переход. Остаемся на неделе {current_week}")
                        break
                else:
                    print(f"Не удалось перейти на неделю {current_week + 1}. Прерываем обработку.")
                    break
            else:
                print("Достигнута конечная неделя. Завершаем обработку.")
                break

        except Exception as e:
            print(f"Критическая ошибка на {current_week} неделе: {str(e)}")
            break

    driver.quit()
    return all_schedule_data

def parse_all_groups(groups_dict, start_week, end_week):
    # Создаем папку для сохранения CSV файлов
    if not os.path.exists('../../schedules'):
        os.makedirs('../../schedules')

    # Создаем пустой DataFrame для всех данных
    all_data = pd.DataFrame()

    for group_name, group_url in groups_dict.items():
        try:
            print(f"\nНачинаем обработку группы: {group_name}")
            group_data = parse_group_schedule(group_name, group_url, start_week, end_week)

            if group_data:
                # Преобразуем данные группы в DataFrame
                group_df = pd.DataFrame(group_data)
                # Добавляем к общим данным
                all_data = pd.concat([all_data, group_df], ignore_index=True)
                print(f"Данные группы {group_name} добавлены в общий набор")
            else:
                print(f"Для группы {group_name} не удалось получить данные")

        except Exception as e:
            print(f"Ошибка при обработке группы {group_name}: {str(e)}")
            continue

    # Сохраняем все данные один раз в конце
    if not all_data.empty:
        all_data.to_csv("all_groups.csv", index=False, encoding='utf-8-sig')
        print("\nВсе данные сохранены в файл 'all_groups.csv'")
    else:
        print("\nНе удалось получить данные ни для одной группы")

    print("\nПарсинг завершен")

# Запускаем парсинг всех групп
parse_all_groups(groups_to_parse, start_week=21, end_week=44)

# Качаем
from google.colab import files
files.download("all_groups.csv")