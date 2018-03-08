# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import pandas as pd

class Portfolio(object):
    """An abstract base class representing a portfolio of
    positions (including both instruments and cash), determined
    on the basis of a set of signals provided by a Strategy."""

    def __init__(self, capital=100.0, c_capital=0.05):
        self.capital = capital
        self.crypto_capital = c_capital
        self.orders = []

    def place_order(self, time, price=0, size=0.001, product='BTC-USD', side='BUY'):
        """
        :param price: price of the order
        :param size: size desired for the order
        :param product: BTC-USD
        :return: current balance
        """
        amount = price*size
        if side == 'BUY':
            if self.capital >= amount:
                self.capital -= amount
                self.crypto_capital += size
            else:
                print("Capital can't be less than zero, current capital: {}".\
                      format(self.capital))
        else:
            if size <= self.crypto_capital:
                self.capital += amount
                self.crypto_capital -= size
            else:
                print("Size of trade cant be more than crypto capital")
        new_df = dict(zip(['time','price','capital','side','product','size'],
                            [time, price, self.capital, side, product, size]))

        self.orders.append(new_df)

    def show_orders(self):
        self.df = pd.DataFrame(self.orders)
        return self.df

