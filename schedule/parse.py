
def getMatrixFromCSV(csvFile):

    rowCount = 0;

    matrix = []

    with open('timetable.csv', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            colCount = 0;

            if rowCount >= len(matrix):
                #print('Adding row to matrix')
                matrix.append([])

            for col in row:
                matrix[rowCount].append(col)
                #print('[' + str(rowCount) + '][' + str(colCount) + '] ' + col)
                colCount += 1
            rowCount += 1

    return matrix

if __name__ == '__main__':
    main()
    
