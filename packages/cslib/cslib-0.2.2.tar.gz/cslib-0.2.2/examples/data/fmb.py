import click
from pathlib import Path
from cslib.datasets.fusion import FMB
from cslib.utils import *

default_dataset_root_path = "/Volumes/Charles/data/vision/torchvision"

@click.command()
@click.option("--dataset-path", default=Path(default_dataset_root_path), type=Path, required=True)
def main(dataset_path: Path):
    train_dataset = FMB(
        dataset_path, 
        download=True, #(default)
        train=True,
        proxy='http://127.0.0.1:7897',
    )
    print(len(train_dataset)) # 1220

    ir, vis = train_dataset[0]
    ir = path_to_gray(ir)
    vis = path_to_rgb(vis)
    print(ir.shape) # torch.Size([1, 256, 256])
    print(vis.shape) # torch.Size([3, 256, 256])
    glance([ir, vis])

    test_dataset = FMB(
        dataset_path, 
        download=True, #(default)
        train=False,
        proxy='http://127.0.0.1:7897',
    )
    print(len(test_dataset)) # 280

if __name__ == '__main__':
    main()