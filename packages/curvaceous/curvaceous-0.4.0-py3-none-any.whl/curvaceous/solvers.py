from dataclasses import dataclass
from typing import List, Union, Literal
import mip
from mip import OptimizationStatus
from curvaceous.curve import Curve

Number = Union[int, float]
Domain = Literal["x", "y"]

@dataclass
class Result:
    status: OptimizationStatus
    xs: List[float]
    ys: List[float]

@dataclass
class Constraint:
    lb: Number
    ub: Number
    idx: List[int]
    domain: Domain


def maximize(curves: List[Curve], constraints: List[Constraint]) -> Result:
    (m, ws) = _create_model(curves, constraints)
    status = m.optimize()
    return _to_result(status, curves, ws)


def _create_model(curves: List[Curve], constraints: List[Constraint], print_logs: bool = False):
    m = mip.Model()
    m.solver.set_verbose(1 if print_logs else 0)

    value = mip.LinExpr()
    bs = []
    ws = []

    costs = {i: mip.LinExpr() for i, c in enumerate(constraints) if c.domain == "x"}
    ys = {i: mip.LinExpr() for i, c in enumerate(constraints) if c.domain == "y"}

    for idx, curve in enumerate(curves):
        k = len(curve.xs)
        w = [m.add_var(var_type=mip.CONTINUOUS) for _ in range(k)]
        b = [m.add_var(var_type=mip.BINARY) for _ in range(k - 1)]
        bs.append(b)
        ws.append(w)

        m += mip.xsum(w[i] for i in range(k)) == 1
        for j in range(k):
            m += w[j] >= 0

        m += w[0] <= b[0]
        for j in range(1, k - 1):
            m += w[j] <= b[j - 1] + b[j]
        m += w[k - 1] <= b[k - 2]
        m += mip.xsum(b[j] for j in range(k - 1)) == 1

        for j in range(k):
            value.add_term(w[j] * float(curve.ys[j]))

            for i, c in enumerate(constraints):
                if idx in c.idx:
                    if c.domain == "x":
                        costs[i].add_term(w[j] * float(curve.xs[j]))
                    elif c.domain == "y":
                        ys[i].add_term(w[j] * float(curve.ys[j]))

    for i, c in enumerate(constraints):
        if c.domain == "x":
            expr = costs[i]
        elif c.domain == "y":
            expr = ys[i]
        else:
            continue  

        if c.lb is not None:
            m += expr >= c.lb
        if c.ub is not None:
            m += expr <= c.ub

    m.objective = mip.maximize(value)
    return (m, ws)

def _to_result(status, curves, ws):
    if status == OptimizationStatus.OPTIMAL:
        return Result(status, *_compute_xs_and_ys(curves, ws))
    return Result(status, None, None)


def _compute_xs_and_ys(curves, ws):
    xs = []
    ys = []
    for (i, curve) in enumerate(curves):
        k = len(curve)
        xs.append(sum(ws[i][j].x * float(curve.xs[j]) for j in range(0, k)))
        ys.append(sum(ws[i][j].x * float(curve.ys[j]) for j in range(0, k)))
    return (xs, ys)
