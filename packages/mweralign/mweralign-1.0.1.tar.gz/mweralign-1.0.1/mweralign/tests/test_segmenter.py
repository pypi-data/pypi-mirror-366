import pytest
from mweralign.segmenter import CJSegmenter, SPSegmenter, is_latin1


class TestIsLatin1:
    """Test the is_latin1 helper function."""
    
    def test_ascii_characters(self):
        assert is_latin1('a')
        assert is_latin1('Z')
        assert is_latin1('1')
        assert is_latin1(' ')
        assert is_latin1('!')
    
    def test_extended_latin1(self):
        assert is_latin1('é')  # U+00E9
        assert is_latin1('ñ')  # U+00F1
        assert is_latin1('ü')  # U+00FC
    
    def test_non_latin1(self):
        assert not is_latin1('中')  # Chinese character
        assert not is_latin1('日')  # Japanese character
        assert not is_latin1('한')  # Korean character
        assert not is_latin1('€')  # Euro symbol (U+20AC)


class TestCJSegmenter:
    """Test the CJSegmenter class."""
    
    def setup_method(self):
        self.segmenter = CJSegmenter()
    
    def test_encode_latin1_words(self):
        text = "hello world"
        expected = ["hello", " ", "world"]
        assert self.segmenter.encode(text) == expected
    
    def test_encode_chinese_characters(self):
        text = "中国"
        expected = ["中", "国"]
        assert self.segmenter.encode(text) == expected
    
    def test_encode_mixed_latin1_chinese(self):
        text = "hello中国world"
        expected = ["hello", "中", "国", "world"]
        assert self.segmenter.encode(text) == expected
    
    def test_encode_mixed_with_spaces(self):
        text = "hello 中国 world"
        expected = ["hello", " ", "中", "国", " ", "world"]
        assert self.segmenter.encode(text) == expected
    
    def test_encode_empty_string(self):
        assert self.segmenter.encode("") == []
    
    def test_encode_only_spaces(self):
        text = "   "
        expected = ["   "]
        assert self.segmenter.encode(text) == expected
    
    def test_encode_punctuation(self):
        text = "hello, world!"
        expected = ["hello,", " ", "world!"]
        assert self.segmenter.encode(text) == expected
    
    def test_decode_latin1_tokens(self):
        tokens = ["hello", "world"]
        expected = "hello world"
        assert self.segmenter.decode(tokens) == expected
    
    def test_decode_chinese_tokens(self):
        tokens = ["中", "国"]
        expected = "中国"
        assert self.segmenter.decode(tokens) == expected
    
    def test_decode_mixed_tokens(self):
        tokens = ["hello", "中", "国", "world"]
        expected = "hello中国world"
        assert self.segmenter.decode(tokens) == expected
    
    def test_decode_with_spaces(self):
        tokens = ["hello", " ", "world"]
        expected = "hello  world"  # Space gets added between latin1 tokens
        assert self.segmenter.decode(tokens) == expected
    
    def test_decode_empty_list(self):
        assert self.segmenter.decode([]) == ""
    
    def test_decode_single_token(self):
        assert self.segmenter.decode(["hello"]) == "hello"
    
    def test_roundtrip_latin1(self):
        text = "hello world test"
        tokens = self.segmenter.encode(text)
        decoded = self.segmenter.decode(tokens)
        # Note: may not be exact due to spacing rules
        assert "hello" in decoded and "world" in decoded and "test" in decoded
    
    def test_roundtrip_chinese(self):
        text = "中国日本"
        tokens = self.segmenter.encode(text)
        decoded = self.segmenter.decode(tokens)
        assert decoded == text


