def add_arrays(arr1, arr2):
    return [x + y for x, y in zip(arr1, arr2)]

def tokenize_text(text):
    return text.lower().replace('.', '').split()
