import pickle


def predict(input_sentence, model_py_file, model_pkl_dir=None):
    memm = model_py_file.MEMM()

    # Some path issues caused by Django.
    if model_pkl_dir is None:
        memm.load_model()
    else:
        with open(model_pkl_dir, 'rb') as f:
            memm.classifier = pickle.load(f)

    predicted_labels, token_list = memm.predict_entities(input_sentence)
    names = ""
    debug_predicted_label = ""

    # Output Prediction
    print(input_sentence)
    print("Names are: ", end=" ")


    for word, label in zip(token_list, predicted_labels):
        if label == 'PERSON':
            print(word, end=", ")
            names += '<span style="background-color: #bce7ac">' + "<b>" + word + "</b>" + "</span>" + " · "
        else:
            names += word + " · "
        debug_predicted_label += label + " "

    print("\n")
    return names, debug_predicted_label

