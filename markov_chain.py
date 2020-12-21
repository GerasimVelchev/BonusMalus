import numpy as np

# The statespace

states = [ "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12" ]

# Probabilities matrix (transition matrix - indexation is from 0 to 11 - so index 0 is group 1, index 1 is group 2 etc.)

size = 12
transitionMatrix = [[0.0 for _ in range(size)] for _ in range(size)]

for i in range(0, size):
        j = i + 2
        if j > size - 1:
            j = size - 1
        transitionMatrix[i][j] += 0.040

for i in range(0, size):
        j = i + 3
        if j > size - 1:
            j = size - 1
        transitionMatrix[i][j] += 0.030

for i in range(0, size):
        j = i + 4
        if j > size - 1:
            j = size - 1
        transitionMatrix[i][j] += 0.010

for i in range(0, size):
        j = i + 9
        if j > size - 1:
            j = size - 1
        transitionMatrix[i][j] += 0.002

for i in range(0, size):
        sum = 0.0
        for j in range(0, size):
            sum += transitionMatrix[i][j]
        j = i - 1
        if j < 0:
            j = 0
        transitionMatrix[i][j] = 1.0 - sum

# The neighbour states of each state
# The neighbour probabilities of each state

nextStates = [ [] for _ in range(size) ]
nextProbs = [ [] for _ in range(size) ]

for i in range(0, size):
    for j in range(0, size):
        if transitionMatrix[i][j] > 0.0:
            nextStates[i].append(j)
            nextProbs[i].append(transitionMatrix[i][j])

print("Transition matrix:")

for cnt in range(0, size):
    print(cnt)
    print(" : ")
    print(transitionMatrix[cnt])

# Make the equation STATIONARY * (P - E) = ZEROES

a = np.zeros((size, size))
a[:, :] = np.array(np.transpose(transitionMatrix))

for i in range(0, size):
    a[i][i] -= 1.0
lastRow = a[size - 1]

# Insert the equation "sum of stationary probabilities = 1" instead the last one from STATIONARY * (P - E) = ZEROES
# Because without it the system has infinite number of solutions

a[size - 1] = [ 1.0 for _ in range(size) ]

zeroes = [ 0.0 for _ in range(size) ]
zeroes[size - 1] = 1.0
b = np.array(zeroes)

# Stationary distribution solution

stationary = np.linalg.solve(a, b)

# Check if it satisfies the last equation from STATIONARY * (P - E) = ZEROES

sum = 0
last_row = 0
for i in range(size):
    sum += stationary[i]
    last_row += lastRow[i] * stationary[i]

print("Verify the distribution is stationary: ")
print(sum)
print("Verify last row is satisifed: ")
print(last_row)

# Bonus malus array values calculation
# We use E_{pi} bonusMalus(X_n) = sum_{i \member I} { (pi[i] * bonusMalus[i]) } = 1

bonusMalus = [ 0.0 for _ in range(size) ]

# Try the first four to be uniformly distributed in [0.75; 1]

print ("Stationary distribution: ")
print(stationary)

bonusMalus[0] = 0.75
bonusMalus[1] = 0.82
bonusMalus[2] = 0.88
bonusMalus[3] = 0.94
bonusMalus[4] = 1.0

'''
distance = 0.25
for i in range(1, 5):
    bonusMalus[i] = bonusMalus[i - 1] + distance / 4
'''

for i in range(5, 12):
    bonusMalus[i] = bonusMalus[i - 1] + 2.0

bonusMalus[6] = 6.0

sum = 0.0
for i in range(0, 11):
    if (i != 5):
        sum += bonusMalus[i] * stationary[i]
bonusMalus[5] = (1.0 - sum) / stationary[5]

print("Bonus malus coeficients")
print(bonusMalus)

# Verify E_{pi} f(X_n) = 1

sum = 0.0
for i in range(size):
    sum += bonusMalus[i] * stationary[i]

print("Verify E_pi f(X_n) = ")
print(sum)

# Simulate the process

def getRandomNextState(idx):
    randomNumber = np.random.rand() # uniform in [0; 1)
    sum = 0.0
    for i in range(0, len(nextProbs[idx])):
        if (sum <= randomNumber and randomNumber < sum + nextProbs[idx][i]):
            return nextStates[idx][i]
        sum += nextProbs[idx][i]

trials = 100000
epsilon = 0.1
sumYearsForState = [ 0.0 for _ in range(size) ]
cntTrialsForState = [ 0 for _ in range(size) ]
avgYearsFromState = [ 0.0 for _ in range(size) ]

for i in range(0, trials):
    currentState = i % size
    sumBM = 0.0
    for years in range(1, 65):
        sumBM += bonusMalus[currentState]
        avgBM = sumBM / years
        if (avgBM > 1.0 - epsilon and avgBM < 1.0 + epsilon):
            sumYearsForState[currentState] += years
            break
        currentState = getRandomNextState(currentState)
    cntTrialsForState[currentState] += 1

for i in range(0, size):
    avgYearsFromState[i] = sumYearsForState[i] / cntTrialsForState[i]

print ("Average number of years for each state (simulated): ")
print (avgYearsFromState)

expectationFromState = [ 0 for _ in range(size) ]
for startingState in range(0, size):
    lambda_i = [ 0.0 for _ in range(0, size) ]
    lambda_i[startingState] = 1.0

    currentTransitionMatrix = transitionMatrix
    for year in range(1, 65):
        currentState = np.matmul(lambda_i, currentTransitionMatrix)
        expectation = 0.0
        for i in range(size):
            expectation +=  currentState[i] * bonusMalus[i]
        if (expectation > 1.0 - epsilon and expectation < 1.0 + epsilon):
            expectationFromState[startingState] = year
            break
        currentTransitionMatrix = np.matmul(currentTransitionMatrix, transitionMatrix)

print("Expected number of years for each state: ")
print(expectationFromState)

'''

print ("All people")
numberOfPeople = 50000
currentStatePeople = [0 for _ in range(0, numberOfPeople)]
trials = 50

for i in range(0, trials):
    for j in range(0, numberOfPeople):
        currentStatePeople[j] = np.random.randint(0, size)
    flag = 0
    for year in range(0, 65):
        sumBM = 0.0
        for j in range(0, numberOfPeople):
            sumBM += bonusMalus[currentStatePeople[j]]
            currentStatePeople[j] = getRandomNextState(currentStatePeople[j])
        avgBM = sumBM / numberOfPeople
        if (avgBM > 1.0 - epsilon and avgBM < 1.0 + epsilon):
            sumYears += year
            flag = 1
            break
    if (flag == 0):
        print("hi")

avgYears = sumYears / trials
print (avgYears)

'''
