from financial_instruments.financial_instrument import FinancialInstrument

class Stock(FinancialInstrument):
    def __init__(self, dividend_yield):

        super().__init__()
        #self.dividend_yield = dividend_yield