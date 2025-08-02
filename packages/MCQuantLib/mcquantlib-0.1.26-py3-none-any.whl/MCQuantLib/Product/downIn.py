from MCQuantLib.Product.singleBarrier import SingleBarrier
from MCQuantLib.Instrument.BarrierOption.SingleBarrierOption.DownBarrierOption.downBarrierOption import DownInOption


class DownIn(SingleBarrier):
    _structure = DownInOption
    _out = False
