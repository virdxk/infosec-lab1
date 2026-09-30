from pathlib import Path
import re

from gost_report import Report, TitleConfig
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parents[1]
report = Report(TitleConfig(
    work_type="Лабораторная работа",
    work_number="№ 1",
    topic="Разработка защищенного REST API с интеграцией в CI/CD",
    student_name="Елисеев Константин Иванович",
    student_group="P3308",
    year="2026",
    university_short=" ",
    faculty="Дисциплина: Информационная безопасность",
    university_full=("Федеральное государственное автономное образовательное учреждение "
                     "высшего образования «Национальный исследовательский университет ИТМО»"),
), project_root=ROOT)


def text(value):
    value = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'\1 (\2)', value)
    return value.replace('**', '').replace('`', '').replace(' — ', ', ').replace('–', '-')


def append_markdown(path):
    lines = path.read_text().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('```'):
            code=[]
            i+=1
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i]); i+=1
            before = len(report._doc.paragraphs)
            report.code('\n'.join(code))
            for paragraph in report._doc.paragraphs[before:-1]:
                paragraph.paragraph_format.keep_with_next = True
        elif line.startswith('|'):
            rows=[]
            while i < len(lines) and lines[i].startswith('|'):
                cells=[text(c.strip()) for c in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r'[: -]+',c) for c in cells):
                    rows.append(cells)
                i+=1
            report.table(rows, caption="Параметры и назначение")
            report._doc.paragraphs[-1].paragraph_format.keep_with_next = True
            table = report._doc.tables[-1]
            table.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            for row in table.rows[:-1]:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        paragraph.paragraph_format.keep_with_next = True
            continue
        elif line.startswith('!['):
            match=re.fullmatch(r'!\[([^]]+)\]\(([^)]+)\)',line)
            report.figure(ROOT / match[2], text(match[1]), width_cm=15)
        elif line.startswith('### '):
            report.h3(text(line[4:]))
        elif line.startswith('## '):
            report.h2(text(line[3:]))
        elif line.startswith('# '):
            pass
        elif line.strip():
            report.text(text(line))
        i+=1


report.h1("Описание и результаты работы")
report.text("Цель: разработать API с защитой от SQL-инъекций, экранированием данных и аутентификацией JWT; включить тесты и сканеры безопасности в CI.")
report.text("Ниже приведено содержимое README проекта. Команды, меры защиты и результаты относятся к лабораторной № 1.")
append_markdown(ROOT / 'README.md')
report.h1("Проверка HTTP-запросов")
append_markdown(ROOT / 'docs/curl-session.md')
report.h1("Вывод")
report.text("Реализованы вход, чтение данных и создание постов. SQLAlchemy отделяет параметры от SQL, bcrypt хранит хэши паролей, middleware проверяет JWT, пользовательский текст экранируется при выдаче. Проверка зависимостей выявила уязвимую версию PyJWT; после обновления повторный аудит и тесты аутентификации прошли.")
report.text("Состояние удалённого CI указано в разделе результатов. Исторические скриншоты не заменяют подтверждение запуска для окончательной версии.")
report.save(ROOT / 'docs/report.docx')
