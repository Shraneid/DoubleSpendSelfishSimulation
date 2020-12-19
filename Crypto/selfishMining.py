import numpy as np
import random as rnd
import pandas as pd
from tqdm import tqdm

nb_simulations = 2000000
alpha = 0
gamma = 0

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
Tho = 10
n0 = 2016
Sn0 = None
B = 1
currentTimestamp = 0

numberOfBlocksBeforeAdjustment = 2016
avgTimePerBlock = 10
latestDifficultyChange = 0  # timestamp


def reset(a=0.35, g=0.5):
    global latestDifficultyChange, B, totalValidatedBlocks, honestValidBlocks, selfishValidBlocks, orphanBlocks, \
        revenueRatio, Sn0, n0, Tho, currentTimestamp, actual_nb_of_steps, privateChainRelative, publicChainRelative, \
        alpha, gamma, nb_simulations, delta, numberOfBlocksBeforeAdjustment, avgTimePerBlock
    nb_simulations = 2000000
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
    Tho = 10
    n0 = 2016
    Sn0 = None
    B = 1
    currentTimestamp = 0

    numberOfBlocksBeforeAdjustment = 2016
    avgTimePerBlock = 10
    latestDifficultyChange = 0  # timestamp


def main(a=0.35, g=0.5):
    reset(a, g)
    global latestDifficultyChange, B, totalValidatedBlocks, honestValidBlocks, selfishValidBlocks, orphanBlocks, \
        revenueRatio, Sn0, n0, Tho, currentTimestamp, actual_nb_of_steps, privateChainRelative, publicChainRelative

    def actualizeAndChangeDifficulty(changeDifficulty):
        global latestDifficultyChange, B, totalValidatedBlocks, honestValidBlocks, selfishValidBlocks, orphanBlocks, \
            revenueRatio, Sn0, n0, Tho, currentTimestamp, privateChainRelative, publicChainRelative

        totalValidatedBlocks = honestValidBlocks + selfishValidBlocks
        orphanBlocks = nb_simulations - totalValidatedBlocks

        if honestValidBlocks or selfishValidBlocks:
            revenueRatio = 100 * selfishValidBlocks / totalValidatedBlocks
        else:
            revenueRatio = 0

        if changeDifficulty:
            Sn0 = currentTimestamp - latestDifficultyChange
            B = B * Sn0 / (n0 * Tho)
            latestDifficultyChange = currentTimestamp

    periodsBetweenDifficultyAdjustment = [numberOfBlocksBeforeAdjustment for _ in
                                          range(nb_simulations // numberOfBlocksBeforeAdjustment)]

    for i in range(len(periodsBetweenDifficultyAdjustment)):
        selfishMinedBlocksTimestamps = map(lambda x: x + currentTimestamp, list(
            np.cumsum(np.random.exponential(1 / alpha * 10 / B, periodsBetweenDifficultyAdjustment[i]))))
        honestMinedBlocksTimestamps = map(lambda x: x + currentTimestamp, list(
            np.cumsum(np.random.exponential(1 / (1 - alpha) * 10 / B, periodsBetweenDifficultyAdjustment[i]))))

        honestBlocksMapping = {x: 'honest' for x in honestMinedBlocksTimestamps}
        selfishBlocksMapping = {x: 'selfish' for x in selfishMinedBlocksTimestamps}

        blocksList = {**honestBlocksMapping, **selfishBlocksMapping}
        blocksList = list(sorted(blocksList.items()))

        # print(blocksList[2016])

        # for block in blocksList[:5]:
        #     print(f"timestamp : {block[0]}, class : {block[1]}")

        for j in range(len(blocksList)):
            # stop condition
            if actual_nb_of_steps > nb_simulations:
                break

            blockNumber = j
            block = blocksList[j]

            currentTimestamp = block[0]

            if block[1] == "selfish":
                # handle selfish mining
                delta = privateChainRelative - publicChainRelative
                privateChainRelative += 1

                if delta == 0 and privateChainRelative == 2:
                    privateChainRelative, publicChainRelative = 0, 0
                    selfishValidBlocks += 2

                actualizeAndChangeDifficulty(changeDifficulty=False)

            else:
                # handle honest mining
                delta = privateChainRelative - publicChainRelative
                publicChainRelative += 1

                if delta == 0:
                    honestValidBlocks += 1

                    # if private chain has 1 block hidden, the selfish chain releases it's block, competition follows
                    if privateChainRelative > 0:
                        # random to determine who wins the fight between selfish and honest when 2 blocks are sent at the
                        # same time
                        rand = rnd.uniform(0, 1)

                        # maybe to change
                        if rand <= gamma:
                            selfishValidBlocks += 1
                        else:
                            honestValidBlocks += 1

                    # in both cases, we reset both relative chains to 0
                    privateChainRelative, publicChainRelative = 0, 0

                elif delta == 2:
                    selfishValidBlocks += privateChainRelative
                    privateChainRelative, publicChainRelative = 0, 0

                actualizeAndChangeDifficulty(changeDifficulty=False)

            if totalValidatedBlocks > (i + 1) * numberOfBlocksBeforeAdjustment:
                # actualize and change difficulty
                actualizeAndChangeDifficulty(changeDifficulty=True)
                break

            actual_nb_of_steps += 1

    actualizeAndChangeDifficulty(changeDifficulty=False)

    print(f"""honest blocks : {honestValidBlocks}
selfish blocks : {selfishValidBlocks}
total blocks : {totalValidatedBlocks}

orphan blocks : {orphanBlocks}

revenue ratio \t\t\t: \t{round(revenueRatio, 1)}%
revenue ratio if honest : \t{alpha*100}%""")

    # stats
    qPrime = (totalValidatedBlocks-honestValidBlocks) / totalValidatedBlocks

    ET0 = ((qPrime * (1.27-1)) / (qPrime - alpha))

    print(f"ET0 = {ET0}")

    if alpha == 1:
        return 100, alpha * 100
    else:
        return round(revenueRatio, 1), alpha * 100


print(main(0.5, 1))

# resS = []
# resH = []
#
# for alpha in tqdm(np.linspace(0, 0.5, 11)):
#     rowS = []
#     rowH = []
#     for gamma in np.linspace(0, 1, 11):
#         r = main(alpha, gamma)
#         rowS.append(r[0])
#         rowH.append(r[1])
#         # print("__________________________")
#
#     resS.append(rowS)
#     resH.append(rowH)
#
# # columns for dataframes
# alphas = [round(x, 2) for x in np.linspace(0, 0.5, 11)]
# gammas = [round(x, 2) for x in np.linspace(0, 1, 11)]
#
# dfS = pd.DataFrame(resS, columns=gammas)
# dfH = pd.DataFrame(resH, columns=gammas)
#
# dfS = dfS.T
# dfH = dfH.T
#
# dfS.columns = alphas
# dfH.columns = alphas
#
# print(dfS)
# print()
# print(dfH)
