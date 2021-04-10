import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from lxml.html import fromstring

MAIN_PAGE = 'https://rosreestr.gov.ru/wps/portal/p/cc_ib_portal_services/online_request/'
TO_FIND = ['Кадастровый номер:', 'Адрес (местоположение):', '(ОКС) Тип:', 'Площадь ОКС\'a:', 'Кадастровая стоимость:', 'Дата обновления информации:', 'Статус объекта:', 'Дата постановки на кадастровый учет:', 'Дата внесения стоимости:', 'Дата определения стоимости:']
DICT = {'Кадастровый номер:':'0', 'Адрес (местоположение):':'1', '(ОКС) Тип:':'2', 'Площадь ОКС\'a:':'3', 'Кадастровая стоимость:':'4', 'Дата обновления информации:':'5', 'Статус объекта:':'6', 'Дата постановки на кадастровый учет:':'7', 'Дата внесения стоимости:':'8', 'Дата определения стоимости:':'9'}

def log(comment):
    print(str(datetime.datetime.now()), '\t', comment) #Ведение лога

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

#Форматирование "некрасивых" строк
def format(string):
    string = string.replace('\n', '').replace('\xa0', ' ').split(' ')
    while '' in string:
        for char in range(len(string)):
            if string[char] == '':
                del string[char]
                break
    return ' '.join(string)

#Сбор данных со страницы
def collect_data(source):
    List = ['n/d' for a in range(10)]
    try:
        _count = len(source.xpath('//*[@id="layoutContainers"]/div[4]/div/div[2]/section/div[2]/div[2]/table/tbody/tr[5]/td/table/tbody/text()'))
        for i in range(1, _count + 1):
            try:
                try:
                    key = source.xpath(f'//*[@id="layoutContainers"]/div[4]/div/div[2]/section/div[2]/div[2]/table/tbody/tr[5]/td/table/tbody/tr[{i}]/td[1]/nobr/text()')[0]
                except:
                    key = source.xpath(f'//*[@id="layoutContainers"]/div[4]/div/div[2]/section/div[2]/div[2]/table/tbody/tr[5]/td/table/tbody/tr[{i}]/td[1]/text()')[0]
                key = format(key)
                value = format(source.xpath(f'//*[@id="layoutContainers"]/div[4]/div/div[2]/section/div[2]/div[2]/table/tbody/tr[5]/td/table/tbody/tr[{i}]/td[2]/b/text()')[0])
                for _key in TO_FIND:
                    if _key in key:
                        List[int(DICT[_key])] = value
            except:
                pass

        _count = len(source.xpath('//*[@id="r_enc"]/table/tbody/text()'))
        for i in range(3, _count + 1, 2):
            try:
                key_law = format(source.xpath(f'//*[@id="r_enc"]/table/tbody/tr[{i}]/td[1]/text()')[0])
                if key_law == '':
                    key_law += 'n/d'  
                List += [key_law]
            except:
                pass
            try:
                count_ = len(source.xpath(f'//*[@id="r_enc"]/table/tbody/tr[{i}]/td[2]/table/tbody/text()'))
                key_restriction = ''
                if count_ == 0:
                    key_restriction += 'n/d'
                elif count_ == 1:
                    key_restriction += format(source.xpath(f'//*[@id="r_enc"]/table/tbody/tr[{i}]/td[2]/table/tbody/tr/td/text()')[0])
                else:
                    for j in range(1, count_ + 1):
                        key_restriction += format(source.xpath(f'//*[@id="r_enc"]/table/tbody/tr[{i}]/td[2]/table/tbody/tr[{j}]/td/text()')[0]) + '; '
                List += [key_restriction]
            except:
                pass
    except:
        log('Incorrect page!')
    return List


#Отправка запроса
def execute_request(number):
    try:
        inputField = wait_element('//*[@id="online_request_search_form_span"]/table/tbody/tr[1]/td[1]/table/tbody/tr[3]/td/table[1]/tbody/tr[2]/td[3]/input')
        inputField.clear()
        inputField.send_keys(number)
        driver.find_element_by_xpath('//*[@id="submit-button"]').send_keys(Keys.RETURN)
        log('Sending request!')
        sleep(1)
        try:
            wait_element('//*[@id="js_oTr0"]/td[1]/a').click()
            source = fromstring(driver.page_source)
            log('Data found!')

            List = collect_data(source)

            sleep(1)
        except:
            log('Data not found!')
    except:
        log('Error sending request!')
    return List

driver = startChrome() #Запуск браузера
driver.get(MAIN_PAGE) #Переход на веб-страницу ранее упомняутого сервиса
log('Page loaded!')

#Циклическое извлечение кадастровых номеров объектов недвижимости из файла
with open ('numbers.txt', 'r', encoding = 'utf-8') as File:
    COUNT = 1
    for Line in File:
        log(Line.replace('\n', ''))
        List = execute_request(Line.replace('\n', ''))

        with open('Output.txt', 'a', encoding='utf-8') as OutputFile:
            for element in List:
                OutputFile.write(str(element) + '\t')
            OutputFile.write('\n')

        log('Done!')
        try:
            wait_element('//*[@id="js_es_1"]').click()
        except:
            log('No button!')
        COUNT += 1

driver.close()#Закрыте браузера после завершения цикла 
log('The program has been completed!')