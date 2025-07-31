"""统计当前文件夹下所有实例的数量"""

from pathlib import Path
from tqdm import tqdm
import xml.etree.ElementTree as ET
import pandas as pd
import json

from MiniToolkit.tools.path import find_files_in_dir
from MiniToolkit.tools.image import just_load_image, just_save_image


def save_table(count: dict):
    """将统计结果保存为excel表格"""
    data = pd.DataFrame.from_dict(count, orient="index", columns=["name"])
    data.to_excel("perform_table.xlsx", index=True)


def split_xml_data(xml_path: Path) -> None:
    # 获取xml文件中的所有缺陷信息
    root = ET.parse(str(xml_path)).getroot()
    # 遍历xml文件中的object标签
    for obj in root.findall("object"):
        value = obj.find("name").text.split("-")
        key = f"{value[1]}-{value[2]}-{value[3]}-{value[4]}"
        if "正常" in key:
            continue
        if key in GT_COUNT:
            GT_COUNT[key] += 1
        else:
            GT_COUNT[key] = 1


def read_json(json_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    shapes = data["shapes"]
    for shape in shapes:
        label = shape["label"]
        # if "正常" in label:
        #     continue
        if label in GT_COUNT:
            GT_COUNT[label] += 1
        else:
            GT_COUNT[label] = 1


if __name__ == "__main__":
    source_dir = Path("/home/fxy/data/industai/无人机模型/无人机运营采集数据测试/202503/接地装置label/json/")
    GT_COUNT = {}  # 统计gt指标数量的全局变量
    file_list = find_files_in_dir(source_dir, [".json"], recurrence=True)
    for file_path in tqdm.tqdm(file_list, dynamic_ncols=True):
        read_json(file_path)
    save_table(GT_COUNT)
