from multiprocessing import Pipe, Process
import time, hardware, save, comm

# params (image sizes are (w, h) in px)
save_dir = "../data/pusht"
control_hz = 100
save_rate = 10
img_size = (1024, 1024)
save_img_size = (512, 512)

if __name__=='__main__':
  save_id = time.time()
  hw_cmd_con_in, hw_cmd_con_out = Pipe()
  save_cmd_con_in, save_cmd_con_out = Pipe()
  data_con_in, data_con_out = Pipe()
  hw_proc = Process(target=hardware.human_control_process,
                    args=(control_hz, save_rate, img_size,
                          hw_cmd_con_in, data_con_out))
  save_proc = Process(target=save.save_process,
                      args=(save_dir, save_id,
                            control_hz/save_rate, save_img_size,
                            save_cmd_con_in, data_con_in))
  hw_proc.start()
  save_proc.start()
  try:
   sc = comm.curses_up()
   while True:
     key = sc.getch()
     if key==27: # escape
       hw_cmd_con_out.send(comm.EXIT)
       hw_cmd_con_out.close()
       save_cmd_con_out.send(comm.EXIT)
       save_cmd_con_out.close()
       break
  finally:
    comm.curses_down(sc)
  hw_proc.join()
  save_proc.join()
