from .finger_detect import FingerModel
from .page_predict import PageModel
from .perspective import save_per
from .toolmodel import ToolModel
# 这里初始化模型？
from config import model_config
tool_model = ToolModel(model_config)
