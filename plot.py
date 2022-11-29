from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import latex

Versuch = "Versuch3_2"
FilePath = f"Messungen/{Versuch}/"

for filename in os.listdir(FilePath):
    root, ext = os.path.splitext(filename)
    if root.startswith("Container"):
        fileNameContainerStats = filename
    elif root.startswith("Loadbalancer"):
        fileNameLoadbalancerStats = filename
    elif root.startswith("Timestamps"):
        fileNameTimestamps = filename


def PlotContainerStats():
    ContainerStatsStartTime = float(open(
        f"{FilePath}{fileNameContainerStats}", "r").readline())

    ContainerStatsDF = pd.read_csv(f"{FilePath}{fileNameContainerStats}",
                                   sep=":", header=1)
    ContainerStatsDF = ContainerStatsDF[ContainerStatsDF["Name"] != "--"]
    ContainerStatsEndTime = (max(ContainerStatsDF["Timestamp"]))
    ContainerStatsDF["CPUPercent"] = ContainerStatsDF["CPUPercent"].apply(
        lambda x: float(x.strip("%")))
    ContainerStatsDF["TimeDiff"] = ContainerStatsDF["Timestamp"].apply(
        lambda x: x - ContainerStatsStartTime)
    setRcParams()
    timeRange = np.arange(min(ContainerStatsDF["TimeDiff"]),
                          max(ContainerStatsDF["TimeDiff"]) + 5, 20)
    plt.xticks(timeRange)
    plt.yticks(np.arange(min(ContainerStatsDF["CPUPercent"]),
                         max(ContainerStatsDF["CPUPercent"]) + 10, 10))

    test = ContainerStatsDF.groupby("Name")

    for group in test.groups.keys():
        plt.plot(test.get_group(group)["TimeDiff"], test.get_group(group)["CPUPercent"])
        #, label=group

#    plt.legend(bbox_to_anchor=(1, 0.5), loc='center left')
    plt.xlabel("Time", fontdict=fontLabel, labelpad=15)
    plt.ylabel("Cpu Usage in percent", fontdict=fontLabel, labelpad=15)
    plt.savefig(f'Plots/{Versuch}_ContainerStatsCPU.png', bbox_inches='tight', dpi=200)
    plt.clf()

    # 19.46MiB / 30.65GiB
    ContainerStatsDF["MemUsage"] = ContainerStatsDF["MemUsage"]\
        .apply(lambda x: x.split("MiB")[0])
    ContainerStatsDF["MemUsage"] = ContainerStatsDF["MemUsage"]\
        .apply(lambda x: x.split("B")[0])
    ContainerStatsDF["MemUsage"] = ContainerStatsDF["MemUsage"]\
        .apply(lambda x: x.split("KiB")[0])
    ContainerStatsDF["MemUsage"] = ContainerStatsDF["MemUsage"].\
        apply(lambda x: x.split("GiB")[0])
    ContainerStatsDF["MemUsage"] = ContainerStatsDF["MemUsage"].\
        apply(lambda x: float(x))
    ContainerStatsDF["TimeDiff"] = ContainerStatsDF["Timestamp"].\
        apply(lambda x: x - ContainerStatsStartTime)
    setRcParams()
    timeRange = np.arange(min(ContainerStatsDF["TimeDiff"]),
                          max(ContainerStatsDF["TimeDiff"]) + 5, 20)
    plt.xticks(timeRange)
    plt.yticks(np.arange(min(ContainerStatsDF["MemUsage"]),
                         max(ContainerStatsDF["MemUsage"]) + 1, 5))
    test = ContainerStatsDF.groupby("Name")

    for group in test.groups.keys():
        plt.plot(test.get_group(group)["TimeDiff"], test.get_group(group)["MemUsage"])

 #   plt.legend(bbox_to_anchor=(1, 0.5), loc='center left')
    plt.xlabel("Time", fontdict=fontLabel, labelpad=15)
    plt.ylabel("Memory Usage in MiB", fontdict=fontLabel, labelpad=15)
    plt.savefig(f'Plots/{Versuch}_ContainerStatsRAM.png', bbox_inches='tight', dpi=200)
    plt.clf()


