import os
import random
import os
import doctest
import io
import sys
from datetime import datetime
import numpy as np
import math

global DATAFILE
global TESTDATAFILE
global LOAD_EMPLOYMENT

def test_datafile(datafile, testdatafile):
    global DATAFILE
    DATAFILE = datafile
    global TESTDATAFILE
    TESTDATAFILE = testdatafile
    assert os.path.exists(datafile), f"Data file {datafile} does not exist"
    assert os.path.exists(testdatafile), f"Test data file {testdatafile} does not exist"
    print('OK. Los ficheros están en su sitio. Puedes continuar')


def test_gen_sample(gen_sample):
    def test(size):
        ok = False
        max_attempts = 5
        attempts = 0
        random.seed(42)  # Ensure reproducibility
        while not ok and attempts < max_attempts:
            gen_sample(DATAFILE, size)
            n = round(size*100)
            new_file = DATAFILE.replace('.csv', f'_{n:02}.csv')
            assert new_file in os.listdir(), f"Sample file for {new_file} size {size} not found"
            with open(new_file, 'r', encoding="utf-8-sig") as f:
                header_new = f.readline()
            with open(DATAFILE, 'r', encoding="utf-8-sig") as f:
                header_full = f.readline()
            assert header_new == header_full, f"Header mismatch in {new_file}"
            fullsize = os.path.getsize(DATAFILE)
            samplesize = os.path.getsize(new_file)
            ok = fullsize*size*0.9 <= samplesize <= fullsize*size*1.1
            attempts += 1
        print("test_gen_sample", size, attempts)
        assert ok, f"Sample size {size} does not match expected size in {new_file}"
        print(f"Sample size {size} OK")

    for size in [0.01, 0.02, 0.05, 0.1]:
        test(size)


def test_gen_sample_checks(gen_sample):
    ok = False
    try:
        gen_sample(DATAFILE, 1.2)
    except:
        ok = True
    assert ok, "gen_sample should raise an error for size > 1"

    ok = False
    try:
        gen_sample(DATAFILE, -1)
    except:
        ok = True
    assert ok, "gen_sample should raise an error for size < 0"
    print("check ratio values OK")

def test_gen_sample_typehints(gen_sample):
    assert gen_sample.__annotations__, 'The function does not have type hints'
    assert set(gen_sample.__annotations__.values()) == {str, float, None}
    print("check type hints OK")

def test_docstring(fun):
    assert fun.__doc__, 'The function does not have a docstring'
    assert len(fun.__doc__) > 30, 'The docstring is too short'
    print("docstring OK")


def test_doctests(fun, globals):
    finder = doctest.DocTestFinder()
    assert len(finder.find(fun)) > 0, 'No doctests found in the function'
    out = io.StringIO()
    stdout = sys.stdout
    try:
        sys.stdout = out
        doctest.run_docstring_examples(fun, globals)
    finally:
        sys.stdout = stdout
    assert len(out.getvalue()) == 0, f"Doctest output:\n{out.getvalue()}"
    print("doctests OK")


def test_str2int(str2int):
    def test(fun, s, expected) -> None:
        """
        Test the str2int function from empleo.py
        """
        n = fun(s)
        assert  n == expected, f"Expected {expected} for input {s}, but got {n}"

    for t in [("123", 123),
              ("0", 0),
              ("abc", 0)]:
        test(str2int, *t)

    print("str2int OK")

def test_str2int_typehints(str2int):
    assert str2int.__annotations__, 'The function does not have type hints'
    assert set(str2int.__annotations__.values()) == {str, int}
    print(f"{str2int.__name__} type hints OK")


def test_str2dt(fun):
    def test(fun, s, expected):
        d = fun(s)
        assert d == expected, f"Expected {expected} for input {s}, but got {d}"
    for t in [("", datetime(1970, 1, 1)),
              ("2025-08-07 00:11:57.897", datetime(2025, 8, 7, 0, 11, 57, 897000))]:
        test(fun, *t)
        print(f"{fun.__name__} OK")

def test_str2dt_typehints(fun):
    assert fun.__annotations__, 'The function does not have type hints'
    assert set(fun.__annotations__.values()) == {str, datetime}
    print(f"{fun.__name__} type hints OK")

