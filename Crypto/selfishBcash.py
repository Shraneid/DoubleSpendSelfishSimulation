import numpy as np
import random as rnd

alpha = 0.2
gamma = 0.75

def main(a=0.35, g=0.5, nb_sim=1000000):
    global B, revenueRatio

    nb_simulations = nb_sim
    alpha = a
    gamma = g

    delta = 0
    selfishForkRelative = 0  # relative
    mainForkRelative = 0

    honestValidBlocks = 0  # absolute
    selfishValidBlocks = 0

    totalNumberOfBlocksMined = 1

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
        orphanBlocks = totalNumberOfBlocksMined - totalValidatedBlocks

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

        if revenueRatio > alpha and totalNumberOfBlocksMined > 144:
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
            if totalNumberOfBlocksMined > nb_simulations or not running:
                break

            block = blocksList[j]

            currentTimestamp = block[0]

            if block[1] == "selfish":
                # handle selfish mining
                delta = selfishForkRelative - mainForkRelative
                selfishForkRelative += 1

                if delta == 0 and selfishForkRelative == 2:
                    selfishForkRelative, mainForkRelative = 0, 0
                    selfishValidBlocks += 2

                    running = actualizeAndChangeDifficulty([blocksList[j - 1][0], currentTimestamp])

            else:
                # handle honest mining
                delta = selfishForkRelative - mainForkRelative
                mainForkRelative += 1

                if delta == 0:
                    honestValidBlocks += 1
                    running = actualizeAndChangeDifficulty([currentTimestamp])

                    # if private chain has 1 block hidden, the selfish chain releases it's block, competition follows
                    if selfishForkRelative > 0:
                        rand = rnd.uniform(0, 1)

                        # maybe to change
                        if rand <= gamma:
                            selfishValidBlocks += 1
                            running = actualizeAndChangeDifficulty([currentTimestamp])
                        else:
                            honestValidBlocks += 1
                            running = actualizeAndChangeDifficulty([currentTimestamp])

                    # in both cases, we reset both relative chains to 0
                    selfishForkRelative, mainForkRelative = 0, 0

                elif delta >= 2:
                    selfishValidBlocks += selfishForkRelative
                    selfishForkRelative, mainForkRelative = 0, 0

                    running = actualizeAndChangeDifficulty([blocksList[j - 1][0], currentTimestamp])

            if totalValidatedBlocks > (i + 1) * numberOfBlocksBeforeAdjustment:
                break

            totalNumberOfBlocksMined += 1

    if revenueRatio > alpha:
        return {"simulated_ratio": round(revenueRatio, 3) * 100,
                "honest_ratio": alpha * 100,
                "time_to_end": totalNumberOfBlocksMined*10
                }
    else:
        return {"simulated_ratio": round(revenueRatio, 3) * 100,
                "honest_ratio": alpha * 100,
                "time_to_end": -1
                }


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


print(get_avg(alpha, gamma))
