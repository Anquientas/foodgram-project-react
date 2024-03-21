
with open('ingredients2.json', 'w', encoding='utf-8') as file:
    file.write('[\n')
    with open('ingredients.csv', 'r', encoding='utf-8') as initial_file:
        lines = initial_file.readlines()
        index = 1
        last_line = lines[-1]
        for line in lines:#[58:70]:
            fields = line.split(',')
            if fields[0][0] == '"':
                fields[0] = fields[0][1:-1]
            fields[0] = fields[0].replace('""', '\\"')

            # if fields[0][0] == '"':
            #     fields[0] = fields[0][1:-1]
            # fields[0] = fields[0].replace('""', '\\"')
            # if fields[0][-2:] == '""':
            #     fields[0] = fields[0][:-2] + '\"'

            # for field in fields:
            #     file.write(field + '\t')

            file.write(
                '\t{\n'
                '\t\t"model": "recipes.ingredient",\n'
                f'\t\t"pk": {index},\n'
                '\t\t"fields": {\n'
                f'\t\t\t"name": "{fields[0]}",\n'
                f'\t\t\t"measurement_unit": "{fields[1][:-1]}"\n'
                '\t\t}\n'
            )
            if line != last_line:
                file.write('\t},\n')
                index += 1
            else:
                file.write('\t}\n')
    file.write(']')
