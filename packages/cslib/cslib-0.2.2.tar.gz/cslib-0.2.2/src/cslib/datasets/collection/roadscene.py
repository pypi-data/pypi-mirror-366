from typing import Callable, Optional, Union
from torchvision.datasets.vision import VisionDataset
import os
from torchvision.datasets.utils import download_and_extract_archive
import shutil
from pathlib import Path
from PIL import Image

__all__ = ['RoadScene']

class RoadScene(VisionDataset):
    """
    RoadScene dataset.
    
    This datset has 221 aligned Vis and IR image pairs containing rich scenes 
    such as roads, vehicles, pedestrians and so on. These images are highly 
    representative scenes from the FLIR video. We preprocess the background 
    thermal noise in the original IR images, accurately align the Vis and IR 
    image pairs, and cut out the exact registration regions to form this dataset.

    https://github.com/hanna-xu/RoadScene

    Args:
        root (str): Root directory of dataset.
        transform (callable, optional): A function/transform that takes in a PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``.
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        download (bool, optional): If true, downloads the dataset from the internet and
            puts it in root directory. If dataset is already downloaded, it is not
            downloaded again.
        proxy (str, optional): Proxy server address.
    """
    url = 'https://github.com/CharlesShan-hub/RoadScene-Backup/releases/download/v1.0.0/RoadScene-master.zip'
    md5 = '02cd268c3b26d68b308e06df09251df5'
    def __init__(
        self,
        root: str,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
        download: bool = True,
        proxy: Optional[str] = None,
    ) -> None:
        super().__init__(root, transform=transform, target_transform=target_transform)
        self.root = root
        self._base_folder = Path(root) / 'RoadScene-temp'
        self._src_folder = Path(root) / 'roadscene'
        self.transform = transform
        self.target_transform = target_transform
        if download:
            self.download(proxy)
        ir_folder = self._src_folder / 'crop_LR_visible'
        vis_folder = self._src_folder / 'cropinfrared'
        self.ir_path = sorted([f for f in ir_folder.iterdir() if f.suffix == '.jpg'], key=lambda x: int(x.stem[-5:]))
        self.vis_path = sorted([f for f in vis_folder.iterdir() if f.suffix == '.jpg'], key=lambda x: int(x.stem[-5:]))
    
    def __len__(self) -> int:
        return len(self.ir_path)

    @staticmethod
    def move_folder_contents(src: Path, dst: Path):
        """Move all contents from source folder to destination folder"""
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.glob('*'):
            dest_path = dst / item.name
            if dest_path.exists():
                if dest_path.is_dir():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()
            shutil.move(str(item), str(dest_path))
        if not any(src.iterdir()):
            src.rmdir()
    
    def __getitem__(self, index: int):
        ir_path = self.ir_path[index]
        vis_path = self.vis_path[index]
        
        if self.transform:
            ir = self.transform(Image.open(ir_path).convert('L'))
            vis = self.transform(Image.open(vis_path).convert('RGB'))
            return ir, vis
        
        return ir_path, vis_path

    def download(self, proxy):
        if proxy: # 'http://127.0.0.1:7897'
            os.environ['http_proxy'] = proxy
            os.environ['https_proxy'] = proxy
        if self._src_folder.exists():
            return
        self._base_folder.mkdir()
        download_and_extract_archive(
            url=self.url,
            download_root=self._base_folder,
            extract_root=self._base_folder,
            filename=f"RoadScene-master.zip",
            md5=self.md5,
            remove_finished=True
        )
        self.move_folder_contents(self._base_folder / 'RoadScene-master', self._src_folder)
        if not any(self._base_folder.iterdir()):
            self._base_folder.rmdir()
