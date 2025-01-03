import numpy as np
import time, socket, cv2, pickle
from util import tcp
from networks import pusht_networks as ptn
from util import ml

import torch as t
from torchvision import models as tvm
from torch.nn import Identity as tnnI
from torch.nn import ModeulDict as tnnmd
from diffusers.schedulers.scheduling_ddpm import DDPMScheduler as DDPMS


# parameters
# TODO: This are gonna be task dependent.
#   >> 16 steps of prediction might be too long for touchT
To = 2  # observation horison (table 17)
Ta = 6  # action execution horison (table 17)
Tp = 12 # action prediction horison (table 17)
img_size = (512, 512)
host = '0.0.0.0' # listen on all interfaces
port = 5000
bufsize = 4096
wait_time = 0.1
#### Agent Paramters
asd=4#agent state dim
ad=4#action dim
n_img_size=(96,96)
#### Image Network Paramters
vfd=512#vision feature dim
od=2*vfd+asd#obsercation dim
#### Diffusion Parameters
ds=100#diffusion step
bs='squaredcos_cap_v2'#beta schedule
csgo=True#clip sample flag
pt='epsilon'#prediciton type
#### Dataset
stats={'agent_pos': {'min': np.array([14846., 12614.,  5968.,  4541.], dtype=np.float32),
                     'max': np.array([32767., 32767., 32767., 24688.], dtype=np.float32)},
        'action': {'min': np.array([14846., 12614.,  5968.,  4541.], dtype=np.float32),
        'max': np.array([32767., 32767., 32767., 24688.], dtype=np.float32)}}

if __name__=='__main__':
  # The usual setup
  d=t.device('cuda')
  vea=getattr(tvm,'resnet18')();vea.fc=tnnI()
  veb=getattr(tvm,'resnet18')();veb.fc=tnnI()
  vea=ptn.replace_bn_with_gn(vea);veb=ptn.replace_bn_with_gn(veb)
  nypd=ptn.ConditionalUnet1D(ad,od*To)
  ns=tnnmd({'vea':vea,'veb':veb,'nypd':nypd});ns.to(d)
  sd=t.load('savedWeights/toucht_trial.ckpt',map_location='cuda')
  ns.load_state_dict(sd)
  nsh=DDPMS(ds,beta_schedule=bs,clip_sample=csgo,prediction_type=pt)
  try:
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.bind((host, port))
    serv_sock.listen()
    slave_con, slave_adr = serv_sock.accept()
    id = int(slave_con.recv(bufsize).decode('utf-8').strip())
    if id: # slave sends 0, master sends 1
      master_con, master_adr = slave_con, slave_adr
      slave_con, slave_adr = serv_sock.accept()
      slave_con.recv(bufsize)
    else:
      master_con, master_adr = serv_sock.accept()
      master_con.recv(bufsize)
    slave_con.sendall(b'ACK_ID')
    master_con.sendall(b'ACK_ID')
    imgs_1=[]
    imgs_2=[]
    poss=[]
    t = 1
    while True:
      # get images + positions
      imgs_1+=[np.frombuffer(tcp.get_buffered_data(master_con))]
      imgs_2+=[np.frombuffer(tcp.get_buffered_data(slave_con))]
      poss+=[np.frombuffer(tcp.get_buffered_data(master_con))]
      if 0 == t % Ta: # send control
        obs_features=t.cat([ # network input
          ns['vea'](t.from_numpy(np.moveaxis(np.array([cv2.resize(
            f,n_img_size,interpolation=cv2.INTER_AREA) for f in imgs_1[-2:]]))
          ).to(d,dtype=t.float32)),
        ns['veb'](t.from_numpy(np.moveaxis(np.array([cv2.resize(
            f,n_img_size,interpolation=cv2.INTER_AREA) for f in imgs_2[-2:]]))
          ).to(d,dtype=t.float32)),
          t.from_numpy(
            ml.normalize_data(np.array(poss[-2:]),stats=stats['agent_pos'])
          ).to(d,dtype=t.float32)
        ],dim=-1).unsqueeze(0).flatten(start_dim=1)
        # Diffusion
        diff_action=t.randn((1,Tp,ad),device=d)
        nsh.set_timesteps(ds)
        for k in nsh.timesteps():
          noise_pred=ns['nypd'](sample=diff_action,
                                  timstep=k,global_cond=obs_features)
          diff_action=nsh.step(model_output=noise_pred,
                                timestep=k,sample=diff_action).prev_sample
        diff_action=diff_action.detach().to('cpu').numpy()[0]
        action_pred=ml.unnormalize_data(diff_action,stats=stats['action'])
        traj=action_pred[:4]
        tcp.send_buffered_data(master_con, traj.tobytes())
      t += 1
      time.sleep(wait_time)
  finally:
    serv_sock.close()
    slave_con.close()
    master_con.close()
