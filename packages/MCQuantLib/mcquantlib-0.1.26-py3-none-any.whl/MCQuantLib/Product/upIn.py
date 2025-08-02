from MCQuantLib.Product.singleBarrier import SingleBarrier
from MCQuantLib.Instrument.BarrierOption.SingleBarrierOption.UpBarrierOption.upBarrierOption import UpInOption


class UpIn(SingleBarrier):
    _structure = UpInOption
    _out = False
