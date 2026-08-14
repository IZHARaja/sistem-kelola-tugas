import os
import zipfile
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape


SISWA_HEADERS = ['NIS', 'EMAIL', 'NAMA_LENGKAP', 'KELAS', 'ANGKATAN']
GURU_HEADERS = ['NIP', 'EMAIL', 'NAMA_LENGKAP', 'MATA_PELAJARAN', 'STATUS_PEGAWAI']

_XML_NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
_REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'


def _normalize_spaces(value):
    return ' '.join((value or '').strip().split())


def normalize_identifier(value):
    return ''.join(_normalize_spaces(value).split()).upper()


def normalize_email(value):
    return _normalize_spaces(value).lower()


def normalize_name(value):
    return _normalize_spaces(value)


def _column_letter(index):
    label = ''
    while index:
        index, remainder = divmod(index - 1, 26)
        label = chr(65 + remainder) + label
    return label


def _column_index(cell_reference):
    letters = ''.join(character for character in (cell_reference or '') if character.isalpha())
    index = 0
    for character in letters:
        index = index * 26 + (ord(character.upper()) - 64)
    return index


def _build_sheet_xml(rows):
    row_xml = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for column_index, value in enumerate(row, start=1):
            cell_reference = f'{_column_letter(column_index)}{row_index}'
            cell_value = escape(str(value or ''))
            cells.append(
                f'<c r="{cell_reference}" t="inlineStr"><is><t>{cell_value}</t></is></c>'
            )
        row_xml.append(f'<row r="{row_index}">' + ''.join(cells) + '</row>')

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetData>'
        + ''.join(row_xml) +
        '</sheetData>'
        '</worksheet>'
    )


def write_registry_workbook(file_path, headers, rows=None, sheet_name='Data Resmi'):
    rows = rows or []
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    workbook_rows = [headers, *[[row.get(header, '') for header in headers] for row in rows]]

    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''

    package_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''

    workbook_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="{escape(sheet_name)}" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>'''

    workbook_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''

    styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="1"><fill><patternFill patternType="none"/></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''

    core_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:creator>GitHub Copilot</dc:creator>
  <cp:lastModifiedBy>GitHub Copilot</cp:lastModifiedBy>
</cp:coreProperties>'''

    app_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Excel</Application>
</Properties>'''

    with zipfile.ZipFile(file_path, 'w', compression=zipfile.ZIP_DEFLATED) as workbook:
        workbook.writestr('[Content_Types].xml', content_types)
        workbook.writestr('_rels/.rels', package_rels)
        workbook.writestr('xl/workbook.xml', workbook_xml)
        workbook.writestr('xl/_rels/workbook.xml.rels', workbook_rels)
        workbook.writestr('xl/worksheets/sheet1.xml', _build_sheet_xml(workbook_rows))
        workbook.writestr('xl/styles.xml', styles_xml)
        workbook.writestr('docProps/core.xml', core_xml)
        workbook.writestr('docProps/app.xml', app_xml)


def _read_shared_strings(workbook):
    if 'xl/sharedStrings.xml' not in workbook.namelist():
        return []

    root = ET.fromstring(workbook.read('xl/sharedStrings.xml'))
    values = []
    for entry in root.findall(f'{{{_XML_NS}}}si'):
        text_parts = [node.text or '' for node in entry.findall(f'.//{{{_XML_NS}}}t')]
        values.append(''.join(text_parts))
    return values


def read_registry_rows(file_path):
    if not os.path.exists(file_path):
        return []

    with zipfile.ZipFile(file_path, 'r') as workbook:
        shared_strings = _read_shared_strings(workbook)
        sheet_root = ET.fromstring(workbook.read('xl/worksheets/sheet1.xml'))

    parsed_rows = []
    for row in sheet_root.findall(f'.//{{{_XML_NS}}}row'):
        values = {}
        for cell in row.findall(f'{{{_XML_NS}}}c'):
            column_index = _column_index(cell.attrib.get('r'))
            cell_type = cell.attrib.get('t')
            value = ''
            if cell_type == 'inlineStr':
                value = ''.join(node.text or '' for node in cell.findall(f'.//{{{_XML_NS}}}t'))
            else:
                raw_value = cell.find(f'{{{_XML_NS}}}v')
                if raw_value is not None and raw_value.text is not None:
                    if cell_type == 's':
                        shared_index = int(raw_value.text)
                        value = shared_strings[shared_index] if shared_index < len(shared_strings) else ''
                    else:
                        value = raw_value.text
            values[column_index] = value

        if not values:
            continue
        max_column = max(values)
        parsed_rows.append([values.get(index, '') for index in range(1, max_column + 1)])

    if not parsed_rows:
        return []

    headers = [normalize_name(header).upper() for header in parsed_rows[0]]
    records = []
    for row in parsed_rows[1:]:
        record = {headers[index]: (row[index] if index < len(row) else '') for index in range(len(headers))}
        if any(normalize_name(value) for value in record.values()):
            records.append(record)
    return records


def append_registry_row(file_path, headers, row_data):
    rows = read_registry_rows(file_path)
    rows.append({header: row_data.get(header, '') for header in headers})
    write_registry_workbook(file_path, headers, rows)


def ensure_registry_templates(config):
    folder_path = config['OFFICIAL_DATA_FOLDER']
    os.makedirs(folder_path, exist_ok=True)

    template_files = (
        (config['SISWA_REGISTRY_FILE'], SISWA_HEADERS, 'Data Siswa Resmi'),
        (config['GURU_REGISTRY_FILE'], GURU_HEADERS, 'Data Guru Resmi'),
    )
    for file_path, headers, sheet_name in template_files:
        if not os.path.exists(file_path):
            write_registry_workbook(file_path, headers, sheet_name=sheet_name)


def _match_record(record, identifier_key, identifier, email, full_name):
    return (
        normalize_identifier(record.get(identifier_key, '')) == normalize_identifier(identifier)
        and normalize_email(record.get('EMAIL', '')) == normalize_email(email)
        and normalize_name(record.get('NAMA_LENGKAP', '')).casefold() == normalize_name(full_name).casefold()
    )


def validate_official_registry(config, role, identifier, email, full_name):
    role_label = 'siswa' if role == 'mahasiswa' else 'guru'
    file_path = config['SISWA_REGISTRY_FILE'] if role == 'mahasiswa' else config['GURU_REGISTRY_FILE']
    identifier_key = 'NIS' if role == 'mahasiswa' else 'NIP'
    rows = read_registry_rows(file_path)

    if not rows:
        return False, f'Data {role_label} resmi sekolah belum tersedia. Isi file Excel master terlebih dahulu.'

    for record in rows:
        if _match_record(record, identifier_key, identifier, email, full_name):
            return True, ''

    return False, f'Data {role_label} tidak ditemukan pada database resmi sekolah.'