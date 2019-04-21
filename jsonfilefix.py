# add '[' at the start of file 
# add ']' at the end of file 
# add ',' to split each json



with open("gamelist.json", 'r+') as f:
    with open("fixedgamelist.json", 'w+') as output:
        output.write('[')
        lines = f.readlines()
        for i in range (0, len(lines)):
            if (lines[i] == '}{\n'):
                lines[i] = '},{\n'
            lines[i] = lines[i].replace('\n', ' ') 
            output.write(lines[i])
        output.write(']')

