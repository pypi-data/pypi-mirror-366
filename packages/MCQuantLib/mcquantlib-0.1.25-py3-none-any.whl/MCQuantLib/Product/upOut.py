from MCQuantLib.Product.singleBarrier import SingleBarrier
from MCQuantLib.Instrument.BarrierOption.SingleBarrierOption.UpBarrierOption.upBarrierOption import UpOutOption


class UpOut(SingleBarrier):
    _structure = UpOutOption
