```python
import os

def analyze_health_data(patient_id: str) -> dict:
    # Placeholder function to analyze health data using an external service
    return {
        "patient_id": patient_id,
        "temperature": 98.6,  # in Fahrenheit
        "heart_rate": 72,  # in bpm
        "blood_pressure": "120/80",  # in mmHg
        "spo2": 95,  # in %
    }

if __name__ == "__main__":
    patient_id = input("Enter patient ID: ")
    analysis_results = analyze_health_data(patient_id)
    print(analysis_results)
```