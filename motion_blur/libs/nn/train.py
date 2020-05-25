import cv2
import mlflow
import yaml
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from motion_blur.libs.forward_models.kernels.motion import motion_kernel
from motion_blur.libs.forward_models.linops.convolution import Convolution
from motion_blur.libs.utils.nn_utils import load_checkpoint, save_checkpoint, define_checkpoint
from motion_blur.libs.metrics.metrics import weighted_mse_loss, run_validation
from motion_blur.libs.configs.read_config import parse_config
from motion_blur.libs.utils.mlflow_utils import log_loss
from motion_blur.libs.data.dataset import CocoDataset
from motion_blur.libs.data.dataloader import collate_fn_varying_size
from motion_blur.libs.utils.training_utils import print_info
from motion_blur.libs.nn.motion_net import MotionNet
import matplotlib.pyplot as plt
from pathlib import Path


def run_train(config, ckp_path, save_path, net, net_type):
    """
        Main training loop
        :param config 
        :param ckp_path path to checkpoint
        :param save_path path to final model
    """

    # mlflow.log_artifact(path_to_config)

    # Initlialization
    criterion = nn.MSELoss()
    optimizer = optim.Adam(net.parameters(), lr=config.lr)
    running_loss = 0.0
    loss_list = []

    # Resume
    if ckp_path.exists():
        start = load_checkpoint(ckp_path, net, optimizer)
    else:
        start = 0

    # weights
    weights = torch.tensor([1, 1]).type(net_type)

    # Data
    dataset = CocoDataset(config.train_dataset_path, config.L_min, config.L_max, net_type)
    dataloader = DataLoader(
        dataset, batch_size=config.mini_batch_size, shuffle=True, collate_fn=collate_fn_varying_size
    )

    # Training loop
    for epoch in range(start, config.n_epoch):
        for idx, (imgs, gts) in enumerate(dataloader):

            # GPU
            net.zero_grad()
            optimizer.zero_grad()

            # Forward pass
            x = net.forward(imgs)

            # Backward pass
            loss = weighted_mse_loss(x, gts, weights)
            loss.backward()

            optimizer.step()
            running_loss += loss.item()

            # Print loss
            if idx % config.loss_period == (config.loss_period - 1):
                loss_list.append(running_loss)
                print_info(running_loss, epoch, idx, len(dataset), config)
                print("\t\t", x[0].cpu().detach(), gts[0].cpu())

                # Checkpoint
                ckp = define_checkpoint(net, optimizer, epoch)
                save_checkpoint(ckp, ckp_path)

            # Run validation
            if idx % config.validation_period == config.validation_period - 1:
                angle_error, length_error = run_validation(config, net, net_type)
                print(f"\t\tValidation error: angle = {angle_error}, length = {length_error}")

    # log_loss(loss_list, config.loss_period)
    torch.save(net.state_dict(), save_path)


def train(path_to_config: str = "motion_blur/libs/configs/config_motionnet.yml"):
    """
        Entry point of the training. Reads config, set up paths, decide variable type.
    """

    # Configs
    config = parse_config(path_to_config)

    # Path
    Path(config.save_path).mkdir(parents=True, exist_ok=True)
    ckp_path = Path(config.save_path) / "ckp.pth"
    save_path = Path(config.save_path) / "final_model.pth"

    # Net
    net = MotionNet()

    # GPU
    if torch.cuda.is_available():
        net.to(device=torch.device("cuda"))
        net_type = torch.cuda.FloatTensor
    else:
        net_type = torch.FloatTensor

    # Training loop
    run_train(config, ckp_path, save_path, net, net_type)
