from __future__ import annotations

import datetime as dt
import sys

from typing import (
    TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Optional,
)

import numpy as np
import pandas as pd
import param

from bokeh.core.properties import (
    Any, Dict, Instance, Int, List, String,
)
from pyviz_comms import JupyterComm

from panel.reactive import SyncableData
from panel.util import isdatetime, lazy_load
from panel.pane.base import ModelPane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


def infer_prop(s: np.ndarray, i=None):
    """

    Arguments
    ---------
    s (pd.Series): 
      the column
    """
    kind = s.dtype.kind
    # print(f'{s.name}: type={s.dtype}, kind={s.dtype.kind}')
    v_cnt = len(s.value_counts())
    semanticType = 'quantitative' if \
        (kind in 'fcmiu' and v_cnt > 16) \
            else 'temporal' if kind in 'M' \
                else 'nominal' if kind in 'bOSUV' or v_cnt <= 2 \
                    else 'ordinal'
    # 'quantitative' | 'nominal' | 'ordinal' | 'temporal';
    analyticType = 'measure' if \
        kind in 'fcm' or (kind in 'iu' and len(s.value_counts()) > 16) \
            else 'dimension'
    return {
        'fid': s.name,
        'name': s.name,
        'semanticType': semanticType,
        'analyticType': analyticType
    }

def raw_fields(data: pd.DataFrame | Dict[str, np.ndarray]):
    if isinstance(data, dict):
        return [
            infer_prop(pd.Series(array, name=col)) for col, array in data.items()
        ]
    else:
        return [
            infer_prop(df[col], i)
            for i, col in enumerate(data.columns)
        ]


class GraphicWalker(ModelPane, SyncableData):
    """
    The `GraphicWalker` pane provides an interactive visualization component for
    large, real-time datasets built on the Vizzu project.

    Reference: https://panel.holoviz.org/reference/panes/pygwalker.html

    :Example:

    >>> GraphicWalker(df)
    """

    _data_params: ClassVar[List[str]] = ['object']

    _bokeh_model = GWalker

    @classmethod
    def applies(cls, object):
        if isinstance(object, dict) and all(isinstance(v, (list, np.ndarray)) for v in object.values()):
            return 0 if object else None
        elif 'pandas' in sys.modules:
            import pandas as pd
            if isinstance(object, pd.DataFrame):
                return 0
        return False

    def _init_params(self):
        props = super()._init_params()
        props['source'] = ColumnDataSource(data=self._data)
        props['config'] = {'rawFields': raw_fields(self._data)}
        return props

    def _get_data(self):
        if self.object is None:
            return {}, {}
        if isinstance(self.object, dict):
            data = self.object
        else:
            data = {col: self.object[col].values for col in self.object.columns}
        return data, {str(k): v for k, v in data.items()}
