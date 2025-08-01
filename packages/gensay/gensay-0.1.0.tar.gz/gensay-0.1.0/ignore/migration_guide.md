# Text Chunking Migration Guide

This guide shows how to migrate from the old text chunking implementation to the new, more maintainable system.

## Old Implementation Issues

The original `split_text_into_chunks` function in the chatterbox-tts project had several limitations:

1. **Complex nested logic** - Multiple levels of if-else statements
2. **Limited configurability** - Hard-coded parameters
3. **Basic regex patterns** - Only handles simple punctuation
4. **No text structure preservation** - Doesn't handle paragraphs
5. **Inefficient string operations** - String concatenation in loops

## New Implementation Benefits

The new `TextChunker` class provides:

1. **Clear separation of concerns** - Different strategies for different use cases
2. **Highly configurable** - All parameters can be customized
3. **Multiple chunking strategies** - Sentence, paragraph, word, and character-based
4. **Better text preservation** - Maintains formatting and structure
5. **Performance optimized** - Compiled regex patterns and efficient operations
6. **Extensive testing** - Comprehensive test suite included
7. **Type hints** - Full type annotations for better IDE support

## Migration Steps

### 1. Basic Drop-in Replacement

To replace the old function with minimal changes:

```python
# Old code
from app import split_text_into_chunks

chunks = split_text_into_chunks(text, max_chars=250)

# New code
from gensay.text_chunker import chunk_text

chunks = chunk_text(text, max_size=250)
```

### 2. TTS-Specific Migration

For TTS applications, use the optimized function:

```python
# Old code
text_chunks = split_text_into_chunks(text_input, chunk_size)
silence_samples = int(0.1 * model.sr)  # Hard-coded silence

# New code
from gensay.text_chunker import smart_chunk_for_tts

chunks, config = smart_chunk_for_tts(
    text_input, 
    max_size=chunk_size,
    silence_duration=0.3  # Configurable silence
)
# Access silence duration from config
silence_samples = int(config.silence_duration * model.sr)
```

### 3. Advanced Migration with Custom Configuration

For more control over chunking behavior:

```python
# Create custom configuration
from gensay.text_chunker import TextChunker, ChunkingConfig, ChunkingStrategy

config = ChunkingConfig(
    max_chunk_size=250,
    min_chunk_size=50,
    preserve_sentences=True,
    preserve_words=True,
    sentence_terminators=r"[.!?]",
    sub_sentence_separators=r"[,;:]",
    silence_duration=0.3,
    strategy=ChunkingStrategy.SENTENCE
)

chunker = TextChunker(config)
chunks = chunker.chunk_text(text)
```

### 4. Full Function Replacement

Here's how to replace the old function entirely:

```python
# Old function (simplified for comparison)
def split_text_into_chunks(text: str, max_chars: int = 250) -> List[str]:
    if len(text) <= max_chars:
        return [text]
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Complex nested logic...
        # ... (100+ lines of code)
    
    return chunks

# New replacement
from gensay.text_chunker import smart_chunk_for_tts

def split_text_into_chunks(text: str, max_chars: int = 250) -> List[str]:
    """Drop-in replacement using new chunker."""
    chunks, _ = smart_chunk_for_tts(text, max_size=max_chars)
    return chunks
```

## Integration Example

Here's a complete example of integrating the new chunker into the TTS generation function:

```python
from gensay.text_chunker import TextChunker, ChunkingConfig, ChunkingStrategy
import torch
import torchaudio

def generate_tts_audio(
    text_input: str,
    audio_prompt_path_input: str,
    chunk_size: int = 250,
    silence_duration: float = 0.3
):
    # Configure chunker for TTS
    config = ChunkingConfig(
        max_chunk_size=chunk_size,
        silence_duration=silence_duration,
        strategy=ChunkingStrategy.SENTENCE,
        preserve_sentences=True,
        strip_whitespace=True
    )
    
    chunker = TextChunker(config)
    chunks = chunker.chunk_text(text_input)
    
    # Get chunk information for logging
    chunk_info = chunker.get_chunk_info(text_input)
    logger.info(f"Processing {len(chunks)} chunks")
    
    generated_wavs = []
    
    for i, (start, end, chunk) in enumerate(chunk_info):
        logger.info(f"Chunk {i+1}/{len(chunks)} [{start}:{end}]: '{chunk[:50]}...'")
        
        # Generate audio for chunk
        wav = model.generate(
            chunk,
            audio_prompt_path=audio_prompt_path_input,
            # ... other parameters
        )
        generated_wavs.append(wav)
    
    # Concatenate with configurable silence
    if len(generated_wavs) > 1:
        silence_samples = int(config.silence_duration * model.sr)
        silence = torch.zeros(1, silence_samples, dtype=generated_wavs[0].dtype)
        
        final_wav = generated_wavs[0]
        for wav_chunk in generated_wavs[1:]:
            final_wav = torch.cat([final_wav, silence, wav_chunk], dim=1)
    else:
        final_wav = generated_wavs[0]
    
    return final_wav
```

## Testing the Migration

After migration, test with various text inputs:

```python
# Test cases
test_texts = [
    # Short text
    "Hello world.",
    
    # Multiple sentences
    "First sentence. Second sentence. Third sentence.",
    
    # Long sentence
    "This is a very long sentence that will definitely exceed the maximum " +
    "chunk size and needs to be split intelligently at appropriate boundaries.",
    
    # Paragraphs
    """First paragraph here.
    
    Second paragraph here.
    
    Third paragraph here.""",
    
    # Complex punctuation
    "Question? Exclamation! Statement. Clause, with comma; and semicolon: done.",
]

for text in test_texts:
    old_chunks = split_text_into_chunks(text, 50)  # Old function
    new_chunks = chunk_text(text, max_size=50)     # New function
    
    print(f"Text: {text[:30]}...")
    print(f"Old chunks: {len(old_chunks)}")
    print(f"New chunks: {len(new_chunks)}")
    print()
```

## Performance Considerations

The new implementation offers better performance through:

1. **Compiled regex patterns** - Patterns are compiled once during initialization
2. **Efficient string operations** - Uses join() instead of repeated concatenation
3. **Early termination** - Returns immediately for empty or short text
4. **Memory efficiency** - Processes text in a single pass where possible

## Customization Options

The new system allows extensive customization:

```python
# Custom sentence terminators for different languages
config = ChunkingConfig(
    sentence_terminators=r"[.!?。！？]",  # Include Chinese punctuation
    sub_sentence_separators=r"[,;:，；：]"
)

# Overlap for context preservation
config = ChunkingConfig(
    max_chunk_size=200,
    overlap_size=20  # 20 character overlap between chunks
)

# Different strategies for different content types
article_config = ChunkingConfig(strategy=ChunkingStrategy.PARAGRAPH)
dialogue_config = ChunkingConfig(strategy=ChunkingStrategy.SENTENCE)
code_config = ChunkingConfig(strategy=ChunkingStrategy.CHARACTER)
```

## Conclusion

The new text chunking system provides a more maintainable, flexible, and performant solution. It's designed to be a drop-in replacement while offering significantly more features and better code organization. The migration can be done gradually, starting with basic replacement and moving to more advanced features as needed.