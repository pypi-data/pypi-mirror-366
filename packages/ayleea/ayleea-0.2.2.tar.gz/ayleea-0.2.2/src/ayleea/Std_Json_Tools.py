from pathlib import Path
import shutil
import cv2
import numpy as np
from typing import List, Dict, Union, Optional
import random
from collections import defaultdict, Counter
from tqdm import tqdm
from .Std_Json import Std_Json

class Std_Json_Sampler:
    """
    基于分类字段的分层采样器，支持按类别数量或比例进行随机采样
    """
    def __init__(self, data: Union[List[Dict], Std_Json], cate_field: str, is_multi_label: bool = False, splitter: str = '|') -> None:
        """
        初始化采样器，按指定字段对数据进行分类
        
        Args:
            data: 输入数据列表或 Std_Json 对象
            cate_field: 用于分类的字段名
        """
        self.cate_field = cate_field
        self.data_by_category = defaultdict(list)
        self.is_multi_label = is_multi_label
        self.splitter = splitter
        
        # 支持 Std_Json 对象作为输入
        # if isinstance(data, Std_Json):
        #     data = data.std_data
        
        # 按分类字段分组数据
        for item in data:
            if cate_field not in item:
                raise ValueError(f"分类字段 '{cate_field}' 不存在于数据项中")
            category = item[cate_field]
            if self.is_multi_label:
                if isinstance(category, str) and splitter:
                    categories = [c.strip() for c in category.split(splitter)]
                elif isinstance(category, list):
                    categories = category
                else:
                    raise ValueError(f"多标签情况下，分类字段 '{cate_field}' 的值必须是带分隔符的字符串或列表")
                for c in categories:
                    self.data_by_category[c].append(item)
            else:
                self.data_by_category[category].append(item)
        
        self.categories = Counter({k:len(self.data_by_category[k]) for k in self.data_by_category.keys()})
    
    def sample(self, 
               n: Optional[Union[int, Dict]] = None, 
               total: Optional[int] = None, 
               ratios: Optional[Dict] = None, 
               seed: int = 42,
               insufficient_strategy: str = 'error',
               add_sample_label:bool = False,
               fun_type:str='sample'
               ) -> Std_Json:
        """
        按类别进行随机采样，支持多种采样方式
        
        Args:
            n: 各类别采样数量的字典 {category: count}，或为 None
            total: 总采样数量，与 ratios 配合使用，或为 None
            ratios: 各类别采样比例的字典 {category: ratio}，与 total 配合使用，或为 None
            seed: 随机种子，用于复现采样结果
            insufficient_strategy: 当类别样本不足时的处理策略，'error'（默认）或 'all','skip','copy'
            fun_type: 采样方式是sample（不允许重复），还是choice（允许重复抽样）
            
        Returns:
            采样结果，为 Std_Json 类型对象
            
        Raises:
            ValueError: 当参数不合法时抛出
        """
        # 设置随机种子确保复现性
        random.seed(seed)
        
        sampled_data = []
        sampled_cate_counts = Counter()
        # 处理不同的采样参数组合
        if n is not None:
            # 处理单一数值 n 表示所有类别采用相同规则的情况
            if isinstance(n, (int, float)):
                n = {category: n for category in self.categories}
            
            # 按指定的各类别数量/比例采样
            if not isinstance(n, dict):
                raise ValueError("参数 n 必须是一个字典 {category: count} 或单个数值")
            
            for category, count in tqdm(n.items(),desc="Sampling..."):
                if category not in self.data_by_category:
                    raise ValueError(f"类别 '{category}' 不存在")
                
                # 获取该类别的总样本数
                total_in_category = len(self.data_by_category[category])
                
                # 计算实际采样数量
                total_actual_count = self._calculate_sample_count(count, total_in_category)
                if fun_type == "sample":
                    full_sample_num = 0
                    # 检查样本是否充足并处理
                    if total_actual_count > total_in_category:
                        if insufficient_strategy == 'error':
                            raise ValueError(f"类别 '{category}' 采样数量 {actual_count} 超过数据量 {total_in_category}")
                        elif insufficient_strategy == 'all':
                            print(f"警告: 类别 '{category}' 采样数量不足，将使用全部 {total_in_category} 个样本")
                            actual_count = total_in_category
                        elif insufficient_strategy == 'copy':
                            print(f"警告: 类别 '{category}' 采样数量不足，将进行重复采样补足 {total_actual_count} 个样本")
                            full_sample_num = total_actual_count // total_in_category
                            actual_count = total_actual_count % total_in_category
                        elif insufficient_strategy == 'skip':
                            print(f"警告: 类别 '{category}' 采样数量不足，将忽略该类别")
                            continue
                        else:
                            raise ValueError(f"不支持的策略: {insufficient_strategy}")
                
                    # 从该类别中随机采样
                    if full_sample_num > 0:
                        samples = []
                        for _ in range(full_sample_num):
                            samples.extend(random.sample(self.data_by_category[category], total_in_category))
                        samples.extend(random.sample(self.data_by_category[category], actual_count))
                    else:
                        samples = random.sample(self.data_by_category[category], total_actual_count)
                    
                elif fun_type == "choice":
                    samples = random.choices(self.data_by_category[category],k=total_actual_count)
                else:
                    raise  ValueError(f"不支持的采样方式: {fun_type}，‘fun_type’ 仅支持‘sample’ ‘choice’")
            
                if add_sample_label:
                    for sample in samples:
                        sample['sample_label'] = category
                        
                print(f"类别 '{category}' 采样数量: {total_actual_count}")
                sampled_data.extend(samples)
                sampled_cate_counts[category] = total_actual_count
                
        elif total is not None and ratios is not None:
            # 按总量和各类占比采样
            if total <= 0:
                raise ValueError("总采样数量 total 必须大于 0")
            if not isinstance(ratios, dict):
                raise ValueError("参数 ratios 必须是一个字典 {category: ratio}")
            
            # 计算各类别的采样数量
            total_ratio = sum(ratios.values())
            if list(ratios.values())[0]<=1:
                assert total_ratio == 1,"比例之和必须等于 1"
            else:
                assert total_ratio == total, f"数量之和必须等于 ‘total’ {total}"
                
            category_counts = {}
            for category, ratio in ratios.items():
                if category not in self.data_by_category:
                    raise ValueError(f"类别 '{category}' 不存在")
                # 计算该类别的采样数量，向上取整
                count = max(1, int(ratio / total_ratio * total))
                category_counts[category] = count
            
            # 调用按类别数量采样的逻辑
            return self.sample(
                n=category_counts, 
                seed=seed,
                insufficient_strategy=insufficient_strategy,
                add_sample_label=add_sample_label,
                fun_type=fun_type
            )
            
        else:
            raise ValueError("必须提供参数 n，或同时提供 total 和 ratios")
            
        # 将采样结果转换为 Std_Json 对象
        return Std_Json(sampled_data), sampled_cate_counts
    
    def _calculate_sample_count(self, count: Union[int, float], total: int) -> int:
        """
        根据输入的 count 参数计算实际采样数量
        
        Args:
            count: 采样数量（整数或小数）
            total: 该类别的总样本数
            
        Returns:
            实际采样数量
        """
        if isinstance(count, int):
            if count == -1:
                # -1 表示采样全部样本
                return total
            elif count >= 1:
                # 整数直接表示数量
                return count
            elif count == 0:
                return 0
            else:
                raise ValueError(f"无效的采样数量: {count}。整数必须为 -1 或 >= 1")
        elif isinstance(count, float):
            if 0 < count < 1:
                # 小数表示比例
                return max(1, int(total * count))
            else:
                raise ValueError(f"无效的采样比例: {count}。小数必须在 (0, 1) 范围内")
        else:
            raise ValueError(f"无效的采样值类型: {type(count)}")


