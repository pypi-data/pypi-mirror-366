from pathlib import Path

from psi_toml.parser import TomlParser


toml = TomlParser()


def main():
    # test_valid_table()
    # test_two_tables()
    test_dump()


def test_valid_table():
    nl = '\n'
    data = (f'[test_table]{nl}'
            f'"a" = 1{nl}'
            f'b = 2{nl}'
            f'c = 3{nl}'
            f'd = 4{nl}')

    result = toml.parse(data.split('\n'))
    assert result['test_table']['a'] == 1


def test_two_tables():
    nl = '\n'
    data = (f'[first_table]{nl}'
            f'"a" = 1{nl}'
            f'b = 2{nl}'
            f'c = 3{nl}'
            f'd = 4{nl}'
            f'[second_table]{nl}'
            f'"a" = true{nl}')

    result = toml.parse(data.split('\n'))
    assert result['first_table']['a'] == 1
    assert len(result['first_table']) == 4
    assert result['second_table']['a'] is True


def test_dump():
    nl = '\n'
    data = (f'name = "my_name"{nl}'
            f'age = 2{nl}'
            f'colours = {{1: "red", 2: "green"}}{nl}'
            f'alive = true{nl}'
            f'dead = false{nl}'
            f'true = "true"{nl}'
            f'{nl}'
            f'[first_table]{nl}'
            f'"a" = 1{nl}'
            f'b = 2{nl}'
            f'c = 3{nl}'
            f'd = 4{nl}'
            f'[second_table]{nl}'
            f'"a" = true{nl}'
            )
    result = toml.parse(data.split('\n'))

    path = Path(
        Path(__file__).parent.parent.parent,
        'tests',
        'test_data',
        'test_write.toml')
    with open(path, 'w', encoding='utf-8') as f_toml:
        toml.dump(result, f_toml)

    with open(path, 'r', encoding='utf-8') as f_toml:
        result = toml.load(f_toml)
    assert result['name'] == 'my_name'
    assert result['age'] == 2
    assert result['alive'] is True
    assert result['dead'] is False
    assert result['true'] == 'true'
    assert result['colours']['1' ] == 'red'

    with open(path, 'r', encoding='utf-8') as f_toml:
        result = f_toml.read()

    assert '[colours]' in result
    assert 'a = 1' in result
    assert 'a = true' in result



if __name__ == '__main__':
    main()
