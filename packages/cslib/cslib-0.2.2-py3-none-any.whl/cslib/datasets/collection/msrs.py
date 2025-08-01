from typing import Callable, Optional, Union
from torchvision.datasets.vision import VisionDataset
import os
from torchvision.datasets.utils import download_and_extract_archive
import shutil
from pathlib import Path
from PIL import Image


__all__ = ['MSRS']

class MSRS(VisionDataset):
    """
    MSRS dataset.
    https://github.com/Linfeng-Tang/MSRS

    Args:
        root (str or Path): Root directory of the dataset.
        transform (callable, optional): A function/transform that takes in a PIL image and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the target and transforms it.
        download (bool, optional): If true, downloads the dataset from the internet and puts it in root directory. If dataset is already downloaded, it is not downloaded again.
        train (bool, optional): If true, uses the training set. If false, uses the test set.
        proxy (str, optional): Proxy server for downloading the dataset.
        segmentation (bool, optional): If true, uses the segmentation labels.
        detection (bool, optional): If true, uses the detection labels.
    """
    
    url = 'https://github.com/CharlesShan-hub/MSRS-Backup/releases/download/v1.0/MSRS-main.zip'
    md5 = 'dfc32330f411437fbefae701e1bb9ba0'
    def __init__(
            self, 
            root: Union[str, Path], 
            transform: Optional[Callable] = None, 
            target_transform: Optional[Callable] = None,
            download: bool = True,
            train: bool = False,
            time: str = ["Day", "Night", "Both"][2],
            proxy: Optional[str] = None,
            segmentation: bool = False,
            detection: bool = False,
        ) -> None:
        super().__init__(root, transform=transform, target_transform=target_transform)
        self.root = root
        self._base_folder = Path(self.root) / "msrs-temp"
        self._src_folder = Path(self.root) / "msrs"
        self.transform = transform
        self.target_transform = target_transform
        if download:
            self.download(proxy)
        self.detection = detection
        self.segmentation = segmentation
        self.ir_path = []
        self.vi_path = []
        set_name = 'train' if train else 'test'
        ir_folder = self._src_folder / set_name / 'ir'
        vis_folder = self._src_folder / set_name / 'vi'
        label_path = self._src_folder / set_name / 'Segmentation_labels'
        self.ir_path = sorted([f for f in ir_folder.iterdir() if f.suffix == '.png'], key=lambda x: int(x.stem[:-1]))
        self.vis_path = sorted([f for f in vis_folder.iterdir() if f.suffix == '.png'], key=lambda x: int(x.stem[:-1]))
        self.label_path = sorted([f for f in label_path.iterdir() if f.suffix == '.png'], key=lambda x: int(x.stem[:-1]))
        if time == "Day":
            self.ir_path = [f for f in self.ir_path if f.stem[-1] == 'D']
            self.vis_path = [f for f in self.vis_path if f.stem[-1] == 'D']
            self.label_path = [f for f in self.label_path if f.stem[-1] == 'D']
        elif time == "Night":
            self.ir_path = [f for f in self.ir_path if f.stem[-1] == 'N']
            self.vis_path = [f for f in self.vis_path if f.stem[-1] == 'N']
            self.label_path = [f for f in self.label_path if f.stem[-1] == 'N']
        assert len(self.ir_path) == len(self.vis_path) == len(self.label_path)
    
    def __len__(self) -> int:
        return len(self.ir_path)

    def __getitem__(self, index: int):
        ir = self.ir_path[index]
        vis = self.vis_path[index]
        
        if self.transform:
            ir = self.transform(Image.open(ir).convert('L'))
            vis = self.transform(Image.open(vis).convert('RGB'))
        if self.segmentation:
            label_path = self.label_path[index]
            label = Image.open(label_path).convert('L')
            if self.target_transform:
                label = self.target_transform(label)
            return ir, vis, label
        else:
            return ir, vis

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

    def download(self, proxy):
        # raise ValueError("MSRS dataset is not supported for download.")
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
            filename=f"MSRS-master.zip",
            md5=self.md5,
            remove_finished=True
        )
        self.move_folder_contents(self._base_folder / 'MSRS-main', self._src_folder)
        if not any(self._base_folder.iterdir()):
            self._base_folder.rmdir()
    