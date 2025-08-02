from MCQuantLib.Product.singleBarrier import SingleBarrier
from MCQuantLib.Instrument.BarrierOption.SingleBarrierOption.DownBarrierOption.downBarrierOption import DownOutOption


class DownOut(SingleBarrier):
    _structure = DownOutOption
