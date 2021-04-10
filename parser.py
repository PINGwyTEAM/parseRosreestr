import numpy as np
import time, datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from lxml import html

MAIN_PAGE = 'https://rosreestr.gov.ru/wps/portal/p/cc_ib_portal_services/online_request/'
TO_FIND = ['Кадастровый номер:', 'Адрес (местоположение):', '(ОКС) Тип:', 'Площадь ОКС\'a:', 'Кадастровая стоимость:', 'Дата обновления информации:', 'Статус объекта:', 'Дата постановки на кадастровый учет:', 'Дата внесения стоимости:', 'Дата определения стоимости:']
DICT = {'Кадастровый номер:':'0', 'Адрес (местоположение):':'1', '(ОКС) Тип:':'2', 'Площадь ОКС\'a:':'3', 'Кадастровая стоимость:':'4', 'Дата обновления информации:':'5', 'Статус объекта:':'6', 'Дата постановки на кадастровый учет:':'7', 'Дата внесения стоимости:':'8', 'Дата определения стоимости:':'9'}
List = ['n/d' for a in range(10)]

#Запуск Хрома
def startChrome():
    chrome_options = Options()
    driver = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)
    driver.set_page_load_timeout(30)
    WebDriverWait(driver, 2)
    return driver

#Отправка запросов для нажатия кнопок
def wait_element (path):
    try:
        WebDriverWait(driver, timeout=30, poll_frequency=1.5).until(EC.presence_of_element_located((By.XPATH, path)))
    except:
        driver.refresh()
    return driver.find_element_by_xpath(path)

def format(string):
    while '' in string:
        for char in range(len(string)):
            if string[char] == '':
                del string[char]
                break
    return ' '.join(string)

#Сбор данных со страницы
def collect_data(source):  
    global List
    try:
        _count = len(source.xpath('//*[@id="layoutContainers"]/div[4]/div/div[2]/section/div[2]/div[2]/table/tbody/tr[5]/td/table/tbody/text()')) + 1
        for i in range(_count):
            try:
                try:
                    key = source.xpath(f'//*[@id="layoutContainers"]/div[4]/div/div[2]/section/div[2]/div[2]/table/tbody/tr[5]/td/table/tbody/tr[{i}]/td[1]/nobr/text()')[0].replace('\n', '').split(' ')
                except:
                    key = source.xpath(f'//*[@id="layoutContainers"]/div[4]/div/div[2]/section/div[2]/div[2]/table/tbody/tr[5]/td/table/tbody/tr[{i}]/td[1]/text()')[0].replace('\n', '').split(' ')
                key = format(key)
                value = format(source.xpath(f'//*[@id="layoutContainers"]/div[4]/div/div[2]/section/div[2]/div[2]/table/tbody/tr[5]/td/table/tbody/tr[{i}]/td[2]/b/text()')[0].replace('\n', '').split(' '))
                for _key in TO_FIND:
                    if _key in key:
                        List[int(DICT[_key])] = value
            except:
                pass
    except:
        print(str(datetime.datetime.now()), '\t', 'Incorrect page!') #Ведение лога
    List += collect_data_2(source)
    return List

# Собирает Право и Ограничения
def collect_data_2(source):
    try:
        _count = len(source.xpath('//*[@id="r_enc"]/table/tbody/text()')) + 1
        law = ''
        restriction = ''
        for i in range(3, _count):
            try:
                key_law = source.xpath(f'//*[@id="r_enc"]/table/tbody/tr[{i}]/td[1]/text()')[0].replace('\n', '').split(' ')
                if key_law != '':
                    law += format(key_law) + '; '
            except:
                pass
            try:
                key_restriction = source.xpath(f'//*[@id="r_enc"]/table/tbody/tr[{i}]/td[2]/text()')[0].replace('\n', '').split(' ')
                if key_restriction != '':
                    restriction += format(key_restriction) + '; '
            except:
                pass
    except:
        print(str(datetime.datetime.now()), '\t', 'Incorrect page!') #Ведение лога
    if law == '':
        law = 'n/d'
    if restriction == '':
        restriction = 'n/d'
    return [law, restriction]


#Отправления запроса
def execute_request(number):
    try:
        inputField = wait_element('//*[@id="online_request_search_form_span"]/table/tbody/tr[1]/td[1]/table/tbody/tr[3]/td/table[1]/tbody/tr[2]/td[3]/input')
        inputField.clear()
        inputField.send_keys(number)
        driver.find_element_by_xpath('//*[@id="submit-button"]').send_keys(Keys.RETURN)
        print(str(datetime.datetime.now()), '\t', 'Sending request!') #Ведение лога
        time.sleep(1)
        try:
            wait_element('//*[@id="js_oTr0"]/td[1]').click()
            source = html.fromstring(driver.page_source)          
            print(str(datetime.datetime.now()), '\t', 'Data found!') #Ведение лога

            List = collect_data(source)

            time.sleep(1)
        except:
            print(str(datetime.datetime.now()), '\t', 'Data not found!') #Ведение лога
    except:
        print(str(datetime.datetime.now()), '\t', 'Error sending request!') #Ведение лога
    return List

#запускаем браузер
driver = startChrome() 
#переходим на веб-страницу ранее упомняутого сервиса
driver.get(MAIN_PAGE) 
print(str(datetime.datetime.now()), '\t', 'Page loaded!') #Ведение лога

#циклически извлекаем кадастровые номера объектов недвижимости из списка
with open ('numbers.txt', 'r', encoding = 'utf-8') as File:
    COUNT = 1
    for Line in File:
        print(str(datetime.datetime.now()), '\t', COUNT, '\t', Line.replace('\n', '')) #Ведение лога
        List = execute_request(Line.replace('\n', ''))

        with open('Output.txt', 'a', encoding='utf-8') as OutputFile:
            for element in List:
                OutputFile.write(str(element) + '\t')
            OutputFile.write('\n')

        print(str(datetime.datetime.now()), '\t', 'Done!') #Ведение лога
        try:
            wait_element('//*[@id="js_es_1"]').click()
        except:
            print(str(datetime.datetime.now()), '\t', 'No button!') #Ведение лога
        COUNT += 1

#по завершению цикла закрыть браузер
driver.close()