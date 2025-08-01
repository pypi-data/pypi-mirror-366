import os
import tomllib

from beancount_budget.beancount import PerCategory

from .category import CategoryQuota
from .quantize import Quantizer


def load_quotas(
    path: str | os.PathLike, quantize: Quantizer
) -> PerCategory[CategoryQuota]:
    with open(path, mode="rb") as f:
        return {
            category: CategoryQuota.from_dict(quotas, quantize)
            for category, quotas in tomllib.load(f).items()
        }
