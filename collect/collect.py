from multiprocessing import Pipe, Process
import time, hardware, save, comm

# params (image sizes are (w, h) in px)
save_dir = "../data/pusht"
control_hz = 100
save_rate = 10
img_size = (1024, 1024)
save_img_size = (512, 512)

# If you aren't gonna define functions this if is pointless
if __name__=='__main__':
  save_id = time.time()
  hw_cmd_con_out, hw_cmd_con_in = Pipe()
  save_cmd_con_out, save_cmd_con_in = Pipe()
  data_con_out, data_con_in = Pipe()
  hw_proc = Process(target=hardware.human_control_process, #Homework process
                    args=(control_hz, save_rate, img_size,
                          hw_cmd_con_out, data_con_in))
  save_proc = Process(target=save.save_process,
                      args=(save_dir, save_id,
                            control_hz/save_rate, save_img_size,
                            save_cmd_con_out, data_con_out))
  hw_proc.start()
  save_proc.start()
  try:
   sc = comm.curses_up()
   while True:
     key = sc.getch()
     if key==27: # escape
       hw_cmd_con_in.send(comm.EXIT)
       hw_cmd_con_in.close()
       save_cmd_con_in.send(comm.EXIT)
       save_cmd_con_in.close()
       break
  finally:
    comm.curses_down(sc)
  hw_proc.join()
  save_proc.join()