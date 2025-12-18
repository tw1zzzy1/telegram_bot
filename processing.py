import json

import xlrd
from openpyxl import load_workbook

def processing(filename):
    
    if filename.endswith('.xls'):
        result, monday=process_xls(filename)
    elif filename.endswith('.xlsx'):
        result, monday=process_xlsx(filename)

    with open("calls.json", "r", encoding="utf-8") as file:
        json_file = json.load(file)
        calls = json_file['monday' if monday else 'main']

    formatted = [result[0],'']
    for i, lesson in enumerate(result):
        if i > 0:

            parts = [p.strip() for p in lesson.split(',')]
            number = lesson.split('.', 1)[0]
            subject = (parts[0])[3:].lstrip()
            room=parts[2]
            call = calls[number]
            
            formatted.append(f'🔹 {number}. ({call}) - {subject}, {room}')  
            
    final_msg = ''
    for i, item in enumerate(formatted, start=1):
        final_msg += item+'\n'
        if i%2 == 0:
            final_msg += '-- -- -- -- -- -- -- -- -- -- --'+'\n'

    return final_msg

def process_xls(filename):
    excel = xlrd.open_workbook(filename, formatting_info=True)
    page=excel.sheet_by_index(0)
    col = page.col_values(18, start_rowx=5)

    cells=[]
    for (row_first, row_last, col_first, col_last) in page.merged_cells:
        if col_first == 18 and col_last == 19:
            cells.extend(range(row_first+1,row_last+1))
   
    monday = None
    date = page.cell_value(4, 0)
    if not date:
        date = page.cell_value(5, 0)
        monday = True

    lessons = [date,]
    num=1
    for i, lesson in enumerate(col, start=1):
        if lesson.strip():
            clean_lesson= lesson.replace('\n','')
            lessons.append(f"{num}. {clean_lesson}")
            num+=1
        elif monday and i in (8,1):
            continue
        elif (not lesson.strip()) and ((i+3) in cells):
            lessons.append(f"{num}.{lessons[-1].split('.', 1)[1]}")
            num+=1
        else:
            num+=1

    return (lessons, monday)

def process_xlsx(filename):
    excel = load_workbook(filename)
    page = excel.active  
    col = page['S'][3:]

    cells=[]
    for cell in page.merged_cells.ranges:
        if cell.min_col == 19 and cell.max_col == 19:
            for row in range(cell.min_row, cell.max_row + 1):
                if row >= 4:
                    cells.append(row)
    
    monday = None
    date = page['A4'].value
    if not date:
        date = page['A5'].value
        monday = True

    lessons=[date,]
    num=1
    for i,lesson in enumerate(col, start=1):
        if lesson.value:
            clean_lesson = (lesson.value).replace('\n','')
            lessons.append(f"{num}. {clean_lesson}")
            num+=1
        elif monday and i in (8,1):
            continue
        elif (not lesson.value) and ((i+3) in cells):
            lessons.append(f"{num}.{lessons[-1].split('.', 1)[1]}")
            num+=1
        else:
            num+=1
    
    return (lessons, monday)


