import os
import numpy as np
import subprocess
import argparse

parser = argparse.ArgumentParser()
#parser.add_argument('--pt', type=str, default='2GeV',
#                    help='Cutoff pt value in GeV (default: 2GeV)')
parser.add_argument('--batchsize', type=int, default=1, metavar='N',
                    help='input batch size for inference')
parser.add_argument('--graphs', type=int, default=5, metavar='N',
                    help='number of random graphs for ave, std')
parser.add_argument('--construction', type=str, default='heptrk_classic',
                    help='graph construction method')
parser.add_argument('--gpu', action='store_true', default=False,
                    help='perform inference on GPU')
args = parser.parse_args()
"""
file = open("timeit_interaction_network.sh", "r")
lines = file.readlines()
lines[1] = 'PT="{}"\n'.format(args.pt)
lines[2] = "BATCHSIZE={}\n".format(args.batchsize)
lines[4] = 'CONSTRUCTION="{}"\n'.format(args.construction)
lines[5] = "CUDA={}\n".format(1 if args.gpu else 0)
file = open("timeit_interaction_network.sh", "w")
file.writelines(lines)
file.close()

if(args.gpu):
  filename = "gpu_timing_{}_{}.txt".format(args.construction, args.pt)
  title = "CPU+GPU inference timing \n"
  device = "CPU+GPU"
else:
  filename = "cpu_timing_{}_{}.txt".format(args.construction, args.pt)
  title = "CPU inference timing \n"
  device = "CPU"

outfile = open(filename, "w")
outfile.write(title)
outfile.close()
"""
pts =['2GeV', '1GeV5', '1GeV', '0GeV75', '0GeV6', '0GeV5']

for pt in pts:
  with open("timeit_interaction_network.sh", "r") as f:
    lines = f.readlines()
  lines[1] = 'PT="{}"\n'.format(pt)
  lines[2] = "BATCHSIZE={}\n".format(args.batchsize)
  lines[4] = 'CONSTRUCTION="{}"\n'.format(args.construction)
  lines[5] = "CUDA={}\n".format(1 if args.gpu else 0)
  with open("timeit_interaction_network_tmp.sh", "w") as f:
    f.writelines(lines)

  if(args.gpu):
    filename = "gpu_timing_{}_{}.txt".format(args.construction, pt)
    title = "CPU+GPU inference timing \n"
    device = "CPU+GPU"
  else:
    filename = "cpu_timing_{}_{}.txt".format(args.construction, pt)
    title = "CPU inference timing \n"
    device = "CPU"

  with open(filename, "w") as outfile:
    outfile.write(title)
  for x in range(0, args.graphs):
    with open("timeit_interaction_network_tmp.sh", "r") as f:
      lines = f.readlines()
    lines[3] = "GRAPHBATCHNUM={}\n".format(x)
    with open("timeit_interaction_network_tmp.sh", "w") as f:
      f.writelines(lines)

    os.system('chmod +x timeit_interaction_network_tmp.sh')

    cmd = subprocess.check_output(['./timeit_interaction_network_tmp.sh']).splitlines()
    
    for i, line in enumerate(cmd):
      if 'loops, best of' in str(line):
        with open(filename, "a") as outfile:
          outfile.write("\n")
          outfile.write("{}\n".format(line))
      else:
        continue

  acc = []
  with open(filename, "r") as f:
    for line in f.readlines():
      if 'loops, best of:' in line:
        print("parse line recognized")
        acc.append(int(line[24:28].strip()))

  avg = 0
  for x in range(0,len(acc)):
    avg += acc[x]

  avg /= len(acc)

  print("average {} inference time(pt cut = {}, model = {}) = {}".format(device, pt, args.construction, avg)) 