def test_str2ym(str2ym):
    def test(str2ym, s, expected):
        """
        Test the str2ym function from empleo.py
        """
        dt = str2ym(s)
        assert dt == expected, f"Expected {expected} for input {s}, but got {dt}"

    for t in [("ene-24", datetime(2024, 1, 1)),
              ("feb-25", datetime(2025, 2, 1)),
              ("mar-23", datetime(2023, 3, 1)),
              ("abr-22", datetime(2022, 4, 1)),
              ("may-21", datetime(2021, 5, 1)),
              ("jun-20", datetime(2020, 6, 1)),
              ("jul-19", datetime(2019, 7, 1)),
              ("ago-18", datetime(2018, 8, 1)),
              ("sep-17", datetime(2017, 9, 1)),
              ("oct-16", datetime(2016, 10, 1)),
              ("nov-15", datetime(2015, 11, 1)),
              ("dic-14", datetime(2014, 12, 1)),
              ("", datetime(1970, 1, 1))
              ]:
        test(str2ym, *t)

def test_str2ym_typehints(str2ym):
    assert str2ym.__annotations__, 'The function does not have type hints'
    assert set(str2ym.__annotations__.values()) == {str, datetime}
    print("str2ym type hints OK")


def test_add_row(fun):
    data = {"FECHA_INSCRIPCION": [],
            "GENERO_DESC": [],
            "DISTRITO_COD": [],
            "DISTRITO_DESC": [],
            "EDAD": [],
            "NACIONALIDAD_DESC": [],
            "OBJETIVOPROFESIONAL1_COD": [],
            "OBJETIVOPROFESIONAL1_DESC": [],
            "OBJETIVOPROFESIONAL2_COD": [],
            "OBJETIVOPROFESIONAL2_DESC": [],
            "OBJETIVOPROFESIONAL3_COD": [],
            "OBJETIVOPROFESIONAL3_DESC": [],
            "FX_CARGA": []
            }
    row = {'DISTRITO_COD': '10',
           'DISTRITO_DESC': ' LATINA',
           'EDAD': '34',
           'FECHA_INSCRIPCION': 'ene-24',
           'FX_CARGA': '2025-08-07 00:11:57.897',
           'GENERO_DESC': 'Hombre',
           'NACIONALIDAD_DESC': 'Español',
           'OBJETIVOPROFESIONAL1_COD': '5833',
           'OBJETIVOPROFESIONAL1_DESC': 'Conserjes de edificios',
           'OBJETIVOPROFESIONAL2_COD': '5220',
           'OBJETIVOPROFESIONAL2_DESC': 'Vendedores en tiendas y almacenes',
           'OBJETIVOPROFESIONAL3_COD': '9602',
           'OBJETIVOPROFESIONAL3_DESC': 'Peones de la construcción de edificios'}
    fun(data, row)
    for k in data:
        assert len(data[k]) == 1, f"Expected 1 entry in {k}, got {len(data[k])}"
    assert data["EDAD"][0] == 34, f"Expected age 34, got {data['EDAD'][0]}"
    assert data["FECHA_INSCRIPCION"][0] == datetime(2024, 1, 1), f"Expected date 2024-01-01, got {data['FECHA_INSCRIPCION'][0]}"
    assert data["FX_CARGA"][0] == datetime(2025, 8, 7, 0, 11, 57, 897000), f"Expected datetime 2025-08-07 00:11:57.897000, got {data['FX_CARGA'][0]}"
    assert data["DISTRITO_COD"][0] == 10, f"Expected district code 10, got {data['DISTRITO_COD'][0]}"
    assert data["DISTRITO_DESC"][0] == "LATINA", f"Expected district desc ' LATINA', got {data['DISTRITO_DESC'][0]}"
    print("add_row OK")
    row = {'DISTRITO_COD': '',
           'DISTRITO_DESC': ' LATINA',
           'EDAD': '',
           'FECHA_INSCRIPCION': '',
           'FX_CARGA': '',
           'GENERO_DESC': '',
           'NACIONALIDAD_DESC': '',
           'OBJETIVOPROFESIONAL1_COD': '',
           'OBJETIVOPROFESIONAL1_DESC': 'Conserjes de edificios',
           'OBJETIVOPROFESIONAL2_COD': '',
           'OBJETIVOPROFESIONAL2_DESC': 'Vendedores en tiendas y almacenes',
           'OBJETIVOPROFESIONAL3_COD': '',
           'OBJETIVOPROFESIONAL3_DESC': 'Peones de la construcción de edificios'}
    fun(data, row)
    for k in data:
        assert len(data[k]) == 2, f"Expected 2 entry in {k}, got {len(data[k])}"
    assert data["EDAD"][1] == 0, f"Expected age 0, got {data['EDAD'][1]}"
    assert data["FECHA_INSCRIPCION"][1] == datetime(1970, 1, 1), f"Expected date 1970-01-01, got {data['FECHA_INSCRIPCION'][1]}"
    assert data["FX_CARGA"][1] == datetime(1970, 1, 1), f"Expected datetime 1970-01-01 00:00:00, got {data['FX_CARGA'][1]}"
    assert data["DISTRITO_COD"][1] == 0, f"Expected district code 0, got {data['DISTRITO_COD'][1]}"
    assert data["DISTRITO_DESC"][1] == "LATINA", f"Expected district desc ' LATINA', got {data['DISTRITO_DESC'][1]}"
    print("add_row with missing values OK")

