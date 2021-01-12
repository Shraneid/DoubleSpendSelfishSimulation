import numpy as np
import random as rnd
import pandas as pd
from tqdm import tqdm


def main(a=0.35, g=0.5, nb_sim=1000000):
    global B, revenueRatio

    nb_simulations = nb_sim
    alpha = a
    gamma = g

    delta = 0
    privateChainRelative = 0  # relative
    publicChainRelative = 0

    honestValidBlocks = 0  # absolute
    selfishValidBlocks = 0

    actual_nb_of_steps = 1

    revenueRatio = None
    orphanBlocks = 0
    totalValidatedBlocks = 0

    # For difficulty adjustment
    Tau0 = 600
    n0prime = 144
    Sn0 = None
    B = 1
    currentTimestamp = 0

    numberOfBlocksBeforeAdjustment = 2016
    avgTimePerBlock = 10

    validatedBlockTimestamps = []


    def actualizeAndChangeDifficulty(timestampsList):
        global B, revenueRatio, totalValidatedBlocks

        totalValidatedBlocks = honestValidBlocks + selfishValidBlocks
        orphanBlocks = actual_nb_of_steps - totalValidatedBlocks

        if honestValidBlocks or selfishValidBlocks:
            revenueRatio = selfishValidBlocks / totalValidatedBlocks
        else:
            revenueRatio = 0

        for timestamp in timestampsList:
            validatedBlockTimestamps.append(timestamp)

        if totalValidatedBlocks >= 144:
            deltaT = round(currentTimestamp, 5) - round(validatedBlockTimestamps[0], 5)
            B = B * ((n0prime * Tau0) / deltaT)

            while len(validatedBlockTimestamps) >= 144:
                validatedBlockTimestamps.pop(0)

        if revenueRatio > alpha and actual_nb_of_steps > 144:
            return False

        return True


    periodsBetweenDifficultyAdjustment = [numberOfBlocksBeforeAdjustment for _ in
                                          range(nb_simulations // numberOfBlocksBeforeAdjustment)]
    running = True

    for i in range(len(periodsBetweenDifficultyAdjustment)):
        if not running:
            break

        selfishList = list(
            np.cumsum(np.random.exponential(1 / alpha * 10 / B, int(periodsBetweenDifficultyAdjustment[i]))))
        honestList = list(
            np.cumsum(np.random.exponential(1 / (1 - alpha) * 10 / B, int(periodsBetweenDifficultyAdjustment[i]))))

        selfishMinedBlocksTimestamps = map(lambda x: x + currentTimestamp, selfishList)
        honestMinedBlocksTimestamps = map(lambda x: x + currentTimestamp, honestList)

        honestBlocksMapping = {x: 'honest' for x in honestMinedBlocksTimestamps}
        selfishBlocksMapping = {x: 'selfish' for x in selfishMinedBlocksTimestamps}

        blocksList = {**honestBlocksMapping, **selfishBlocksMapping}
        blocksList = list(sorted(blocksList.items()))

        for j in range(int(len(blocksList))):
            # stop condition
            if actual_nb_of_steps > nb_simulations or not running:
                break

            block = blocksList[j]

            currentTimestamp = block[0]

            if block[1] == "selfish":
                # handle selfish mining
                delta = privateChainRelative - publicChainRelative
                privateChainRelative += 1

                if delta == 0 and privateChainRelative == 2:
                    privateChainRelative, publicChainRelative = 0, 0
                    selfishValidBlocks += 2

                    running = actualizeAndChangeDifficulty([blocksList[j - 1][0], currentTimestamp])

            else:
                # handle honest mining
                delta = privateChainRelative - publicChainRelative
                publicChainRelative += 1

                if delta == 0:
                    honestValidBlocks += 1
                    running = actualizeAndChangeDifficulty([currentTimestamp])

                    # if private chain has 1 block hidden, the selfish chain releases it's block, competition follows
                    if privateChainRelative > 0:
                        rand = rnd.uniform(0, 1)

                        # maybe to change
                        if rand <= gamma:
                            selfishValidBlocks += 1
                            running = actualizeAndChangeDifficulty([currentTimestamp])
                        else:
                            honestValidBlocks += 1
                            running = actualizeAndChangeDifficulty([currentTimestamp])

                    # in both cases, we reset both relative chains to 0
                    privateChainRelative, publicChainRelative = 0, 0

                elif delta >= 2:
                    selfishValidBlocks += privateChainRelative
                    privateChainRelative, publicChainRelative = 0, 0

                    running = actualizeAndChangeDifficulty([blocksList[j - 1][0], currentTimestamp])

            if totalValidatedBlocks > (i + 1) * numberOfBlocksBeforeAdjustment:
                break

            actual_nb_of_steps += 1


    if revenueRatio > alpha:
        return {"simulated_ratio": round(revenueRatio, 3) * 100,
                "honest_ratio": alpha * 100,
                "time_to_end": actual_nb_of_steps*10
                }
    else:
        return {"simulated_ratio": round(revenueRatio, 3) * 100,
                "honest_ratio": alpha * 100,
                "time_to_end": -1
                }



alpha = 0.3
gamma = 0.75

#print(main(alpha, gamma))


def get_avg(alpha, gamma):
    sel = []
    res = []
    result = None
    for i in range(100):
        result = main(alpha, gamma, 200000)
        """if result['time_to_end'] == -1:
            print(f"honest : {result['honest_ratio']}, selfish : {result['simulated_ratio']}, not profitable")
            return {"selfish": result['simulated_ratio'], "time": -1}"""

        sel.append(result['simulated_ratio'])
        res.append(result['time_to_end'])

    if len(res) == 100 and len(sel) == 100:
        minutes_to_profit = round(sum(res) / len(res))
        return {"selfish": round(sum(sel)/len(sel), 1), "profitable": True}

    else:
        return {"selfish": round(sum(sel)/len(sel), 1), "profitable": False}

print(get_avg(0.1, 0.0))

"""resS = []
resH = []

for alpha in tqdm(np.linspace(0, 0.5, 11)):
    rowS = []
    rowH = []
    for gamma in np.linspace(0, 1, 11):
        r = get_avg(alpha, gamma)
        rowS.append([r["selfish"], r["profitable"]])
        # print("__________________________")

    resS.append(rowS)

# columns for dataframes
alphas = [round(x, 2) for x in np.linspace(0, 0.5, 11)]
gammas = [round(x, 2) for x in np.linspace(0, 1, 11)]

dfS = pd.DataFrame(resS, columns=gammas)
#dfH = pd.DataFrame(resH, columns=gammas)

dfS = dfS.T
#dfH = dfH.T

dfS.columns = alphas
#dfH.columns = alphas

print(dfS)"""
"""print()
print(dfH)"""