def PlotLoadbalancerStats():
    LoadbalancerStats = pd.read_csv(f"{FilePath}{fileNameLoadbalancerStats}"
                                    , sep=":", header=0)
    # CPU
    setRcParams()
    LoadbalancerStats["CPU"] = LoadbalancerStats["CPU"].apply(lambda x: float(x.strip(" %")))
    plt.plot(range(LoadbalancerStats["CPU"].count()), LoadbalancerStats["CPU"])
    plt.xticks(np.arange(min(range(LoadbalancerStats["Memory"].count())),
                         max(range(LoadbalancerStats["Memory"].count())) + 1, 10))
    plt.yticks(np.arange(min(LoadbalancerStats["CPU"]), max(LoadbalancerStats["CPU"]) + 1, 5))
    plt.xlabel("Time", fontdict=fontLabel, labelpad=15)
    plt.ylabel("Cpu Usage in percent", fontdict=fontLabel, labelpad=15)
    plt.savefig(f'Plots/{Versuch}_LoadbalancerStatsCPU.png', bbox_inches='tight', dpi=200)
    plt.clf()

    # RAM
    setRcParams()
    LoadbalancerStats["Memory"] = LoadbalancerStats["Memory"]\
        .apply(lambda x: float(x.strip(" MiB")))
    plt.plot(range(LoadbalancerStats["Memory"].count()), LoadbalancerStats["Memory"])
    plt.xticks(np.arange(min(range(LoadbalancerStats["Memory"].count())),
                         max(range(LoadbalancerStats["Memory"].count())) + 1, 10))
    plt.yticks(np.arange(round(min(LoadbalancerStats["Memory"])),
                         round(max(LoadbalancerStats["Memory"])) + 1, 0.5))
    plt.xlabel("Time", fontdict=fontLabel, labelpad=15)
    plt.ylabel("Memory Usage in MiB", fontdict=fontLabel, labelpad=15)
    plt.savefig(f'Plots/{Versuch}_LoadbalancerStatsRAM.png', bbox_inches='tight', dpi=200)
    plt.clf()


def PlotTimestamps():
    # 0|1666362474.1514375|RequestID:8ce4aa85-514c-11ed-b603-359305e241e9|
    # Client:8ce4aa84-514c-11ed-b603-359305e241e9|Send new Request
    colnames = ["Index", "Timestamp", "RequestID", "ClientID", "Message"]
    TimestampsDF = pd.read_csv(f"{FilePath}{fileNameTimestamps}", sep="|", names=colnames)

    # Response Time per Request
    setRcParams()
    perRequest = TimestampsDF.groupby("Index")

    for request in perRequest.groups.keys():
        start = datetime.fromtimestamp(min(perRequest.get_group(request)["Timestamp"]))
        end = datetime.fromtimestamp(max(perRequest.get_group(request)["Timestamp"]))
        tdelta = end - start
        seconds = tdelta.total_seconds()
        plt.bar(perRequest.get_group(request)["Index"], seconds)
    plt.xlabel("Request", fontdict=fontLabel, labelpad=15)
    plt.ylabel("Response Time", fontdict=fontLabel, labelpad=15)
    plt.savefig(f'Plots/{Versuch}_TimeStamps_ResponseTime.png', bbox_inches='tight', dpi=200)
    plt.clf()

    # Response Time per Request
    setRcParams()
    perRequest = TimestampsDF.groupby("Index")
    # Processing Time per Request
    for request in perRequest.groups.keys():
        df = perRequest.get_group(request)
        start = datetime.fromtimestamp(
            df.loc[df["Message"] ==
                   "Received new Request. Starting Calculation"]["Timestamp"].values[0])
        end = datetime.fromtimestamp(
            df[df["Message"] == "Calculation finished. Sending Response"]["Timestamp"].values[0])
        tdelta = end - start
        seconds = tdelta.total_seconds()
        plt.bar(df["Index"], seconds)
    plt.xlabel("Request", fontdict=fontLabel, labelpad=15)
    plt.ylabel("Processing Time", fontdict=fontLabel, labelpad=15)
    plt.savefig(f'Plots/{Versuch}_TimeStamps_ProcessingTime.png',
                bbox_inches='tight', dpi=200)
    plt.clf()