def test_add_row_typehints(fun):
    assert fun.__annotations__, 'The function does not have type hints'
    assert set(map(str, fun.__annotations__.values())) == {"<class '__main__.EmploymentData'>", 'None', 'dict[str, str]'}
    print("add_row type hints OK")

def test_load_employment(load_employment):
    global LOAD_EMPLOYMENT
    LOAD_EMPLOYMENT = load_employment
    data = load_employment(TESTDATAFILE)
    assert set(data.keys()) == {
        "FECHA_INSCRIPCION", "GENERO_DESC",
        "DISTRITO_COD", "DISTRITO_DESC",
        "EDAD", "NACIONALIDAD_DESC",
        "OBJETIVOPROFESIONAL1_COD", "OBJETIVOPROFESIONAL1_DESC",
        "OBJETIVOPROFESIONAL2_COD", "OBJETIVOPROFESIONAL2_DESC",
        "OBJETIVOPROFESIONAL3_COD", "OBJETIVOPROFESIONAL3_DESC", "FX_CARGA"}, \
        "Keys do not match expected keys"
    assert len(data['FECHA_INSCRIPCION']) == 1508,\
       f"Expected 1508 records, but got {len(data['FECHA_INSCRIPCION'])}"
    assert len([d for d in data['EDAD'] if d==0]) == 3, \
        'There should be 3 records with age 0:'
    assert data['EDAD'][8] == 0
    assert data['EDAD'][7] == 50
    assert len([d for d in data['DISTRITO_COD'] if d==0]) == 0, \
        "There are records with district_code 0"
    assert len([d for d in data['OBJETIVOPROFESIONAL1_COD'] \
                if d==0]) == 123, \
                   "There are 123 records with professional_objective1_code 0"
    print("load_employment OK")

def test_load_employment_typehints(load_employment):
    assert load_employment.__annotations__, 'The function does not have type hints'
    print(f"test: {set(map(str, load_employment.__annotations__.values()))}")
    assert set(map(str, load_employment.__annotations__.values())) == {"<class '__main__.EmploymentData'>", "<class 'str'>"}
    print("load_employment type hints OK")


def test_people_by_district(people_by_district):
    lst = LOAD_EMPLOYMENT(TESTDATAFILE)
    d = people_by_district(lst)
    assert d == [('OTRO MUNICIPIO', 268),
                ('PUENTE DE VALLECAS', 141),
                ('CARABANCHEL', 124),
                ('LATINA', 123),
                ('VILLAVERDE', 94),
                ('CIUDAD LINEAL', 90),
                ('VILLA DE VALLECAS', 73),
                ('USERA', 71),
                ('TETUÁN', 71),
                ('VICÁLVARO', 54),
                ('FUENCARRAL-EL PARDO', 50),
                ('CENTRO', 48),
                ('ARGANZUELA', 46),
                ('HORTALEZA', 45),
                ('MORATALAZ', 41),
                ('SAN BLAS - CANILLEJAS', 41),
                ('CHAMBERÍ', 26),
                ('SALAMANCA', 25),
                ('RETIRO', 23),
                ('CHAMARTÍN', 21),
                ('MONCLOA-ARAVACA', 18),
                ('BARAJAS', 15)]
    print("people_by_district OK")

def test_people_by_district_typehints(people_by_district):
    assert people_by_district.__annotations__, 'The function does not have type hints'
    assert set(map(str, people_by_district.__annotations__.values())) == {"<class '__main__.EmploymentData'>", 'list[tuple[str, int]]'}
    print("people_by_district type hints OK")

