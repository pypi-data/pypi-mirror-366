#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core.py: Carga dinámica de input_params y expone los módulos principales del paquete.
"""
import os
import importlib.util

# Carga dinámica de input_params.py (o ruta indicada en INPUT_PARAMS_PATH)
def _load_input_params(path="input_params.py"):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"No encontré el archivo de parámetros en {path}")
    spec = importlib.util.spec_from_file_location("input_params", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PARAMS, module.LAYERS

PARAMS, LAYERS = _load_input_params(
    os.environ.get("INPUT_PARAMS_PATH", "input_params.py")
)


# Librerías estándar y de terceros
import pandas as pd
import os
import json
from pathlib import Path
# Importar módulo SOM dentro del paquete
import numpy as np
from .SOM import SOM,SOM_Batched