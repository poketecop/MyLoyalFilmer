import re
import subprocess
import time

SYSTEM_PASSWORD = b'yahboom\n'
PS_BLUETOOTH_CONTROL_REGEX = re.compile(r'((pi)|(root))\s+(?P<pid>\d+).*bluetooth_control')
PS_MJPG_STREAMER_REGEX = re.compile(r'((pi)|(root))\s+(?P<pid>\d+).*mjpg_streamer')
PS_STDOUT_SPLITTED_PID_POSITION = 1

class Initializer:    

    def prepare_environment(self):
        # Prepares environment
        self.kill_demanding_processes()

    def get_processes(self):
        stdout, stderr = subprocess.Popen(['ps', '-ef'],
                            stdout = subprocess.PIPE, 
                            stderr = subprocess.PIPE).communicate()
        if stderr or not stdout:
            raise Exception(stderr.decode('utf-8'))

        ps_stdout_str = stdout.decode('utf-8')
        print(ps_stdout_str)

        return ps_stdout_str

    def kill_demanding_processes(self):
        # Kill demanding processes
        ps_stdout_str = self.get_processes()

        matching = re.search(PS_BLUETOOTH_CONTROL_REGEX, ps_stdout_str)

        if matching:
            bluetooth_control_pid = matching.group('pid')

            stdout, stderr = subprocess.Popen(['sudo', 'kill', '-9', bluetooth_control_pid],
                        stdout = subprocess.PIPE, 
                        stderr = subprocess.PIPE).communicate(input=SYSTEM_PASSWORD)
            if stderr:
                print(stderr.decode('utf-8'))
            else:
                print('\nProceso bluetooth matado. stdout: ' + (stdout.decode('utf-8') if stdout else ''))
        
        matching = re.search(PS_MJPG_STREAMER_REGEX, ps_stdout_str)

        if matching:
            mjpg_streamer_pid = matching.group('pid')
            
            stdout, stderr = subprocess.Popen(['sudo', 'kill', '-9', mjpg_streamer_pid],
                            stdout = subprocess.PIPE, 
                            stderr = subprocess.PIPE).communicate()
            if stderr:
                print(stderr.decode('utf-8'))
            else:
                print('\nProceso mjpg streamer matado. stdout: ' + (stdout.decode('utf-8') if stdout else ''))
        
        ps_stdout_str = self.get_processes()

        matching = re.search(PS_BLUETOOTH_CONTROL_REGEX, ps_stdout_str)

        if matching:
            raise Exception('\nBluetooth process still running')

        matching = re.search(PS_MJPG_STREAMER_REGEX, ps_stdout_str)

        if matching:
            raise Exception('\MJPG streamer process still running')

        time.sleep(1)