import unittest
from pyfunc import Pipeline, square, increment, half, pipeline, _

class TestPipeline(unittest.TestCase):

    def test_conditional_and_cloning(self):
        value = 15
        p = Pipeline(value).when(lambda x: x > 10, lambda x: x * 2).unless(lambda x: x >= 30, lambda x: x + 10)
        clone = p.clone().apply(lambda x: x + 1)
        self.assertEqual(p.get(), 30)
        self.assertEqual(clone.get(), 31)

    def test_data_aggregation_pipeline(self):
        data = {
            "alice": [10, 20, 30],
            "bob": [5, 15, 25],
            "carol": [7, 14, 21]
        }
        result = (
            Pipeline(data)
            .with_items()
            .starmap(lambda name, scores: (name, sum(scores)))
            .filter(lambda pair: pair[1] > 45)
            .chain([("dave", 45)])
            .sort(key=lambda pair: pair[1], reverse=False)
            .map(lambda pair: f"{pair[0]}: {pair[1]}")
            .to_list()
        )
        expected = ["dave: 45", "alice: 60"]
        self.assertEqual(result, expected)

    def test_text_processing_pipeline(self):
        text = "  The quick brown fox jumps over the lazy dog.  "
        result = (
            Pipeline(text)
            .apply(str.strip)
            .apply(str.lower)
            .apply(lambda s: s.replace('.', ''))
            .explode(" ")
            .filter(lambda w: len(w) > 3)
            .chain(["extra", "words"])
            .unique()
            .sort()
            .to_list()
        )
        expected = ['brown', 'extra', 'jumps', 'lazy', 'over', 'quick', 'words']
        self.assertEqual(result, expected)

        # Test with implode and surround after to_list
        result_implode_surround = (
            Pipeline(text)
            .apply(str.strip)
            .apply(str.lower)
            .apply(lambda s: s.replace('.', ''))
            .explode(" ")
            .filter(lambda w: len(w) > 3)
            .chain(["extra", "words"])
            .unique()
            .sort()
            .to_list()
        )
        result_implode_surround = Pipeline(result_implode_surround).implode(" ").surround("<p>", "</p>").get()
        self.assertEqual(result_implode_surround, "<p>brown extra jumps lazy over quick words</p>")

    def test_numeric_analysis_pipeline(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        result = (
            Pipeline(data)
            .filter(lambda x: x % 2 == 1)
            .map(lambda x: x ** 2)
            .window(3, 1)
            .map(sum)
            .apply_if(lambda xs: len(xs) > 2, lambda xs: xs[::-1])
            .to_list()
        )
        self.assertEqual(result, [155, 83, 35])

    def test_complex_string_template_pipeline(self):
        template = "Dear {title} {last_name}, your balance is {balance:.2f} USD."
        result = (
            Pipeline(template)
            .template_fill({"title": "Mr.", "last_name": "Smith", "balance": 1234.567})
            .surround("---\n", "\n---")
            .get()
        )
        expected = "---\nDear Mr. Smith, your balance is 1234.57 USD.\n---"
        self.assertEqual(result, expected)

    def test_iterable_operations(self):
        data1 = [1, 2, 3, 4, 5, 6]
        data2 = ['a', 'b', 'c']
        result = (
            Pipeline(data1)
            .pairwise()
            .zip_with(data2)
            .to_list()
        )
        expected = [((1, 2), 'a'), ((3, 4), 'b'), ((5, 6), 'c')]
        self.assertEqual(result, expected)

    def test_pipeline_decorator_and_operator_overloads(self):
        @pipeline
        def process(p):
            return p.apply(square).apply(increment).apply(half)

        result = process(4).get()
        self.assertEqual(result, 8.5)

        result2 = Pipeline(3) | square | increment | half
        self.assertEqual(result2.get(), 5.0)

        result3 = Pipeline(3) >> square >> increment >> half
        self.assertEqual(result3.get(), 5.0)

    def test_callable_pipeline_with_add_and_subtract(self):
        # Test chaining add and subtract within a single pipeline
        result = Pipeline(initial_value=4).add(5).subtract(2).get()
        self.assertEqual(result, 7)

        # Test the pipeline as a callable function
        # This demonstrates that the pipeline can be initialized with a value
        # and then operations are applied.
        p = Pipeline().add(5).subtract(2)
        self.assertEqual(p(4), 7)

    def test_if_else_method(self):
        # Test with a simple condition
        result = Pipeline(10).if_else(_ > 5, _ * 2, _ + 1).get()
        self.assertEqual(result, 20)

        result = Pipeline(3).if_else(_ > 5, _ * 2, _ + 1).get()
        self.assertEqual(result, 4)

        # Test with a callable predicate
        is_even = lambda x: x % 2 == 0
        result = Pipeline(4).if_else(is_even, _ / 2, _ * 3).get()
        self.assertEqual(result, 2.0)

        result = Pipeline(5).if_else(is_even, _ / 2, _ * 3).get()
        self.assertEqual(result, 15)

        # Test with list and placeholder
        data = [1, 2, 3, 4, 5]
        result = Pipeline(data).map(
            lambda x: Pipeline(x).if_else(_ % 2 == 0, _ * 10, _ + 1).get()
        ).to_list()
        self.assertEqual(result, [2, 20, 4, 40, 6])

    def test_placeholder_syntax(self):
        from pyfunc import _

        # Arithmetic operations
        result = Pipeline(5).apply(_ * 10).get()
        self.assertEqual(result, 50)

        result = Pipeline(5).apply(_ + 5).get()
        self.assertEqual(result, 10)

        result = Pipeline(10).apply(_ - 3).get()
        self.assertEqual(result, 7)

        result = Pipeline(20).apply(_ / 4).get()
        self.assertEqual(result, 5.0)

        result = Pipeline(21).apply(_ // 4).get()
        self.assertEqual(result, 5)

        result = Pipeline(21).apply(_ % 4).get()
        self.assertEqual(result, 1)

        result = Pipeline(2).apply(_ ** 3).get()
        self.assertEqual(result, 8)

        # Reverse arithmetic operations
        result = Pipeline(5).apply(10 * _).get()
        self.assertEqual(result, 50)

        result = Pipeline(5).apply(5 + _).get()
        self.assertEqual(result, 10)

        # Comparison operations
        result = Pipeline(5).apply(_ > 2).get()
        self.assertEqual(result, True)

        result = Pipeline(5).apply(_ == 5).get()
        self.assertEqual(result, True)

        result = Pipeline(5).apply(_ <= 4).get()
        self.assertEqual(result, False)

        # Attribute access and method calls
        result = Pipeline("  hello  ").apply(_.strip()).get()
        self.assertEqual(result, "hello")

        result = Pipeline("HELLO").apply(_.lower()).get()
        self.assertEqual(result, "hello")

        # Test .then() method
        result = Pipeline(5).then(_ * 2).then(_ + 1).get()
        self.assertEqual(result, 11)

        

        # Unary operations
        result = Pipeline(5).apply(-_).get()
        self.assertEqual(result, -5)

        result = Pipeline(-5).apply(+_).get()
        self.assertEqual(result, -5)

        

        result = Pipeline(-10).apply(abs(_)).get()
        self.assertEqual(result, 10)

        # Chained placeholder operations
        result = Pipeline([1, 2, 3, 4]).filter(_ > 2).map(_ * 10).to_list()
        self.assertEqual(result, [30, 40])

        result = Pipeline("  Test String  ").apply(_.strip().lower().replace(" ", "-")).get()
        self.assertEqual(result, "test-string")

        # Placeholder with item access on a list of dictionaries
        data_list = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
        result = Pipeline(data_list).map(_['a']).to_list()
        self.assertEqual(result, [1, 3])

    def test_take_and_skip_methods(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        result_take = Pipeline(data).take(5).to_list()
        self.assertEqual(result_take, [1, 2, 3, 4, 5])

        result_skip = Pipeline(data).skip(5).to_list()
        self.assertEqual(result_skip, [6, 7, 8, 9, 10])

        result_take_skip = Pipeline(data).skip(3).take(4).to_list()
        self.assertEqual(result_take_skip, [4, 5, 6, 7])

    def test_take_while_and_skip_while_methods(self):
        data = [1, 2, 3, 4, 5, 6, 1, 2]

        result_take_while = Pipeline(data).take_while(_ < 4).to_list()
        self.assertEqual(result_take_while, [1, 2, 3])

        result_skip_while = Pipeline(data).skip_while(_ < 4).to_list()
        self.assertEqual(result_skip_while, [4, 5, 6, 1, 2])

        result_combined = Pipeline(data).take_while(_ < 6).skip_while(_ < 3).to_list()
        self.assertEqual(result_combined, [3, 4, 5])

    def test_reduce_method(self):
        data = [1, 2, 3, 4, 5]

        # Test with no initializer
        result = Pipeline(data).reduce(_ + _).get()
        self.assertEqual(result, 15)

        # Test with initializer
        result = Pipeline(data).reduce(_ + _, 10).get()
        self.assertEqual(result, 25)

        # Test with a different function
        result = Pipeline(data).reduce(_ * _).get()
        self.assertEqual(result, 120)

    def test_reduce_right_method(self):
        data = [1, 2, 3, 4, 5]

        # Test with no initializer (right-to-left subtraction)
        # 1 - (2 - (3 - (4 - 5))) = 1 - (2 - (3 - (-1))) = 1 - (2 - 4) = 1 - (-2) = 3
        result = Pipeline(data).reduce_right(_ - _).get()
        self.assertEqual(result, 3)

        # Test with initializer (right-to-left concatenation)
        # "1" + "2" + "3" + "4" + "5" + "_init"
        result = Pipeline([1, 2, 3, 4, 5]).reduce_right(lambda x, acc: str(x) + acc, "_init").get()
        self.assertEqual(result, "12345_init")

    def test_extensibility(self):
        class MyCustomType:
            def __init__(self, value):
                self.value = value

            def custom_transform(self, multiplier):
                return MyCustomType(self.value * multiplier)

        # Register a custom type handler
        Pipeline.register_custom_type(MyCustomType, {
            "custom_transform": lambda obj, multiplier: obj.custom_transform(multiplier)
        })

        # Extend the Pipeline with a new method
        def custom_pipeline_method(self, factor):
            return self.apply(lambda x: x.value * factor)

        Pipeline.extend("custom_pipeline_method", custom_pipeline_method)

        # Test custom type handling
        obj = MyCustomType(10)
        result = Pipeline(obj).apply(lambda x: x.custom_transform(2)).get()
        self.assertEqual(result.value, 20)

        # Test extended method
        result2 = Pipeline(obj).custom_pipeline_method(3).get()
        self.assertEqual(result2, 30)

    def test_product_method(self):
        data = [1, 2]
        result = Pipeline(data).product([3, 4]).to_list()
        expected = [(1, 3), (1, 4), (2, 3), (2, 4)]
        self.assertEqual(result, expected)

    def test_combinations_method(self):
        data = [1, 2, 3]
        result = Pipeline(data).combinations(2).to_list()
        expected = [(1, 2), (1, 3), (2, 3)]
        self.assertEqual(result, expected)

    def test_sliding_pairs_method(self):
        data = [1, 2, 3, 4]
        result = Pipeline(data).sliding_pairs().to_list()
        expected = [[1, 2], [2, 3], [3, 4]]
        self.assertEqual(result, expected)

    def test_group_by_method(self):
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}, {"name": "Charlie", "age": 30}]
        result = Pipeline(data).group_by(_["age"]).get()
        expected = {
            30: [{"name": "Alice", "age": 30}, {"name": "Charlie", "age": 30}],
            25: [{"name": "Bob", "age": 25}]
        }
        self.assertEqual(result, expected)

        # Test with a callable key
        data2 = [1, 2, 3, 4, 5, 6]
        result2 = Pipeline(data2).group_by(lambda x: "even" if x % 2 == 0 else "odd").get()
        expected2 = {
            "odd": [1, 3, 5],
            "even": [2, 4, 6]
        }
        self.assertEqual(result2, expected2)

    def test_first_method(self):
        data = [1, 2, 3]
        result = Pipeline(data).first().get()
        self.assertEqual(result, 1)

        empty_data: list[int] = []
        result_empty = Pipeline(empty_data).first().get()
        self.assertIsNone(result_empty)

    def test_last_method(self):
        data = [1, 2, 3]
        result = Pipeline(data).last().get()
        self.assertEqual(result, 3)

        empty_data: list[int] = []
        result_empty = Pipeline(empty_data).last().get()
        self.assertIsNone(result_empty)

        # Test with a generator
        gen_data = (i for i in range(5))
        result_gen = Pipeline(gen_data).last().get()
        self.assertEqual(result_gen, 4)

    def test_nth_method(self):
        data = [10, 20, 30, 40, 50]
        result = Pipeline(data).nth(2).get()
        self.assertEqual(result, 30)

        result_out_of_bounds = Pipeline(data).nth(10).get()
        self.assertIsNone(result_out_of_bounds)

        empty_data: list[int] = []
        result_empty = Pipeline(empty_data).nth(0).get()
        self.assertIsNone(result_empty)

    def test_is_empty_method(self):
        data = [1, 2, 3]
        result = Pipeline(data).is_empty().get()
        self.assertFalse(result)

        empty_data: list[int] = []
        result_empty = Pipeline(empty_data).is_empty().get()
        self.assertTrue(result_empty)

    def test_count_method(self):
        data = [1, 2, 3, 4, 5]
        result = Pipeline(data).count().get()
        self.assertEqual(result, 5)

        empty_data: list[int] = []
        result_empty = Pipeline(empty_data).count().get()
        self.assertEqual(result_empty, 0)

    def test_sum_method(self):
        data = [1, 2, 3, 4, 5]
        result = Pipeline(data).sum().get()
        self.assertEqual(result, 15)

        data_float = [1.0, 2.5, 3.5]
        result_float = Pipeline(data_float).sum().get()
        self.assertEqual(result_float, 7.0)

        empty_data: list[int] = []
        result_empty = Pipeline(empty_data).sum().get()
        self.assertEqual(result_empty, 0)

    def test_min_method(self):
        data = [5, 1, 8, 2, 9]
        result = Pipeline(data).min().get()
        self.assertEqual(result, 1)

        data_float = [5.5, 1.1, 8.8]
        result_float = Pipeline(data_float).min().get()
        self.assertEqual(result_float, 1.1)

        empty_data: list[int] = []
        result_empty = Pipeline(empty_data).min().get()
        self.assertIsNone(result_empty)

    def test_max_method(self):
        data = [5, 1, 8, 2, 9]
        result = Pipeline(data).max().get()
        self.assertEqual(result, 9)

        data_float = [5.5, 1.1, 8.8]
        result_float = Pipeline(data_float).max().get()
        self.assertEqual(result_float, 8.8)

        empty_data: list[int] = []
        result_empty = Pipeline(empty_data).max().get()
        self.assertIsNone(result_empty)

    def test_reverse_method(self):
        data = [1, 2, 3, 4, 5]
        result = Pipeline(data).reverse().to_list()
        self.assertEqual(result, [5, 4, 3, 2, 1])

        empty_data: list[int] = []
        result_empty = Pipeline(empty_data).reverse().to_list()
        self.assertEqual(result_empty, [])


if __name__ == "__main__":
    unittest.main()