def test_mean_age_by_district(mean_age_by_district):
    lst = LOAD_EMPLOYMENT(TESTDATAFILE)
    d = mean_age_by_district(lst)
    actual = {'OTRO MUNICIPIO': 37.82706766917293,
              'MORATALAZ': 38.19512195121951,
              'PUENTE DE VALLECAS': 40.361702127659576,
              'USERA': 38.50704225352113,
              'CIUDAD LINEAL': 40.06741573033708,
              'CARABANCHEL': 38.38709677419355,
              'HORTALEZA': 41.0,
              'VILLAVERDE': 40.765957446808514,
              'LATINA': 42.10569105691057,
              'ARGANZUELA': 38.73913043478261,
              'VILLA DE VALLECAS': 42.76712328767123,
              'CENTRO': 39.958333333333336,
              'MONCLOA-ARAVACA': 42.77777777777778,
              'RETIRO': 38.26086956521739,
              'VICÁLVARO': 38.2962962962963,
              'FUENCARRAL-EL PARDO': 39.3,
              'CHAMBERÍ': 46.0,
              'CHAMARTÍN': 40.333333333333336,
              'BARAJAS': 42.93333333333333,
              'SAN BLAS - CANILLEJAS': 36.46341463414634,
              'TETUÁN': 37.478873239436616,
              'SALAMANCA': 43.44}
    assert len(d.keys()) == len(actual.keys()), "Keys do not match"
    for dist in actual:
        assert dist in d, f"District {dist} not found in result"
        assert math.isclose(d[dist], actual[dist]), f"Mean age for {dist} expected {actual[dist]}, but got {d[dist]}"
    print("mean_age_by_district OK")

def _test_type_hints(fun, expected):
    assert fun.__annotations__, 'The function does not have type hints'
    assert set(map(str, fun.__annotations__.values())) == expected, \
        f"Type hints do not match expected {expected}, got {set(map(str, fun.__annotations__.values()))}"
    print(f"{fun.__name__} type hints OK")

def test_mean_age_by_district_typehints(fun):
    _test_type_hints(fun,
                     {"<class '__main__.EmploymentData'>", 'dict[str, float]'})


def test_year_month_data(year_month_data):
    ed = LOAD_EMPLOYMENT(TESTDATAFILE)
    ym_data, ini_y = year_month_data(ed)
    assert ym_data.shape == (9,12), f"Expected shape (9,12), got {ym_data.shape}"
    assert ini_y == 2017, f"Expected initial year 2017, got {ini_y}"

    assert ym_data[0][0] == np.int64(9), f"Expected 9 for (2017, Jan), got {ym_data[0][0]}"

    assert ym_data[8][11] == np.int64(0), f"Expected 0 for (2025, Dec), got {ym_data[8][11]}"

    assert ym_data[5][4] == np.int64(19), f'Expected 19 for (2022, May), got {ym_data[5][4]}'
    print("year_month_data OK")


def test_year_month_data_typehints(fun):
    expected = {"<class '__main__.EmploymentData'>", 'tuple[numpy.array, int]'}
    _test_type_hints(fun, expected)

def test_sum_by_month_year(sum_by_month_year):
    ym_data2 = \
      np.array([[ 9, 10,  9, 10,  3, 20, 17, 10,  7,  7, 23, 15],
                [12, 17, 15, 11, 11, 13, 15,  4, 12, 24, 14, 17],
                [17, 11, 21, 13, 19, 13, 16, 12, 10, 16, 15, 17]])
    print(f"data: {ym_data2}")
    by_month, by_year = sum_by_month_year(ym_data2)
    assert all(by_month == \
               np.array([38, 38, 45, 34, 33, 46, 48, 26, 29, 47, 52, 49])), \
        f"by_month incorrect: {by_month}"
    assert all(by_year == np.array([140, 165, 180])), \
        f"by year incorrect: {by_year}"
    print("sum_by_month_year OK")

def test_sum_by_month_year_typehints(fun):
    expected = {'<built-in function array>', 'tuple[numpy.array, numpy.array]'}
    _test_type_hints(fun, expected)

def test_max_requests(fun):
    ym_data2 = \
      np.array([[ 9, 10,  9, 10,  3, 20, 17, 10,  7,  7, 23, 15],
                [12, 17, 15, 11, 11, 13, 15,  4, 12, 24, 14, 17],
                [17, 11, 21, 13, 19, 13, 16, 12, 10, 16, 15, 17]])
    print(f"data: {ym_data2}")
    year, month, val = fun(ym_data2, 2020)
    assert year == 2021, f"Expected year 2021, got {year}"
    assert month == 'oct', f"Expected month 'oct', got {month}"
    assert val == 24, f"Expected value 24, got {val}"
    print("max_requests OK")

