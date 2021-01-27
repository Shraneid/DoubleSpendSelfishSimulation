# Cryptofinance :cactus:

## Simulation de l'attaque originelle de Satoshi :racehorse:

On imagine qu'un attaquant répète sans arrêt (ou un grand nombre de fois) l'attaque décrite par Satoshi Nakamoto dans son papier fondateur.

Input : nombre de cycles d'attaques (n), taux de hachage relatif (q), seuil de sécurité fixé par le vendeur i.e., nombre de confirmations (z), seuil de tolérance (A) i.e., retard maximal autorisé par l'attaquant sur la blockchain officielle, nombre de blocs préminés par l'attaquant au début de son attaque (k), montant de la double dépense (v). L'attaque de Satoshi correspond à k = 1.

Output : taux de rendement de la stratégie

Pour n, A, k, z fixés, tracer la courbe qui donne le taux de rendement de la stratégie en fonction de q. Tracer et donner la possibilité à un utilisateur de modifier simplement les constantes n, A, k ,z (équivalent du Manipulate sur Mathematica).

On suppose qu'il n'y a pas d'ajustement de difficulté. Nous devons identifier les régions où l'attaque est plus rentable que la stratégie honnête de minage.

### What is a double spend attack ?

> "Double-spend Attack Models with Time Advantange for Bitcoin", Carlos Pinzon, Camilo Rocha

This section presents an overview of how double-spend attacks can happen in the Bitcoin network. It is known that falsifying a digital signature is a hard computational problem.
Therefore, it is practically useless to try to modify a valid transaction that has been signed. However, there’s still a technique that can be used to deceive someone about
the state of a transaction. This kind of attack to the Bitcoin network is called a double-spend attack. Even though it requires a tremendous computational power
and it is very likely to fail, it may be profitable. As a matter of fact, it has happened already.

A double-spend attack can be performed as follows:

1. The attacker A wants a service or a product from B
2. A creates two transactions: one paying to B and another paying to himself, using the the same input for the transactions.
3. A publishes the “A to B” payment and secretly starts mining a block containing the “A to A” payment. Once the latter mining task succeeds, it continues to add blocks after it.
4. B gives the product or service to A, since the payment was confirmed or B did not wait long enough.
5. A is lucky and the fraudulent branch becomes longer than the valid one. The attacker nodes publish all the blocks in the new branch and all the nodes agree on considering them as the valid ones since the branch is longer than the current valid branch.
6. B gave out the product or service to A without receiving any payment. At this point, B can not find A because it is anonymous or has left.

