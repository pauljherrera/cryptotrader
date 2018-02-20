
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))




class Portfolio(object):
    """An abstract base class representing a portfolio of
    positions (including both instruments and cash), determined
    on the basis of a set of signals provided by a Strategy."""

    def __init__(self, capital=100.0):
        self.capital = capital


    def place_order(self, type='limit', size=0.001, product='BTC-USD'):
        """

        :param type: type of order
        :param size: size desired for the order
        :param product: BTC-USD
        :return: current balance
        """