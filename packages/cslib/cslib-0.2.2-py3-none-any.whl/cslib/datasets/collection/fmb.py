from typing import Callable, Optional, Union
from torchvision.datasets.vision import VisionDataset
import os
from torchvision.datasets.utils import download_and_extract_archive, download_file_from_google_drive
import shutil
from pathlib import Path
from PIL import Image

__all__ = ['FMB']

class FMB(VisionDataset):
    """
    FMB Dataset
    https://github.com/JinyuanLiu-CV/SegMiF

    Args:
        root (str or Path): Root directory of dataset where directory
            ``fmb`` exists or will be saved to if download is set to True.
        train (bool, optional): If True, creates dataset from training set, otherwise
            creates from test set.
        transform (callable, optional): A function/transform that takes in a PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        download (bool, optional): If true, downloads the dataset from the internet and
            puts it in root directory. If dataset is already downloaded, it is not
            downloaded again.
    """
    url_test = 'https://github.com/CharlesShan-hub/FMB_Backup/releases/download/V1.0.0/test.zip'
    md5_test = '916b3482f1d5988046ea74c287bbf518'
    url_train = 'https://github.com/CharlesShan-hub/FMB_Backup/releases/download/V1.0.0/train.zip'
    md5_train = '896c457d6fadb828fced86d7c0e0d66f'
    def __init__(
        self, 
        root: Union[str, Path] = None, 
        transforms: Optional[Callable] = None, 
        transform: Optional[Callable] = None, 
        target_transform: Optional[Callable] = None,
        download: bool = True,
        train: bool = False,
        proxy: Optional[str] = None,
    ) -> None:
        super().__init__(root, transforms, transform, target_transform)
        self.root = root
        self.transforms = transforms
        self.transform = transform
        self.target_transform = target_transform
        self._base_folder = Path(root) / 'fmb-temp'
        self._src_folder = Path(root) / 'fmb'
        if download:
            self.download(proxy)
        set_name = 'train' if train else 'test'
        ir_folder = self._src_folder / set_name / 'Infrared'
        vis_folder = self._src_folder / set_name / 'Visible'
        self.ir_path = list(ir_folder.glob('*.png'))
        self.vis_path = list(vis_folder.glob('*.png'))
        assert len(self.ir_path) == len(self.vis_path)
        
    def __len__(self) -> int:
        return len(self.ir_path)
    
    def __getitem__(self, index: int):
        ir_path = self.ir_path[index]
        vis_path = self.vis_path[index]
        
        if self.transform:
            ir = self.transform(Image.open(ir_path).convert('L'))
            vis = self.transform(Image.open(vis_path).convert('RGB'))
            return ir, vis
        
        return ir_path, vis_path

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

    def download(self, proxy) -> None:
        if self.root is None:
            raise ValueError('root is None')
        if proxy: # 'http://127.0.0.1:7897'
            os.environ['http_proxy'] = proxy
            os.environ['https_proxy'] = proxy
        if self._src_folder.exists():
            return
        self._base_folder.mkdir()
        download_and_extract_archive(
            url=self.url_test,
            download_root=self._base_folder,
            extract_root=self._base_folder,
            filename=f"test.zip",
            md5=self.md5_test,
            remove_finished=True
        )
        download_and_extract_archive(
            url=self.url_train,
            download_root=self._base_folder,
            extract_root=self._base_folder,
            filename=f"train.zip",
            md5=self.md5_train,
            remove_finished=True
        )
        self.move_folder_contents(self._base_folder, self._src_folder)

