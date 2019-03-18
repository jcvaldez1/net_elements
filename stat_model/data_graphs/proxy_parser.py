import packet_analyzer

class prox:
    
    def __init__(self):
        analyzer = packet_analyzer.packet_analyzer()
        analyzer.initEmulation()

        # declare the metrics
        self.responseDistrib = analyzer.TCPresponseDistribution
        self.requestDistrib = analyzer.TCPrequestDistribution
        self.delayDistrib = analyzer.TCPdelayDistribution
        self.connectionLength = analyzer.connection_lengths
        self.HostPairFrequency = analyzer.TCPDestinationDistribution

    def gen_graph(self):
        # pgfplot the shits here keku
        print(str(self.responseDistrib))
        print(str(self.requestDistrib))
        print(str(self.delayDistrib))
        print(str(self.connectionLength))
        print(str(self.HostPairFrequency))

    def __str__(self):
        return str(self.responseDistrib) + '$' + str(self.requestDistrib) + '$' + str(self.delayDistrib) + '$' + str(self.connectionLength) + '$' + str(self.HostPairFrequency)
        

if __name__ == "__main__":
    new_clone = prox()
    print(new_clone)


