import data, datetime, requests, time
from lxml.html import fromstring
from time import sleep

def log(comment):
    print(str(datetime.datetime.now()), '\t', comment) #Ведение лога

def format_number(number):
    number = number.split(':')
    for i in range(len(number)):
        number[i] = str(int(number[i]))
    return ':'.join(number)

#Циклическое извлечение кадастровых номеров объектов недвижимости из файла
with open (data.INPUT_FILE, 'r', encoding = 'utf-8') as InputFile:
    COUNT = 1
    for Line in InputFile:
        Line = format_number(Line.replace('\n', ''))
        log(str(COUNT) + '\t' + Line)

        List = ['n/d' for x in range(8)]
        source = requests.get(f'https://pkk.rosreestr.ru/api/features/5/{Line}').json()
        try:
            List[0] = source['feature']['attrs']['cn'] #1. Кадастровый номер
            List[1] = source['feature']['attrs']['kvartal'] #2. Кадастровый квартал
            List[2] = source['feature']['attrs']['address'] #3. Адрес
            List[3] = source['feature']['attrs']['cad_cost'] #4. Кадастровая стоимость
            #print('5. Тип площади', source['feature'])
            #print('6. Категория земель', source['feature'])
            #print('7. Разрешенное использование', source['feature'])
            #print('8. По документу', source['feature'])
            List[4] = source['feature']['attrs']['oks_type']
            List[5] = source['feature']['attrs']['area_dev_type']
            List[6] = source['feature']['attrs']['purpose']
            List[7] = source['feature']['attrs']['area_value']
        except:
            List[0] = Line
            log('Error reading data!')

        with open(data.OUTPUT_FILE, 'a', encoding='utf-8') as OutputFile:
            for element in List:
                OutputFile.write(str(element) + '\t')
            OutputFile.write('\n')

        log('Done!')
        COUNT += 1

log('The program has been completed!')
