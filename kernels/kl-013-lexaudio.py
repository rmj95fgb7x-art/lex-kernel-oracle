```python
import os

def analyze_audio(file_path: str) -> dict:
    # Placeholder function for audio analysis using an external service
    return {
        "file_path": file_path,
        "duration": 120,  # in seconds
        "loudness": -23.5,  # in dBFS
        "pitch": 440,  # in Hz
    }

if __name__ == "__main__":
    audio_file = input("Enter path to audio file: ")
    analysis_results = analyze_audio(audio_file)
    print(analysis_results)
```