import zipimport
import os

zipimport.zipimporter(os.path.dirname(__file__) + "/lanus.pyz").load_module("load")