@pytest.mark.skipif(True, reason="Requires SentencePiece model file")
class TestSPSegmenter:
    """Test the SPSegmenter class. Skipped by default as it requires a model file."""
    
    def setup_method(self):
        # This would need a real SentencePiece model file
        self.model_path = "path/to/test.model"
        self.segmenter = SPSegmenter(self.model_path)
    
    def test_encode_returns_list(self):
        text = "hello world"
        result = self.segmenter.encode(text)
        assert isinstance(result, list)
        assert all(isinstance(token, str) for token in result)
    
    def test_decode_returns_string(self):
        tokens = ["hello", "world"]
        result = self.segmenter.decode(tokens)
        assert isinstance(result, str)
    
    def test_roundtrip(self):
        text = "hello world"
        tokens = self.segmenter.encode(text)
        decoded = self.segmenter.decode(tokens)
        # Exact match may not be guaranteed due to tokenization
        assert isinstance(decoded, str)


class TestSPSegmenterMocked:
    """Test SPSegmenter with mocked SentencePiece."""
    
    def test_encode_with_mock(self, monkeypatch):
        """Test encode method with mocked SentencePiece."""
        
        class MockSentencePiece:
            def __init__(self, model_file):
                pass
            
            def encode(self, text, out_type=None):
                if text == "hello world":
                    return ["▁hello", "▁world"]
                return ["▁" + text]
        
        # Mock the sentencepiece import
        import sys
        mock_spm = type(sys)('mock_sentencepiece')
        mock_spm.SentencePieceProcessor = MockSentencePiece
        monkeypatch.setitem(sys.modules, 'sentencepiece', mock_spm)
        
        segmenter = SPSegmenter("fake_model.model")
        result = segmenter.encode("hello world")
        assert result == ["▁hello", "▁world"]
    
    def test_decode_with_mock(self, monkeypatch):
        """Test decode method with mocked SentencePiece."""
        
        class MockSentencePiece:
            def __init__(self, model_file):
                pass
            
            def encode(self, text, out_type=None):
                return []
            
            def decode(self, tokens):
                return " ".join(token.replace("▁", "") for token in tokens)
        
        # Mock the sentencepiece import
        import sys
        mock_spm = type(sys)('mock_sentencepiece')
        mock_spm.SentencePieceProcessor = MockSentencePiece
        monkeypatch.setitem(sys.modules, 'sentencepiece', mock_spm)
        
        segmenter = SPSegmenter("fake_model.model")
        result = segmenter.decode(["▁hello", "▁world"])
        assert result == "hello world"import pytest
from mweralign.segmenter import CJSegmenter, SPSegmenter, is_latin1


class TestIsLatin1:
    """Test the is_latin1 helper function."""
    
    def test_ascii_characters(self):
        assert is_latin1('a')
        assert is_latin1('Z')
        assert is_latin1('1')
        assert is_latin1(' ')
        assert is_latin1('!')
    
    def test_extended_latin1(self):
        assert is_latin1('é')  # U+00E9
        assert is_latin1('ñ')  # U+00F1
        assert is_latin1('ü')  # U+00FC
    
    def test_non_latin1(self):
        assert not is_latin1('中')  # Chinese character
        assert not is_latin1('日')  # Japanese character
        assert not is_latin1('한')  # Korean character
        assert not is_latin1('€')  # Euro symbol (U+20AC)


