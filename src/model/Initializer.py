import re
import subprocess

SYSTEM_PASSWORD = b'yahboom\n'
PS_BLUETOOTH_CONTROL_REGEX = re.compile(r'pi\s+(\d+).*bluetooth_control')
PS_MJPG_STREAMER_REGEX = re.compile(r'pi\s+(\d+).*mjpg_streamer')
PS_STDOUT_SPLITTED_PID_POSITION = 1

class Initializer:    

    def prepare_environment(self):
        # Prepares environment
        self.kill_demanding_processes()

    def kill_demanding_processes(self):
        # Kill demanding processes

        stdout, stderr = subprocess.Popen(['ps', '-ef'],
                            stdout = subprocess.PIPE, 
                            stderr = subprocess.PIPE).communicate()
        if stderr:
            print(stderr.decode('utf-8'))
            return

        if not stdout:
            return

        ps_stdout_str = stdout.decode('utf-8')
        print(ps_stdout_str)
        matching = re.search(PS_BLUETOOTH_CONTROL_REGEX, ps_stdout_str)

        if matching:
            bluetooth_control_pid = matching.group(1)

            stdout, stderr = subprocess.Popen(['sudo', 'kill', '-9', bluetooth_control_pid],
                        stdout = subprocess.PIPE, 
                        stderr = subprocess.PIPE).communicate(input=SYSTEM_PASSWORD)
            if stderr:
                print(stderr.decode('utf-8'))
        
        matching = re.search(PS_MJPG_STREAMER_REGEX, ps_stdout_str)

        if matching:
            mjpg_streamer_pid = matching.group(1)
            
            stdout, stderr = subprocess.Popen(['sudo', 'kill', '-9', mjpg_streamer_pid],
                            stdout = subprocess.PIPE, 
                            stderr = subprocess.PIPE).communicate()
            if stderr:
                print(stderr.decode('utf-8'))