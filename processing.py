
import json

import xlrd
import openpyxl

ABBREVIATIONS = {
"основы безопасности и защиты родины":"ОБЗР",
"физическая культура":"Физкультура"
}

def processing(filename):
    
    # Получение ячеек с уроками
    cells, monday = get_cells(filename)
    
    # Чтение json с расписанием звонков
    # В понедельник другое расписание 
    with open("calls.json", "r", encoding="utf-8") as file:
        json_file = json.load(file)
        calls = json_file['monday' if monday else 'main']

    lessons = []
    
    date = cells[0]
    date = (f'📅  {date}')
    lessons.append(date)
    lessons.append('')
    
    # Обработка уроков
    for i, lesson in enumerate(cells):
        if i > 0:
            
            parts = [p.strip() for p in lesson.split(',')]
            number = lesson.split('.', 1)[0]
            subject = (parts[0])[3:].strip()
            subject = ABBREVIATIONS.get(subject.lower(), subject)
            room = parts[2]
            call = calls[number]
            
            lessons.append(f'🔹{number}. ({call}) - {subject}, {room}')  
            
    # Финальная обработка сообщения
    final_msg = ''
    for i, item in enumerate(lessons, start=1):
        final_msg += item+'\n'
        if i%2 == 0:
            final_msg += '-- -- -- -- -- -- -- -- -- -- --'+'\n'

    return final_msg



def get_cells(filename):
    
    if filename.endswith(".xlsx"):
        # Сбор данных специфичных для библиотеки openpyxl

        # Чтение значений ячеек в столбце 'S' (группа 516В)
        # В первые 3 ячейки не заносится расписание
        excel = openpyxl.load_workbook(filename)
        page = excel.active  
        col = [x.value for x in page['S'][3:]]

        # Поиск склеенных ячеек в 19 столбце ('S')
        first_merged = []
        last_merged = []

        for cell in page.merged_cells.ranges:
            if cell.min_col == 19 and cell.max_col == 19:
                first_merged.append(cell.min_row)
                last_merged.append(cell.max_row)

        # Получение даты, в понедельник она на 1 ячейку ниже
        monday = False
        date = page["A4"].value
        
        if not date:
            date = page["A5"].value
            monday = True

    
    elif filename.endswith(".xls"):
        # Сбор данных специфичных для библиотеки xlrd

        # В данной библиотеке ячейки считаются по индексам
        # Чтение значений ячеек в 19 столбце ('S')
        excel = xlrd.open_workbook(filename, formatting_info=True)
        page=excel.sheet_by_index(0)
        col = page.col_values(18, start_rowx=3)
        
        # Поиск склеенных ячеек в 19 столбце ('S')
        first_merged = []
        last_merged = []

        for (row_first, row_last, col_first, col_last) in page.merged_cells:
            if col_first == 18 and col_last == 19:
                first_merged.append(row_first+1)
                last_merged.append(row_last)
    
        # Получение даты, в понедельник она на 1 ячейку ниже
        monday = False
        date = page.cell_value(3, 0)
        
        if not date:
            date = page.cell_value(4, 0)
            monday = True

    # Обработка ячеек
    # num - Фактический номер урока, т.к. при пропуске Разговоров о важном к i прибавляется 1
    lessons = [date,]
    num=1
    current_lesson = ''
    merged = False

    for i, lesson in enumerate(col, start=1):

        # Пропуск разговоров о важном в понедельник
        if monday and i in (1,8):
            continue

        # Проверка наличия урока в ячейке
        if lesson not in (None, ''):
            if i+3 in first_merged:
                merged = True
            current_lesson = (lesson).replace('\n', '')
            lessons.append(f"{num}. {current_lesson}")
            num+=1

        # Дублирование урока в склеенной ячейке
        elif merged:
            lessons.append(f'{num}. {current_lesson}')
            if i+3 in last_merged:
                merged = False
            num += 1
        
        # Продолжение счетчика уроков при пустой ячейке
        else:
            num+=1

    return (lessons, monday)


