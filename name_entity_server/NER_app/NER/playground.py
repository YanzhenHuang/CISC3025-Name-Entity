some_text = "This text is used to test whether the backend can reach here."


def foo():
    sample_text = ""
    for i in range(10000000):
        sample_text = str(i)
    return sample_text
