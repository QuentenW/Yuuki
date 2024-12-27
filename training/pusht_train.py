from typing import Tuple, Sequence, Dict, Union, Optional, Callable

import numpy as np
from tqdm.auto import tqdm

import torch
import torch.nn as nn
import torchvision

from diffusers.schedulers.scheduling_ddpm import DDPMScheduler
from diffusers.training_utils import EMAModel
from diffusers.optimization import get_scheduler

from models import pusht_networks
from datasets import pusht_dataset

#### Dataset Parameters
dataset_path = "/home/tom/Projects/RobotArm/training/data/pusht.zarr.zip"
pred_horizon = 16
obs_horizon = 2
action_horizon = 8
raw_img_width = 512
raw_img_height = 512

#### Agent Paramters
agent_state_dim = 4
action_dim = 4
net_img_input_width = 96
net_img_input_height = 96

#### Image Network Paramters
vision_feature_dim = 512
obs_dim = vision_feature_dim + agent_state_dim

#### Diffusion Parameters
diffusion_steps = 100
beta_schedule = 'squaredcos_cap_v2'
clip_sample = True
prediction_type = 'epsilon'

#### Training Parameters
num_epochs = 100
ema_power = 0.75
lr = 1e-4
weight_decay = 1e-6
warmup_steps = 500
lr_scheduler_name = 'cosine'

#### Testing Parameters
max_steps = 200

device = torch.device('cuda')

def get_resnet(name:str, weights=None, **kwargs) -> nn.Module:
    """
    name: resnet18, resnet34, resnet50
    weights: "IMAGENET1K_V1", None
    """
    # Use standard ResNet implementation from torchvision
    func = getattr(torchvision.models, name)
    resnet = func(weights=weights, **kwargs)

    # remove the final fully connected layer
    # for resnet18, the output dim should be 512
    resnet.fc = torch.nn.Identity()
    return resnet

def setup_data() -> Tuple[torch.utils.data.DataLoader, Dict]:
    ''''''

    dataset = pusht_dataset.PushTImageDataset(
        dataset_path,
        pred_horizon,
        obs_horizon,
        action_horizon
    )
    stats = dataset.stats

    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size = 64,
        num_workers = 4,
        shuffle = True,
        pin_memory = True,
        persistent_workers = True
    )

    return dataloader, stats

def setup_nets() -> nn.ModuleDict:
    ''''''

    vision_encoder = get_resnet('resnet18')
    # replace all BatchNorm with GroupNorm to work with EMA
    # performance will tank if you forget to do this!
    vision_encoder = pusht_networks.replace_bn_with_gn(vision_encoder)

    noise_pred_net = pusht_networks.ConditionalUnet1D(
        input_dim=action_dim,
        global_cond_dim=obs_dim*obs_horizon
    )

    nets = nn.ModuleDict({
        'vision_encoder' : vision_encoder,
        'noise_pred_net' : noise_pred_net
    })

    _ = nets.to(device)

    return nets

def train(dataloader:torch.utils.data.DataLoader, nets:nn.ModuleDict):
    ''''''

    noise_scheduler = DDPMScheduler(
        num_train_timesteps = diffusion_steps,
        beta_schedule = beta_schedule,
        clip_sample = clip_sample,
        prediction_type = prediction_type
    )

    ema = EMAModel(
        parameters=nets.parameters(),
        power=ema_power
    )

    optimizer = torch.optim.AdamW(
        params=nets.parameters(),
        lr=lr,
        weight_decay=weight_decay
    )

    lr_scheduler = get_scheduler(
        name=lr_scheduler_name,
        optimizer=optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=len(dataloader) * num_epochs
    )

    with tqdm(range(num_epochs), desc='Epoch') as tglobal:
        # epoch loop
        for epoch_idx in tglobal:
            epoch_loss = list()
            # batch loop
            with tqdm(dataloader, desc='Batch', leave=False) as tepoch:
                for nbatch in tepoch:
                    # data normalized in dataset
                    # device transfer
                    nimage = nbatch['image'][:,:obs_horizon].to(device)
                    nagent_pos = nbatch['agent_pos'][:,:obs_horizon].to(device)
                    naction = nbatch['action'].to(device)
                    B = nagent_pos.shape[0]

                    # encoder vision features
                    image_features = nets['vision_encoder'](nimage.flatten(end_dim=1))
                    image_features = image_features.reshape(*nimage.shape[:2],-1)
                    # (B,obs_horizon,D)

                    # concatenate vision feature and low-dim obs
                    obs_features = torch.cat([image_features, nagent_pos], dim=-1)
                    obs_cond = obs_features.flatten(start_dim=1)
                    # (B, obs_horizon * obs_dim)

                    # sample noise to add to actions
                    noise = torch.randn(naction.shape, device=device)

                    # sample a diffusion iteration for each data point
                    timesteps = torch.randint(
                        0, noise_scheduler.config.num_train_timesteps,
                        (B,), device=device
                    ).long()

                    # add noise to the clean images according to the noise magnitude at each diffusion iteration
                    # (this is the forward diffusion process)
                    noisy_actions = noise_scheduler.add_noise(naction, noise, timesteps)

                    # predict the noise residual
                    noise_pred = nets['noise_pred_net'](noisy_actions, timesteps, global_cond=obs_cond)

                    # L2 loss
                    loss = nn.functional.mse_loss(noise_pred, noise)

                    # optimize
                    loss.backward()
                    optimizer.step()
                    optimizer.zero_grad()
                    # step lr scheduler every batch
                    # this is different from standard pytorch behavior
                    lr_scheduler.step()

                    # update Exponential Moving Average of the model weights
                    ema.step(nets.parameters())

                    # logging
                    loss_cpu = loss.item()
                    epoch_loss.append(loss_cpu)
                    tepoch.set_postfix(loss=loss_cpu)
            tglobal.set_postfix(loss=np.mean(epoch_loss))

    ema.copy_to(nets.parameters())

    return nets

def test(dataloader:torch.utils.data.DataLoader, nets:nn.ModuleDict):
    pass

def main():
    dataloader, stats = setup_data()
    nets = setup_nets()
    trained_nets = train(dataloader, nets)

    torch.save(trained_nets.state_dict(), "savedWeights/pusht_trial.ckpt")


if __name__ == "__main__":
    main()