"""
Name - Simar Singh
Email - hfv6838@wmich.edu

"""

import argparse
import sys

ready_queue = list()
io_queue = list()
arrival_queue = list()
# graveyard
departure_queue = list()
cpu = None
time = 0
parser = argparse.ArgumentParser()

# parser.add_argument("input", dest="input", help="<input file>", type=str, required=True)
parser.add_argument("-q", "--quantum", dest="quantum", help="quantum", type=int, default=1)
parser.add_argument("-s", "--type", dest="type", help="<type of scheduler>", type=str, required=True)
parser.add_argument("input", help="<input file>", type=str)
output_file = "output.txt"
# filename_in = "examples/input1/in.csv"
args = parser.parse_args()
filename_in = args.input
factor = 1
if args.type == "FF" or args.type == "HR" or args.type == "SP":
    args.quantum = 9999999
elif args.type == "SR":
    args.quantum = 1
elif args.type == "FB":
    factor = args.quantum
    args.quantum = 1


class Process:
    def __init__(self, name, birthday, lifetime):
        self.name = name
        self.birthday = birthday
        self.lifetime = lifetime
        self.io_burst = []
        self.number_of_ticks = 0
        self.time_at_desk = 0
        self.quantum = args.quantum
        self.time_left_in_vacation = 0
        self.time_waiting = 0
        self.priority = 1
        self.virgin = None
        self.death_date = None

    def __str__(self):
        return f'name: {self.name}, birthday: {self.birthday} \n lifetime: {self.lifetime}, io_burst: {self.io_burst}' \
               f'time_at_desk:{self.time_at_desk} \n number_of_ticks:{self.number_of_ticks},' \
               f'Time waiting: {self.time_waiting} '


def scheduling():
    # file1 = args.tracefile
    process = None
    with open(filename_in) as f:
        lines = f.readlines()
        global ready_queue
        global io_queue
        for line in lines:
            print(line)
            line = line.strip()
            split_line = line.split(",")
            if line != "":
                name = split_line[0]
                if name == "":
                    vacation = int(split_line[1])
                    stay_there = int(split_line[2])
                    process.io_burst.append((vacation, stay_there))

                else:
                    birthday = int(split_line[1])
                    # how long it wants cpu
                    lifetime = int(split_line[2])
                    process = Process(name, birthday, lifetime)
                    arrival_queue.append(process)


def tick():
    global cpu
    global time
    for i in arrival_queue:
        if time == i.birthday:
            ready_queue.append(i)
            arrival_queue.remove(i)
    if cpu is not None:
        if cpu.lifetime == cpu.number_of_ticks:
            departure_queue.append(cpu)
            cpu.death_date = time
            cpu = None
        elif len(cpu.io_burst) > 0 and cpu.io_burst[0][0] == cpu.number_of_ticks:
            cpu.time_left_in_vacation = cpu.io_burst[0][1]
            io_queue.append(cpu)
            cpu.io_burst.pop(0)
            cpu = None
        elif cpu.quantum <= cpu.time_at_desk and len(ready_queue) > 0:
            ready_queue.append(cpu)
            # for FB
            cpu.priority += 1
            cpu.quantum *= factor
            cpu = None
    for processes in io_queue:
        if processes.time_left_in_vacation < 0:
            ready_queue.append(processes)
            io_queue.remove(processes)
    if cpu is None and len(ready_queue) > 0:
        cpu = select()
        if cpu.virgin is None:
            cpu.virgin = time
        cpu.time_at_desk = 0
    if cpu is not None:
        cpu.time_at_desk += 1
        # cpu.lifetime -= 1
        cpu.number_of_ticks += 1
        print("----------------------------")
        print(f"TIME: {time}")
        print(f"cpu: {str(cpu)}")
        print(f"ready_queue {[str(x) for x in ready_queue]}")
        print(f"io_queue {[str(x) for x in io_queue]}")
        print(f"arrival_queue {[str(x) for x in arrival_queue]}")
        print("--------------------------------")
    for process in ready_queue:
        process.time_waiting += 1
    for process in io_queue:
        process.time_waiting += 1
        process.time_left_in_vacation -= 1
    time += 1


def select():
    # go through ready queue and append to cpu
    if args.type == "FF":
        return_cpu = max(ready_queue, key=lambda x: x.time_waiting)
        ready_queue.remove(return_cpu)
    if args.type == "RR":
        # quantum from commandline
        return_cpu = ready_queue.pop(0)
    if args.type == "SP":
        return_cpu = min(ready_queue, key=lambda x: x.lifetime)
        ready_queue.remove(return_cpu)
    if args.type == "SR":
        return_cpu = min(ready_queue, key=lambda x: x.lifetime - x.number_of_ticks)
        ready_queue.remove(return_cpu)
    if args.type == "HR":
        return_cpu = max(ready_queue, key=lambda x: (x.time_waiting + x.lifetime) / x.lifetime)
        ready_queue.remove(return_cpu)
    if args.type == "FB":
        # quantum from commandline
        return_cpu = min(ready_queue, key=lambda x: x.priority)
        ready_queue.remove(return_cpu)

    return return_cpu


if __name__ == '__main__':
    scheduling()
    while len(arrival_queue) > 0 or len(ready_queue) > 0 or cpu or len(io_queue):
        tick()
    with open(output_file, 'w') as f:
        f.write('"name", "arrival time", "service time", "start time", "total wait time", "finish time", "turnaround '
                'time", "normalized turnaround" \n')
        avg_turn_around_time = 0
        avg_normalized_turn_around_time = 0
        for d in departure_queue:
            f.write("%s, %u, %u, %u, %u, %u, %u, %.2f\n" % (
                d.name, d.birthday, d.lifetime, d.virgin, d.time_waiting, d.death_date, (d.lifetime + d.time_waiting)
                , ((d.lifetime + d.time_waiting) / d.lifetime)))
            avg_turn_around_time += d.lifetime + d.time_waiting
            avg_normalized_turn_around_time += (d.lifetime + d.time_waiting) / d.lifetime
        f.write("%.2f, %.2f\n" % (
            avg_turn_around_time / len(departure_queue), avg_normalized_turn_around_time / len(departure_queue)))