def set_image_root_dir_for_Std_Json(
    std_json: Std_Json, image_root_dir: str | Path, image_key="image", is_remove=False
):
    image_root_dir = (
        Path(image_root_dir) if isinstance(image_root_dir, str) else image_root_dir
    )
    for item in std_json:
        if is_remove:
            item[image_key] = str(Path(item[image_key]).relative_to(image_root_dir))
        else:
            item[image_key] = str(image_root_dir / item[image_key])
    return std_json


def Std_Json_image_to_dir(std_json: Std_Json, save_dir, image_key="image"):
    for item in std_json:
        image = Path(item[image_key])
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        if not image.exists():
            print(image, "not exists!")
            continue
        shutil.copy2(image, save_dir)


# plot functions for Std_Json
def plot_polygon(
    image: np.ndarray,
    polygon: list | np.ndarray,
    color: tuple = (0, 255, 0),
    thickness: int = 2,
    render_index_points=True,
):
    polygon = np.array(polygon)
    assert polygon.ndim == 2, "polygon must be 2D array"
    assert polygon.shape[0] > 2, "polygon must have at least 3 points"
    assert polygon.shape[1] == 2, "polygon must have 2 columns"

    polygon = polygon.reshape((-1, 1, 2)).astype(np.int32)
    cv2.polylines(image, [polygon], True, color, thickness)
    if render_index_points:
        for i in range(len(polygon)):
            u, v = polygon[i][0][0], polygon[i][0][1]
            cv2.putText(
                image,
                f"{i}",
                (u, v),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (225, 0, 0),
                2,
            )
    return image


