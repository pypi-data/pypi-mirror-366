import click
from pathlib import Path
from cslib.datasets.fusion import MSRS
from cslib.utils import glance, path_to_gray, path_to_rgb

default_dataset_root_path = "/Volumes/Charles/data/vision/torchvision"

@click.command()
@click.option("--dataset-path", default=Path(default_dataset_root_path), type=Path, required=True)
def main(dataset_path: Path):
    day_dataset = MSRS(
        dataset_path, 
        download=True, #(default)
        train=False, # <- Test Set (default)
        proxy='http://127.0.0.1:7897',
        time="Day",
    )
    print(len(day_dataset)) # 179

    night_dataset = MSRS(
        dataset_path, 
        download=True, #(default)
        train=False, # <- Test Set (default)
        proxy='http://127.0.0.1:7897',
        time="Night",
    )
    print(len(night_dataset)) # 182

    both_dataset = MSRS(
        dataset_path, 
        download=True, #(default)
        train=False, # <- Test Set (default)
        proxy='http://127.0.0.1:7897',
        time="Both", #(Default)
    )
    print(len(both_dataset)) # 361

    glance([path_to_gray(both_dataset[0][0]), path_to_rgb(both_dataset[0][1])])

if __name__ == '__main__':
    main()