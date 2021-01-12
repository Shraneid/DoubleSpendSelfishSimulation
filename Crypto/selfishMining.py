import numpy as np
import random as rnd


def main(a, g, nb_sim=1000000):
    # those variables need to be global, to be used in our update function
    global latestDifficultyChange, B, revenueRatio, totalValidatedBlocks

    # initializing variables
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
    Tho = 10
    n0 = 2016
    Sn0 = None
    B = 1
    currentTimestamp = 0

    numberOfBlocksBeforeAdjustment = 2016
    avgTimePerBlock = 10
    latestDifficultyChange = 0  # timestamp


    def actualizeAndChangeDifficulty(changeDifficulty):
        global totalValidatedBlocks, latestDifficultyChange, B, revenueRatio

        # we update values to check if we can stop the simulation or go on
        totalValidatedBlocks = honestValidBlocks + selfishValidBlocks
        orphanBlocks = totalNumberOfBlocksMined - totalValidatedBlocks

        if honestValidBlocks or selfishValidBlocks:
            revenueRatio = selfishValidBlocks / totalValidatedBlocks
        else:
            revenueRatio = -1

        if changeDifficulty:
            Sn0 = currentTimestamp - latestDifficultyChange
            B = B * Sn0 / (n0 * Tho)
            latestDifficultyChange = currentTimestamp

        # we stop the simulation if we are profitable
        if revenueRatio > alpha and totalNumberOfBlocksMined > 2016:
            return False

        return True


    periodsBetweenDifficultyAdjustment = [numberOfBlocksBeforeAdjustment for _ in
                                          range(nb_simulations // numberOfBlocksBeforeAdjustment)]
    running = True

    for i in range(len(periodsBetweenDifficultyAdjustment)):
        if not running:
            break

        selfishList = list(np.cumsum(np.random.exponential(1 / alpha * 10 / B, int(periodsBetweenDifficultyAdjustment[i]))))
        honestList = list(np.cumsum(np.random.exponential(1 / (1 - alpha) * 10 / B, int(periodsBetweenDifficultyAdjustment[i]))))

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

                running = actualizeAndChangeDifficulty(False)

            else:
                # handle honest mining
                delta = selfishForkRelative - mainForkRelative
                mainForkRelative += 1

                if delta == 0:
                    honestValidBlocks += 1

                    # if private chain has 1 block hidden, the selfish chain releases it's block, competition follows
                    if selfishForkRelative > 0:
                        # random to determine who wins the fight between selfish and honest when 2 blocks are sent at the
                        # same time
                        rand = rnd.uniform(0, 1)

                        # maybe to change
                        if rand <= gamma:
                            selfishValidBlocks += 1
                        else:
                            honestValidBlocks += 1
                    selfishForkRelative, mainForkRelative = 0, 0

                elif delta >= 2:
                    selfishValidBlocks += selfishForkRelative
                    selfishForkRelative, mainForkRelative = 0, 0

                running = actualizeAndChangeDifficulty(False)

            if totalValidatedBlocks > (i + 1) * numberOfBlocksBeforeAdjustment:
                # actualize and change difficulty
                running = actualizeAndChangeDifficulty(True)
                break

            totalNumberOfBlocksMined += 1

    actualizeAndChangeDifficulty(False)

    """print(f"honest blocks : {honestValidBlocks}\
selfish blocks : {selfishValidBlocks}\
total blocks : {totalValidatedBlocks}\
\
orphan blocks : {orphanBlocks}\
\
revenue ratio \t\t\t: \t{round(revenueRatio, 1)}%\
revenue ratio if honest : \t{alpha*100}%")"""

    """if revenueRatio/100 > alpha:
        print(f"Selfish mining became profitable after {totalNumberOfBlocksMined*10} minutes.")
    else:
        print("Selfish mining was never profitable")"""

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


# print(main(0.2, 0.8))

alpha = 0.2
gamma = 0.75


sel = []
res = []
result = None
for i in range(100):
    result = main(alpha, gamma, 1000000)
    if result['time_to_end'] == -1:
        print(f"honest : {result['honest_ratio']}, selfish : {result['simulated_ratio']}, not profitable")
        break

    sel.append(result['simulated_ratio'])
    res.append(result['time_to_end'])

if len(res) == 100 and len(sel) == 100:
    minutes_to_profit = round(sum(res) / len(res))
    print(f"honest : {result['honest_ratio']}%\nselfish_avg : {round(sum(sel)/len(sel), 1)}%\navg time to be profitable : {minutes_to_profit} minutes / {round(minutes_to_profit/(24*60))} days")

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
