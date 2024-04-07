import pickle


def predict(input_sentence, model_py_file, model_pkl_dir=None):
    memm = model_py_file.MEMM()

    # Some path issues caused by Django.
    if model_pkl_dir is None:
        memm.load_model()
    else:
        with open(model_pkl_dir, 'rb') as f:
            memm.classifier = pickle.load(f)

    predicted_labels = memm.predict_entities(input_sentence)
    names = ""

    # Output Prediction
    print(input_sentence)
    print("Names are: ", end=" ")
    for word, label in zip(input_sentence.split(), predicted_labels):
        if label == 'PERSON':
            print(word, end=", ")
            names += "*" + word + "* "
        else:
            names += word + " "

    print("\n")
    return names

