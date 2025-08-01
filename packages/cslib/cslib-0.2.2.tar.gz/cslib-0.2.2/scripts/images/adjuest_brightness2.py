import os
from PIL import Image
import click
import numpy as np

@click.command()
@click.option("--src", default="/Users/kimshan/Public/project/CPFusion/glance_outputs/fusion_detail",required=True, type=click.Path(exists=True, file_okay=False),
              help="包含图片的源文件夹路径")
@click.option("--dst", default="/Users/kimshan/Public/project/CPFusion/glance_outputs/fusion_detail/adjust", type=click.Path(file_okay=False),
              help="输出文件夹路径，默认为'./adjusted_images'")
@click.option("--gamma", default=0.65, type=float,
              help="亮度调整系数(0.0-1.0)")
def adjust_brightness(src, dst, gamma):
    """
    使用 Gamma 校正调整文件夹中所有图片的亮度，并保存为brightness_{gamma}_{原文件名}
    """
    # 确保输出目录存在
    os.makedirs(dst, exist_ok=True)
    
    # 支持的图片格式
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    
    # 遍历源文件夹
    for filename in os.listdir(src):
        if filename.lower().endswith(valid_extensions):
            try:
                # 构建完整路径
                src_path = os.path.join(src, filename)
                dst_path = os.path.join(dst, f"brightness_{gamma:.1f}_{filename}")
                
                # 打开图片并调整亮度
                with Image.open(src_path) as img:
                    # 转换为RGB/RGBA数组
                    arr = np.array(img)
                    
                    # 使用Gamma校正调整亮度
                    arr = arr / 255.0  # 归一化到 [0, 1]
                    adjusted = np.power(arr, gamma)
                    adjusted = (adjusted * 255).astype(np.uint8)  # 反归一化
                    
                    # 转换回图片对象
                    result = Image.fromarray(adjusted)
                    
                    # 保存处理后的图片
                    result.save(dst_path)
                    print(f"处理完成: {filename} -> brightness_{gamma:.1f}_{filename}")
                    
            except Exception as e:
                print(f"处理图片 {filename} 时出错: {e}")

if __name__ == "__main__":
    adjust_brightness()