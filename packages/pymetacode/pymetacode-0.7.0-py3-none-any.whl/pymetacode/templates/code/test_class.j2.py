

class Test{{ class.name }}(unittest.TestCase):
    def setUp(self):
        self.{{ class.instance }} = {{ module.name }}.{{ class.name }}()

    def test_instantiate_class(self):
        pass