def plotTotalResponseTimeOfEachExperiment():
    setRcParams()
    FilePath_ = "Messungen/"
    for _, dir_, _ in os.walk(FilePath_):
        dir_.sort()
        for experiment in dir_:
            for filename_ in os.listdir(FilePath_ + experiment + "/"):
                root_, ext_ = os.path.splitext(filename_)
                if root_.startswith("Timestamps"):
                    colnames = ["Index", "Timestamp", "RequestID", "ClientID", "Message"]
                    TimestampsDF = pd.read_csv(f"{FilePath_}{experiment}/"
                                               f"{filename_}", sep="|", names=colnames)
                    start = datetime.fromtimestamp(min(TimestampsDF["Timestamp"]))
                    end = datetime.fromtimestamp(max(TimestampsDF["Timestamp"]))
                    tdelta = end - start
                    seconds = tdelta.total_seconds()
                    plt.bar(experiment, seconds)
    plt.ylabel("Time in Seconds", fontdict=fontLabel, labelpad=15)
    plt.savefig(f'Plots/TotalResponseTimes.png', bbox_inches='tight', dpi=200)
    plt.clf()


def plotTotalMeanResponseTimeOfEachExperiment():
    setRcParams()
    FilePath_ = "Messungen/"
    for _, dir_, _ in os.walk(FilePath_):
        dir_.sort()
        for experiment in dir_:
            for filename_ in os.listdir(FilePath_ + experiment + "/"):
                root_, ext_ = os.path.splitext(filename_)
                if root_.startswith("Timestamps"):
                    colnames = ["Index", "Timestamp", "RequestID", "ClientID", "Message"]
                    TimestampsDF = pd.read_csv(f"{FilePath_}{experiment}/"
                                               f"{filename_}", sep="|", names=colnames)
                    perRequest = TimestampsDF.groupby("Index")
                    totalSeconds = 0
                    for request in perRequest.groups.keys():
                        start = datetime.fromtimestamp(
                            min(perRequest.get_group(request)["Timestamp"]))
                        end = datetime.fromtimestamp(
                            max(perRequest.get_group(request)["Timestamp"]))
                        tdelta = end - start
                        totalSeconds += tdelta.total_seconds()
                    mean = totalSeconds / len(perRequest)
                    plt.bar(experiment, mean)
    plt.ylabel("Time in Seconds", fontdict=fontLabel, labelpad=15)
    plt.savefig(f'Plots/MeanResponseTimes.png', bbox_inches='tight', dpi=200)
    plt.clf()


def plotTotalMeanProcessingTimeOfEachExperiment():
    setRcParams()
    FilePath_ = "Messungen/"
    for _, dir_, _ in os.walk(FilePath_):
        dir_.sort()
        for experiment in dir_:
            for filename_ in os.listdir(FilePath_ + experiment + "/"):
                root_, ext_ = os.path.splitext(filename_)
                if root_.startswith("Timestamps"):
                    colnames = ["Index", "Timestamp", "RequestID", "ClientID", "Message"]
                    TimestampsDF = pd.read_csv(f"{FilePath_}{experiment}/"
                                               f"{filename_}", sep="|", names=colnames)
                    perRequest = TimestampsDF.groupby("Index")
                    totalSeconds = 0
                    for request in perRequest.groups.keys():
                        df = perRequest.get_group(request)
                        start = datetime.fromtimestamp(
                            df.loc[df["Message"] == "Received new Request. "
                                                    "Starting Calculation"]["Timestamp"].values[
                                0])
                        end = datetime.fromtimestamp(
                            df[df["Message"] == "Calculation finished. "
                                                "Sending Response"]["Timestamp"].values[0])
                        tdelta = end - start
                        totalSeconds += tdelta.total_seconds()
                    mean = totalSeconds / len(perRequest)
                    plt.bar(experiment, mean)
    plt.ylabel("Time in Seconds", fontdict=fontLabel, labelpad=15)
    plt.savefig(f'Plots/MeanProcessingTimes.png', bbox_inches='tight', dpi=200)
    plt.clf()


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

