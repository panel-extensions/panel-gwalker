"""
Defines custom graphic-walker bokeh model.
"""
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
from bokeh.models import LayoutDOM
from bokeh.models.sources import ColumnarDataSource, ColumnDataSource
from pyviz_comms import JupyterComm

from panel.reactive import SyncableData
from panel.util import isdatetime, lazy_load
from panel.pane.base import ModelPane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class GWalker(LayoutDOM):
    """
    A Bokeh model that wraps around an Vizzu chart and renders it
    inside a Bokeh.
    """

    config = Dict(String, Any)

    source = Instance(ColumnarDataSource, help="""
    Local data source to use when rendering glyphs on the plot.
    """)
