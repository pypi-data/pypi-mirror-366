import unittest

from cyjax.resources.model_dto import ModelDto


class ModelDtoTest(unittest.TestCase):

    def test_model_dto_constructor_from_dict(self):
        obj = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 70,
            'phones': [
                '100-200-300',
                '400-500-600'
            ],
            'address': {
                'city': 'London',
                'street': 'Oxford Street',
                'postcode': 'OX1 1AA'
            }
        }

        dto = ModelDto(**obj)

        self.assertIsInstance(dto, dict)
        self.assertEqual('John', dto.get('first_name'))
        self.assertEqual('John', dto['first_name'])
        self.assertFalse(hasattr(dto, 'first_name'))
        self.assertEqual(70, dto['age'])
        self.assertEqual(['100-200-300', '400-500-600'], dto['phones'])
        self.assertEqual({
                'city': 'London',
                'street': 'Oxford Street',
                'postcode': 'OX1 1AA'
            }, dto.get('address'))
        self.assertEqual('London', dto.get('address').get('city'))
        self.assertEqual('Oxford Street', dto['address']['street'])
        self.assertEqual(obj, dict(dto))

    def test_model_dto_with_properties(self):
        class UserDto(ModelDto):

            @property
            def first_name(self):
                return self.get('first_name')

            @property
            def last_name(self):
                return self.get('last_name')

            @property
            def age(self):
                return self.get('age')

        obj = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 70,
            'phones': [
                '100-200-300',
                '400-500-600'
            ],
            'address': {
                'city': 'London',
                'street': 'Oxford Street',
                'postcode': 'OX1 1AA'
            }
        }

        dto = UserDto(**obj)

        self.assertTrue(hasattr(dto, 'first_name'))
        self.assertTrue(hasattr(dto, 'last_name'))
        self.assertTrue(hasattr(dto, 'age'))
        self.assertFalse(hasattr(dto, 'phones'))
        self.assertFalse(hasattr(dto, 'address'))
        self.assertEqual('John', dto.get('first_name'))
        self.assertEqual('John', dto['first_name'])
        self.assertEqual('John', dto.first_name)
        self.assertEqual('Doe', dto.last_name)
        self.assertEqual(70, dto.age)