def test_max_requests_typehints(fun):
    expected = {'<built-in function array>', 'tuple[int, str, int]',
                "<class 'int'>"}
    _test_type_hints(fun, expected)

def test_by_quarters(by_quarters):
    ym_data2 = \
      np.array([[ 9, 10,  9, 10,  3, 20, 17, 10,  7,  7, 23, 15],
                [12, 17, 15, 11, 11, 13, 15,  4, 12, 24, 14, 17],
                [17, 11, 21, 13, 19, 13, 16, 12, 10, 16, 15, 17]])
    print(f"data: {ym_data2}")
    q_data = by_quarters(ym_data2)
    expected = np.array([[28, 33, 34, 45],
                          [44, 35, 31, 55],
                          [49, 45, 38, 48]])
    assert np.array_equal(q_data, expected), f"Expected {expected}, got {q_data}"
    print("by_quarters OK")

def test_by_quarters_typehints(fun):
    assert len(fun.__annotations__.values()) == 2
    expected = {'<built-in function array>'}
    _test_type_hints(fun, expected)


def test_load_dataframe(load_dataframe):
    data = load_dataframe('inscritos.csv')
    size = (150137, 15)
    res = data.shape
    assert res == size, f'El tamaño del dataframe debe ser {size}, el tuyo es {res}'
    print(f'size = {res}.....OK')
    tcols = [("FECHA_INSCRIPCION", "object"),
             ("GENERO_DESC", "object"),
             ("DISTRITO_COD", "int64"),
             ("DISTRITO_DESC", "object"),
             ("EDAD", "int64"),
             ("NACIONALIDAD_DESC", "object"),
             ("OBJETIVOPROFESIONAL1_COD", "float64"),
             ("OBJETIVOPROFESIONAL1_DESC", "object"),
             ("OBJETIVOPROFESIONAL2_COD", "float64"),
             ("OBJETIVOPROFESIONAL2_DESC", "object"),
             ("OBJETIVOPROFESIONAL3_COD", "float64"),
             ("OBJETIVOPROFESIONAL3_DESC", "object"),
             ("FX_CARGA", "datetime64[ns]"),
             ("MES_INSCRIPCION", "object"),
             ("ANYO_INSCRIPCION", "int64")]
    for c, t in tcols:
        assert str(data[c].dtype) == t, f'El tipo de la columna {c} no es {t}'
        print(f'El tipo de la columna {c} es {t}....OK')

    assert data['ANYO_INSCRIPCION'].to_list() == data['FECHA_INSCRIPCION'].str.split("-").str[1].astype(int).to_list(), "La columnda ANYO_INSCRIPCION no es correcta"
    assert data['MES_INSCRIPCION'].to_list() == data['FECHA_INSCRIPCION'].str.split("-").str[0].to_list(), "La columnda MES_INSCRIPCION no es correcta"
    dist = data["DISTRITO_DESC"].to_list()
    dist2 = map(lambda x: x.strip(), dist)
    assert all(map(lambda x: x[0] == x[1], zip(dist, dist2))), 'No has quitado el espacio extra en la descripción del distrito'
    print('OK')


def test_reduce_cols(reduce_cols, load_dataframe):
    data = reduce_cols(load_dataframe('inscritos.csv'))
    size = (150137, 9)
    res = data.shape
    assert res == size, f'El tamaño del dataframe debe ser {size}, el tuyo es {res}'
    print(f'size = {res}.....OK')

    tcols = [("FECHA_INSCRIPCION", "object"),
             ("GENERO_DESC", "object"),
             ("DISTRITO_COD", "int64"),
             ("DISTRITO_DESC", "object"),
             ("EDAD", "int64"),
             ("NACIONALIDAD_DESC", "object"),
             ("FX_CARGA", "datetime64[ns]"),
             ("MES_INSCRIPCION", "object"),
             ("ANYO_INSCRIPCION", "int64")]
    res = set(data.columns.to_list())
    act = set({col for col, _ in tcols})
    assert res == act, f'No has quitado las columnas de forma adecuada, esperaba {act} y he obtenido {res}'
    print('Columnas...... OK')
    for c, t in tcols:
        assert str(data[c].dtype) == t, f'El tipo de la columna {c} no es {t}'
        print(f'El tipo de la columna {c} es {t}....OK')

def test_filter_year(filter_year, load_dataframe):
    data = filter_year(load_dataframe('inscritos_test_sample.csv'), 2022)
    assert all(map(lambda x: x==22, data['ANYO_INSCRIPCION'].to_list())), 'Los datos no están correctamente filtrados'
    print('OK')
