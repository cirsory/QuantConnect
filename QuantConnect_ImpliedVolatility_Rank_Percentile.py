# Calculating the Implied Volatility Rank and Implied Volatility Percentile
# of tickers that have an associated Volatility Index for QuantConnect


# This is a close approximation of actual IVRank and IVPercentile
# However, due to varying calculation methods between the Underlying Volatility Index and Ticker Option-based methods,
#   they won't be a 1:1 match to other data sources such as barchart.


# https://www.quantconnect.com/datasets/cboe-vix-daily
# Underlying to Vol Index Pairs are
# (SPY,VIX),(QQQ,VXN),(RUT,RVX),(USO,OVX),(GLD,GVZ),(EEM,VXEEM) and others listed in the link above.
#
# Other underlying volatility index pairs I haven't found access to in QC
# (DJIA,VXD),(AAPL,VXAPL),(AMZN,VXAZN),(GOOGL,VXGO),(GS,VXGS)

from AlgorithmImports import *
from System import TimeSpan
from QuantConnect.Indicators import Maximum, Minimum
from QuantConnect.DataSource import *

class MyAlgorithm(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2022, 3, 14)  # Set Start Date
        #self.SetEndDate(2020, 12, 28)  # Set End Date
        self.SetCash(100000)  # Set Strategy Cash

        # Mapping of ETFs to their respective IV symbols
        self.Underlying = self.AddEquity('SPY',Resolution.Minute)
        self.IvIndex = self.AddData(CBOE,'VIX')
        self.IVlookback = 365


        # Schedule the function at the market open
        self.Schedule.On(self.DateRules.EveryDay(self.Underlying.Symbol), 
                        self.TimeRules.AfterMarketOpen(self.Underlying.Symbol, 0), 
                        self.CalculateIV)

        # Set up a chart
        ivChart = Chart('Implied Volatility')
        ivChart.AddSeries(Series('IVR', SeriesType.Line, 0))
        ivChart.AddSeries(Series('IVP', SeriesType.Line, 0))
        self.AddChart(ivChart)

        self.SetWarmUp(self.IVlookback, Resolution.Daily)

    def CalculateIV(self):
        # This method will be called after the warm-up period is over
        # Placeholder for IV calculation logic
        if self.IsWarmingUp: return

        # Get history of the volatility index
        self.history = self.History([self.IvIndex.Symbol], self.IVlookback, Resolution.Daily)

        #Set up initial values for calculations
        current_iv = float(self.IvIndex.Price)  
        highest_price = 0
        lowest_price = 100
        days_below_current_iv = 0 
        IVR = 0
        IVP = 0

        for index, row in self.history.iterrows():
            highest_price = max(highest_price, row['high'])
            lowest_price = min(lowest_price, row['low'])
            if row['close'] < current_iv:
                days_below_current_iv += 1

        # Implied Volatility Rank Calculation
        IVR = round(((current_iv - lowest_price) / (highest_price - lowest_price)) * 100,0)

        #Implied Volatility Percentage Calculation
        IVP = round((days_below_current_iv / self.IVlookback) * 100, 0)
        
        # Plot the IVR dynamically
        self.Plot('Implied Volatility', 'IV Rank', IVR)
        self.Plot('Implied Volatility', 'IV Percentil', IVP)
        self.Debug(f'Price: {current_iv} Current IV Rank: {IVR} Current IV Percentile: {IVP}')

    def OnData(self, slice):
        pass