class TestCJSegmenter:
    """Test the CJSegmenter class."""
    
    def setup_method(self):
        self.segmenter = CJSegmenter()
    
    def test_encode_latin1_words(self):
        text = "hello world"
        expected = ["hello", " ", "world"]
        assert self.segmenter.encode(text) == expected
    
    def test_encode_chinese_characters(self):
        text = "中国"
        expected = ["中", "国"]
        assert self.segmenter.encode(text) == expected
    
    def test_encode_mixed_latin1_chinese(self):
        text = "hello中国world"
        expected = ["hello", "中", "国", "world"]
        assert self.segmenter.encode(text) == expected
    
    def test_encode_mixed_with_spaces(self):
        text = "hello 中国 world"
        expected = ["hello", " ", "中", "国", " ", "world"]
        assert self.segmenter.encode(text) == expected
    
    def test_encode_empty_string(self):
        assert self.segmenter.encode("") == []
    
    def test_encode_only_spaces(self):
        text = "   "
        expected = ["   "]
        assert self.segmenter.encode(text) == expected
    
    def test_encode_punctuation(self):
        text = "hello, world!"
        expected = ["hello,", " ", "world!"]
        assert self.segmenter.encode(text) == expected
    
    def test_decode_latin1_tokens(self):
        tokens = ["hello", "world"]
        expected = "hello world"
        assert self.segmenter.decode(tokens) == expected
    
    def test_decode_chinese_tokens(self):
        tokens = ["中", "国"]
        expected = "中国"
        assert self.segmenter.decode(tokens) == expected
    
    def test_decode_mixed_tokens(self):
        tokens = ["hello", "中", "国", "world"]
        expected = "hello中国world"
        assert self.segmenter.decode(tokens) == expected
    
    def test_decode_with_spaces(self):
        tokens = ["hello", " ", "world"]
        expected = "hello  world"  # Space gets added between latin1 tokens
        assert self.segmenter.decode(tokens) == expected
    
    def test_decode_empty_list(self):
        assert self.segmenter.decode([]) == ""
    
    def test_decode_single_token(self):
        assert self.segmenter.decode(["hello"]) == "hello"
    
    def test_roundtrip_latin1(self):
        text = "hello world test"
        tokens = self.segmenter.encode(text)
        decoded = self.segmenter.decode(tokens)
        # Note: may not be exact due to spacing rules
        assert "hello" in decoded and "world" in decoded and "test" in decoded
    
    def test_roundtrip_chinese(self):
        text = "中国日本"
        tokens = self.segmenter.encode(text)
        decoded = self.segmenter.decode(tokens)
        assert decoded == text


@pytest.mark.skipif(True, reason="Requires SentencePiece model file")
class TestSPSegmenter:
    """Test the SPSegmenter class. Skipped by default as it requires a model file."""
    
    def setup_method(self):
        # This would need a real SentencePiece model file
        self.model_path = "path/to/test.model"
        self.segmenter = SPSegmenter(self.model_path)
    
    def test_encode_returns_list(self):
        text = "hello world"
        result = self.segmenter.encode(text)
        assert isinstance(result, list)
        assert all(isinstance(token, str) for token in result)
    
    def test_decode_returns_string(self):
        tokens = ["hello", "world"]
        result = self.segmenter.decode(tokens)
        assert isinstance(result, str)
    
    def test_roundtrip(self):
        text = "hello world"
        tokens = self.segmenter.encode(text)
        decoded = self.segmenter.decode(tokens)
        # Exact match may not be guaranteed due to tokenization
        assert isinstance(decoded, str)


class TestSPSegmenterMocked:
    """Test SPSegmenter with mocked SentencePiece."""
    
    def test_encode_with_mock(self, monkeypatch):
        """Test encode method with mocked SentencePiece."""
        
        class MockSentencePiece:
            def __init__(self, model_file):
                pass
            
            def encode(self, text, out_type=None):
                if text == "hello world":
                    return ["▁hello", "▁world"]
                return ["▁" + text]
        
        # Mock the sentencepiece import
        import sys
        mock_spm = type(sys)('mock_sentencepiece')
        mock_spm.SentencePieceProcessor = MockSentencePiece
        monkeypatch.setitem(sys.modules, 'sentencepiece', mock_spm)
        
        segmenter = SPSegmenter("fake_model.model")
        result = segmenter.encode("hello world")
        assert result == ["▁hello", "▁world"]
    
    def test_decode_with_mock(self, monkeypatch):
        """Test decode method with mocked SentencePiece."""
        
        class MockSentencePiece:
            def __init__(self, model_file):
                pass
            
            def encode(self, text, out_type=None):
                return []
            
            def decode(self, tokens):
                return " ".join(token.replace("▁", "") for token in tokens)
        
        # Mock the sentencepiece import
        import sys
        mock_spm = type(sys)('mock_sentencepiece')
        mock_spm.SentencePieceProcessor = MockSentencePiece
        monkeypatch.setitem(sys.modules, 'sentencepiece', mock_spm)
        
        segmenter = SPSegmenter("fake_model.model")
        result = segmenter.decode(["▁hello", "▁world"])
        assert result == "hello world"