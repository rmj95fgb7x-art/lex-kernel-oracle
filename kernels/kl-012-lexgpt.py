```python
import os

def generate_text(prompt: str) -> str:
    # Placeholder function for text generation using an external model
    return f"Generated response to '{prompt}'"

if __name__ == "__main__":
    user_input = input("Enter a prompt: ")
    response = generate_text(user_input)
    print(response)
```