![usecase1](https://github.com/victorlrz/DoubleSpendSelfishSimulation/blob/main/Crypto/docs/DoubleSpend.JPG)

Figure 4 depicts some stages of a successful double-spend attack. Stage (a) depicts the initial state of the blockchain. In Stage (b), honest nodes are extending
the valid chain by putting valid blocks, while the attacker secretly starts mining a fraudulent branch. In Stage (c), the attacker succeeds in making the fraudulent
branch longer than the honest one. Finally, in Stage (d), the attacker’s branch is published and is now considered the valid one.

### The Model of S. Nakamoto

> "Double-spend Attack Models with Time Advantange for Bitcoin", Carlos Pinzon, Camilo Rocha

The double-spend attack model of S. Nakamoto computes the probability of a double-spend attack by combining the probability of the attacker having mined
exactly n blocks once the honest nodes mine the K’th confirmation block, with the probability of catching-up from a K − n block difference. The double-spend
attack model of S. Nakamoto in considers that the attacker has exactly mined 1 fraudulent block before starting the attack, but it can be easily modified to handle
an advantage of n fraudulent blocks.

![usecase1](https://github.com/victorlrz/DoubleSpendSelfishSimulation/blob/main/Crypto/docs/AttackersPotentialProgress.JPG)

```
# Attacker's potential progress function
def P_N(q,m,n):
    return poisson.pmf(n, m*q/(1-q))
```

![usecase2](https://github.com/victorlrz/DoubleSpendSelfishSimulation/blob/main/Crypto/docs/CatchUpFunction.JPG)

```
# Catch up function
def C(q,z):
    if z<0 or q>=0.5:
        prob = 1
    else:
        prob = (q/(1-q)) ** (z+1)
    return prob
```

![usecase3](https://github.com/victorlrz/DoubleSpendSelfishSimulation/blob/main/Crypto/docs/DoubleSpendAttackProbability.JPG)

```
# Double-spend attack probability
def DS_N(q,K):
    return 1-sum(P_N(q,K,n)*(1-C(q,K-n-1)) for n in range(0,K+1))
```

We finally define our custom double spend function :

```
def doublespendfun(x, n, z, A, k, v):
    out = [v*DS_N(float(q_value), k) for q_value in x]

    return out
```

The user can custom the input parameters threw a small application. Just run the script in order to play with it !

## Simulation de l'attaque de minage égoïste

On imagine qu'un attaquant répète sans arrêt (ou un grand nombre de fois) la stratégie déviante de minage égoïste.

Input : nombre de cycles d'attaques (n), taux de hachage relatif (q), connectivité de l'attaquant (gamma)

Output : taux de rendement de la stratégie et durée avant que la stratégie ne devienne rentable.

Tracer la courbe qui donne le taux de rendement de la stratégie en fontion de q et gamma. Comparer au taux de rendement de la stratégie classique.

On prend en compte l'ajustement de difficulté dans le calcul du taux de rendement de la stratégie (on calcule le taux de rendement de la stratégie à long-terme)

### Selfish mining strategy

> C. GRUNSPAN AND R. PEREZ-MARCO

We describe the selfish mining strategy presented in [5]. The selfish miner attack
starts by validating and not broadcasting a block, then continuing mining secretly on
top of this block. Then he proceeds as follows:

1. If the advance of the selfish miner is only equal to 1 block and the honest
   miners discover a block then the selfish miner broadcasts immediately the
   block he has mined secretly. A competition then follows. The selfish miner is
   assumed to be suficiently well connected with the rest of the network so that
   a fraction 0 <= gamma <= 1 of the honest network accepts his block proposal and
   starts mining on top of it.

2. If the advance of the selfish miner is 2 blocks and the honest miners discover
   a block, then the selfish miner broadcasts immediately the two blocks he had
   mined secretly. Then, the whole network switches to his fork.

3. If the advance of the selfish miner is greater than 2, then the selfish miner
   releases a block as soon as the honest miners discovers one.

4. In other cases, the selfish miner keeps on mining secretly on top of his fork.

Note that if the advance of the miner is greater than 2, then at some point the
advance of the selfish miner will be equal to 2 (because we assume that his hashrate is
less than 50%, otherwise other more efficient attacks are possible) and then, according
to the second point, the whole network ends up adopting the fork proposed by the
selfish miner. Therefore, the blocks made public by the selfish miner when his advance
is greater than 2 always end up being accepted by the network.

### 2.1 Cas de Bitcoin

Ici, on considère l'ajustement de difficulté implémentée dans Bitcoin Core: l'ajustement se fait tous les 2016 blocs en prenant en compte la durée mise pour valider ces derniers 2016 blocs. La difficulté de minage est constante par morceau (par parliers de 2016 blocs)

![usecase4](https://github.com/victorlrz/DoubleSpendSelfishSimulation/blob/main/Crypto/docs/Corollaire.JPG)

On obtient les résulats suivants :

Exemple pour alpha = 0.2 et gamma = 0.75

- honest : 20.0%
- selfish_avg : 20.8%
- avg time to be profitable : 30102 minutes / 21 days

![usecase4](https://github.com/victorlrz/DoubleSpendSelfishSimulation/blob/main/Crypto/docs/bitcoin.png)

You can run the script and change the parameters !

### 2.2 Cas de Bitcoin Cash

![usecase5](https://github.com/victorlrz/DoubleSpendSelfishSimulation/blob/main/Crypto/docs/bcashcase.JPG)

Example pour alpha = 0.2 et gamma = 0.75
{'selfish': 21.9, 'profitable': True}

![usecase4](https://github.com/victorlrz/DoubleSpendSelfishSimulation/blob/main/Crypto/docs/bcash.png)

You can run the script and change the parameters !

### 2.3 Cas de Bitcoin avec prise en compte des blocs orphelins

On suppose ici que l'ajustement de difficulté prend en compte la production de blocs orphelins.

Example pour alpha = 0.2 et gamma = 0.75

- honest : 20.0%
- selfish_avg : 20.9%
- avg time to be profitable : 28078 minutes / 19 days

## Authors :couple_with_heart: :two_men_holding_hands:

- Quentin Tourette
- Victor Larrezet