def plot_bbox(
    image: np.ndarray,
    bbox: list | np.ndarray,
    color: tuple = (0, 255, 0),
    thickness: int = 2,
    render_index_points=True,
):
    bbox = np.array(bbox)
    assert bbox.ndim == 1, "bbox must be 1D array"
    assert bbox.shape[0] == 4, "bbox must have 4 elements (x1,y1,x2,y2)"
    x1, y1, x2, y2 = bbox
    cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
    if render_index_points:
        cv2.putText(
            image,
            "0",
            (x1, y1),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (225, 0, 0),
            2,
        )
        cv2.putText(
            image,
            "1",
            (x2, y2),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (225, 0, 0),
            2,
        )
    return image


def plot_point(
    image: np.ndarray,
    point: tuple | list | np.ndarray,
    color: tuple = (0, 0, 255),
    thickness: int = 2,
):
    point = np.array(point)
    assert point.ndim == 1, "point must be 1D array"
    assert len(point) == 2, "point must have 2 elements (x,y)"
    x, y = point
    cv2.circle(image, (x, y), 5, color, thickness)
    return image


def plot_text(
    image: np.ndarray,
    text: str,
    point: tuple | list | np.ndarray,
    color: tuple = (255, 0, 0),
    thickness: int = 2,
):
    point = np.array(point)
    assert point.ndim == 1, "point must be 1D array"
    assert len(point) == 2, "point must have 2 elements (x,y)"
    x, y = point
    cv2.putText(
        image,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        thickness,
    )
    return image


def plot_item(
    info_item: dict,
    image: str | Path,
    out_image: str | Path,
    plot_geo_names: list,
    coor_is_norm=False,
    **kwargs,
):
    if not Path(image).exists():
        print(image, "not exists!")
        return
    image = cv2.imread(image)
    h, w = image.shape[:2]
    for info_name in plot_geo_names:
        if info_name == "polygon":
            polygon = np.array(info_item[info_name])
            if coor_is_norm:
                polygon *= [w, h]
            image = plot_polygon(image, polygon, **kwargs)
        elif info_name == "bbox":
            bbox = np.array(info_item[info_name])
            if coor_is_norm:
                bbox *= [w, h, w, h]
            image = plot_bbox(image, bbox, **kwargs)
        elif info_name == "point":
            point = np.array(info_item[info_name])
            if coor_is_norm:
                point *= [w, h]
            image = plot_point(image, point, **kwargs)
        elif info_name == "text":
            image = plot_text(image, info_item[info_name], **kwargs)
        else:
            raise ValueError(f"info_name {info_name} not supported!")

    out_image = Path(out_image)
    out_image.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_image), image)


def plot_geo_for_Std_Json(
    std_json: Std_Json,
    out_dir: str | Path,
    plot_item_func=plot_item,
    image_key="image",
    plot_geo_name=["polygon", "bbox", "point", "text"],
    coor_is_norm=False,
    **kwargs
):
    """
    参数:
        std_json (Std_Json): 包含注释和图像路径的 Std_Json 对象。
        out_dir (str | Path): 保存输出图像的目录。
        plot_item_func (function, optional): 用于在图像上绘制几何的函数。默认为 plot_item。
        image_key (str, optional): Std_Json 项目中包含图像路径的键。默认为 "image"。
        plot_info_name (list, optional): 要绘制的几何类型列表。默认为 ["polygon", "bbox", "point", "text"]。
        coor_is_norm (bool, optional): 几何中的坐标是否归一化。默认为 False。
        **kwargs: 传递给 plot_item_func 的其他关键字参数。
    """
    for item in std_json:
        image_path = item[image_key]
        out_image = Path(out_dir) / Path(image_path).name
        plot_item_func(item, image_path, out_image, plot_geo_name,coor_is_norm,**kwargs)
