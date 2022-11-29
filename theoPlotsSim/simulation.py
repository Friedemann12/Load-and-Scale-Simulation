from math import factorial

import matplotlib
import matplotlib.pyplot as plt

font = {
    "family": "serif",
    "size": 20,
}
fontLabel = {
    "family": "serif",
    "size": 30,
}


def setRcParams():
    plt.style.context('science')
    plt.rcParams["figure.figsize"] = (20, 7.5)
    plt.rcParams["text.usetex"] = True
    matplotlib.rc("font", **font)


def ErlangC(rho, m):
    zaehler = (((m * rho) ** m) / factorial(m)) * (1.0 / (1.0 - rho))
    nenner = 0
    for k in range(0, m):
        nenner += (((m * rho) ** k) / factorial(k)) + (((m * rho) ** m) / factorial(m)) * (1 / (1 - rho))
    return zaehler / nenner


def clacProp(Lambda, mu, m):
    x = 0
    for k in range(0, m):
        x += (1 / factorial(k)) * (Lambda / mu) + (1 / factorial(m)) * ((Lambda / mu) ** m) * (
                (m * mu) / ((m * mu) - Lambda))
    return 1 / x


def calcPropIdle(rho, m):
    x = 0
    for k in range(0, m):
        x += ((m * rho) ** k) / factorial(k)
    x += ((m * rho) ** m) * (1.0 / factorial(m)) * (1.0 / (1.0 - rho))
    return x ** -1


def calcAverageJobsInQueue(P_0, m, Lambda, mu):
    return ((1 / factorial(m - 1)) * ((Lambda / mu) ** m) * ((Lambda * mu) / (((m * mu) - Lambda) ** 2))) * P_0


def calcAverageNumberOfJobs(L_Q, Lambda, mu):
    return L_Q + (Lambda / mu)


def calcWaitingTimeInQueue(L_Q, Lambda):
    return L_Q / Lambda


def calcWaitingTimeInSystem(L_S, Lambda):
    return L_S / Lambda


def calcPropAllServerBusy(P_0, m, Lambda, mu):
    return ((1 / factorial(m)) * ((Lambda / mu) ** m) * ((m * mu) / ((m * mu) - Lambda) ** 2)) * P_0


def plotTimePerLambda():
    setRcParams()
    Lambda = 1
    m = 1
    fig, ax = plt.subplots()
    L = 101
    mu = 101

    for _ in range(0, 100):
        # Service Rate M/M/1-Wartschlange
        ##print(Lambda)
        T1 = 1 / (L - Lambda)

        # Probability of no units in the system
        rho = Lambda / (mu * m)
        # print(rho)

        P_0 = calcPropIdle(rho, m)
        print(P_0)

        L_Q = calcAverageJobsInQueue(P_0, m, Lambda, mu)
        # print(L_Q)

        L_S = calcAverageNumberOfJobs(L_Q, Lambda, mu)
        # print(L_S)

        W_Q = calcWaitingTimeInQueue(L_Q, Lambda)
        # print(W_Q)

        W_S = calcWaitingTimeInSystem(L_S, Lambda)
        # print(W_S)

        P_busy = calcPropAllServerBusy(P_0, m, Lambda, mu)
        # print(P_busy)

        T2 = W_S

        T = T1 + T2

        ax.bar(Lambda, T, color="blue")

        Lambda += 1

    plt.xlabel("Ankuntsrate ($\lambda$)", fontdict=fontLabel, labelpad=15)
    plt.ylabel("Zeit in Sekunden", fontdict=fontLabel, labelpad=15)
    plt.savefig(f'Plots/TimePerLambda_M{m}.png', bbox_inches='tight', dpi=200)
    plt.clf()


def plotTimePerLambdaOnlyMMm():
    setRcParams()
    Lambda = 1
    m = 3
    fig, ax = plt.subplots()
    L = 101
    mu = 101

    for _ in range(0, 100):
        # Service Rate M/M/1-Wartschlange
        ##print(Lambda)

        # Probability of no units in the system
        rho = Lambda / (mu * m)
        # print(rho)

        P_0 = calcPropIdle(rho, m)
        # print(P_0)

        L_Q = calcAverageJobsInQueue(P_0, m, Lambda, mu)
        # print(L_Q)

        L_S = calcAverageNumberOfJobs(L_Q, Lambda, mu)
        # print(L_S)

        W_Q = calcWaitingTimeInQueue(L_Q, Lambda)
        # print(W_Q)

        W_S = calcWaitingTimeInSystem(L_S, Lambda)
        # print(W_S)

        P_busy = calcPropAllServerBusy(P_0, m, Lambda, mu)
        # print(P_busy)

        T2 = W_S

        T = T2

        ax.bar(Lambda, T, color="blue")

        Lambda += 1

    plt.xlabel("Ankuntsrate ($\lambda$)", fontdict=fontLabel, labelpad=15)
    plt.ylabel("Zeit in Sekunden", fontdict=fontLabel, labelpad=15)
    plt.savefig(f'Plots/TimePerLambdaOnlyMMm_M{m}.png', bbox_inches='tight', dpi=200)
    plt.clf()


def plotIdleServers():
    setRcParams()
    Lambda = 10
    m = 2
    fig, ax = plt.subplots()
    mu = 11

    for _ in range(0, 5):
        # Probability of no units in the system
        rho = Lambda / (mu * m)
        # print(rho)

        P_0 = calcPropIdle(rho, m)
        print(P_0)

        L_Q = calcAverageJobsInQueue(P_0, m, Lambda, mu)
        # print(L_Q)

        L_S = calcAverageNumberOfJobs(L_Q, Lambda, mu)
        # print(L_S)

        ax.bar(m, P_0 * 100, color="green")

        m += 1

    plt.xlabel("Anzahl Server", fontdict=fontLabel, labelpad=15)
    plt.ylabel("Wahrscheinlichkeit Leerlauf in %", fontdict=fontLabel, labelpad=15)
    plt.savefig(f'Plots/WskIdle.png', bbox_inches='tight', dpi=200)
    plt.clf()


#plotTimePerLambda()
#plotIdleServers()
plotTimePerLambdaOnlyMMm()

# Lambda = np.linspace(0, 2, 100)

# Akunftsrate


######################################################################################


# print(ErlangC((10/20), 10))

# T1 = (1.0 / L) / (1.0 - (Lambda / L))

# tau = 0.19

##gamma = Lambda / (1.0 - tau)

##rho = gamma / mu

##C = ErlangC(rho, m)
# T2 = (((mu * (Lambda / mu)) ** m) / (factorial(m - 1) * ((m * mu) - Lambda) ** 2)) * P_0 + (1 / mu)

# T2 = (1 / mu) + (C / (m * mu - gamma))
