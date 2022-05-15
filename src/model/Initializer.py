import re
import subprocess

SYSTEM_PASSWORD = b'yahboom\n'
PS_STDOUT_SEPARATOR = r'\s+'
PS_STDOUT_SPLITTED_PID_POSITION = 1

class Initializer:    

    def prepare_environment(self):
        # Prepares environment
        self.kill_demanding_processes()

    def kill_demanding_processes(self):
        # Kill demanding processes

        stdout, stderr = subprocess.Popen(['ps', '-ef|grep', 'bluetooth_control'],
                            stdout = subprocess.PIPE, 
                            stderr = subprocess.PIPE).communicate()
        if stderr:
            print(stderr)
            return

        if stdout:
            print(stdout)
            bluetooth_control_pid = re.split(PS_STDOUT_SEPARATOR, stdout)[PS_STDOUT_SPLITTED_PID_POSITION]

            stdout, stderr = subprocess.Popen(['ps', '-ef|grep', 'mjpg_streamer'],
                                stdout = subprocess.PIPE, 
                                stderr = subprocess.PIPE).communicate()
            if stderr:
                print(stderr)
                return
            
            print(stdout)

        mjpg_streamer_pid = re.split(PS_STDOUT_SEPARATOR, stdout)[PS_STDOUT_SPLITTED_PID_POSITION]

        stdout, stderr = subprocess.Popen(['sudo', 'kill', '-9', bluetooth_control_pid],
                            stdout = subprocess.PIPE, 
                            stderr = subprocess.PIPE).communicate(input=SYSTEM_PASSWORD)
        if stderr:
            print(stderr)
            return

        if stdout:
            print(stdout)

            stdout, stderr = subprocess.Popen(['sudo', 'kill', '-9', mjpg_streamer_pid],
                                stdout = subprocess.PIPE, 
                                stderr = subprocess.PIPE).communicate()
            if stderr:
                print(stderr)
                return

            print(stdout)