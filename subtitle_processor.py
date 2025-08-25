import re

def extract_plain_text_from_srt(srt_content):
    """
    Extracts plain text from SRT subtitle content, removing timestamps and metadata.
    """
    # Remove subtitle numbers, timestamps, and empty lines between subtitles
    # This regex matches lines that are purely numbers (subtitle index) or timestamps (HH:MM:SS,ms --> HH:MM:SS,ms)
    cleaned_content = re.sub(r'^\d+\n(?:\d{2}:){2}\d{2},\d{3} --> (?:\d{2}:){2}\d{2},\d{3}\n', '', srt_content, flags=re.MULTILINE)
    
    # Remove any remaining timestamps (e.g., if not at the start of a block)
    cleaned_content = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', cleaned_content)
    
    # Remove HTML tags that might be present in some subtitles
    cleaned_content = re.sub(r'<[^>]+>', '', cleaned_content)
    
    # Replace multiple newlines with a single space to merge lines into paragraphs
    cleaned_content = re.sub(r'\n\n+', ' ', cleaned_content)
    cleaned_content = re.sub(r'\n', ' ', cleaned_content)
    
    # Remove any leading/trailing whitespace
    cleaned_content = cleaned_content.strip()
    
    return cleaned_content

def clean_text(text):
    """
    Performs general text cleaning, such as removing extra spaces and special characters.
    """
    # Remove non-alphanumeric characters except for common punctuation and spaces
    # This might be too aggressive depending on desired output, adjust regex as needed
    # For now, let's focus on common cleaning: multiple spaces, leading/trailing spaces
    cleaned_text = re.sub(r'\s+', ' ', text) # Replace multiple spaces with a single space
    cleaned_text = cleaned_text.strip() # Remove leading/trailing whitespace
    return cleaned_text

# Example usage (for testing purposes, not part of the module's core function)
if __name__ == '__main__':
    sample_srt = """
1
00:00:01,000 --> 00:00:03,500
Hello, this is a test.

2
00:00:04,000 --> 00:00:06,000
<i>This is the second line.</i>

3
00:00:07,000 --> 00:00:09,000
And a third line with some <font color="#FF0000">HTML</font>.
"""
    
    plain_text = extract_plain_text_from_srt(sample_srt)
    print("Extracted Plain Text:")
    print(plain_text)
    
    cleaned_final_text = clean_text(plain_text)
    print("\nCleaned Final Text:")
    print(cleaned_final_text)
