from MEM import MEMM
import pickle

# 1. Read meta text txt in line
with open('./data/Meta-Test.txt', 'r') as f:
    str_list = []
    for line in f:
        line = line.replace('\n', '')
        str_list.append(line)


# 2. Initialize Model
memm = MEMM()

with open('../../name_entity_server/static/model.pkl', 'rb') as f:
    memm.classifier = pickle.load(f)

# 3. Classification
predicted_labels, token_list = memm.predict_entities(str_list)

with open('./data/group.28.out.txt ', 'w') as output_file:
    for token, label in zip(token_list, predicted_labels):
        output_file.write(token + '\t' + label + '\n')
        print(token + '\t' + label)
