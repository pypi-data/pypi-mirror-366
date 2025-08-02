from inspect import signature

import typerhook.utils as utils


class TestCombineSignatures:
    """Test the combine_signatures function."""

    def test_combined_empty_signatures(self):
        """Test merging two empty signatures."""
        def empty1(): pass
        def empty2(): pass
        
        result = utils._combine_signatures(signature(empty1), signature(empty2))
        assert len(result.parameters) == 0

    def test_combined_no_overlap(self):
        """Test merging signatures with no parameter overlap."""
        def func1(a: int, b: str): pass
        def func2(c: float, d: bool): pass
        
        result = utils._combine_signatures(signature(func1), signature(func2))
        
        param_names = list(result.parameters.keys())
        assert param_names == ['a', 'b', 'c', 'd']
        assert result.parameters['a'].annotation == int
        assert result.parameters['c'].annotation == float

    def test_combined_with_overlap_first_wins(self):
        """Test that first signature parameters win in case of name collision."""
        def func1(a: int, b: str): pass
        def func2(a: float, c: bool): pass
        
        result = utils._combine_signatures(signature(func1), signature(func2))
        
        param_names = list(result.parameters.keys())
        assert param_names == ['a', 'b', 'c']
        assert result.parameters['a'].annotation == int  # First wins

    def test_combined_with_ellipsis_default(self):
        """Test that ellipsis defaults are replaced from second signature."""
        def func1(a: int, b=...): pass
        def func2(b: str = "default"): pass
        
        result = utils._combine_signatures(signature(func1), signature(func2))
        
        assert result.parameters['b'].default == "default"

    def test_combined_with_empty_annotation(self):
        """Test that empty annotations are replaced from second signature."""
        def func1(a, b: str): pass
        def func2(a: int): pass
        
        result = utils._combine_signatures(signature(func1), signature(func2))
        
        assert result.parameters['a'].annotation == int
        assert result.parameters['b'].annotation == str

    def test_combined_with_drop_parameter(self):
        """Test that dropped parameters are excluded."""
        def func1(a: int, b: str): pass
        def func2(c: float, d: bool): pass
        
        result = utils._combine_signatures(signature(func1), signature(func2), drop=['d'])
        
        param_names = list(result.parameters.keys())
        assert param_names == ['a', 'b', 'c']
        assert 'd' not in result.parameters

    def test_combined_with_defaults(self):
        """Test merging with default values."""
        def func1(a: int, b: str = "hello"): pass
        def func2(c: float = 3.14): pass
        
        result = utils._combine_signatures(signature(func1), signature(func2))
        
        assert result.parameters['b'].default == "hello"
        assert result.parameters['c'].default == 3.14
