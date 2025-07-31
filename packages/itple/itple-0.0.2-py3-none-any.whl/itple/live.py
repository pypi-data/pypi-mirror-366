import serial
import serial.tools.list_ports
import time
import subprocess
import tempfile
import shutil
import importlib.resources
from pathlib import Path
from .base import ITPLayBase

# 이 클래스에서 사용할 펌웨어 버전 정보
FIRMWARE_VERSION = "1.0.0" 

class ITPLayLive(ITPLayBase):
    """
    아두이노와 실시간으로 통신하여 제어하는 클래스입니다.
    객체 생성 시, 아두이노에 범용 펌웨어를 업로드하고 시리얼 통신을 시작합니다.
    """
    def __init__(self):
        self.port = self._find_arduino_port()
        self.connection = None
        self.duration = 2000 # 버저 기본 지속 시간
        if self.port:
            self._connect_serial()
        else:
            print("오류: 아두이노를 찾을 수 없습니다. 연결 상태를 확인해주세요.")

    def _find_arduino_port(self):
        """아두이노가 연결된 시리얼 포트를 자동으로 찾습니다."""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # 아두이노 정품 또는 호환 보드(CH340 드라이버)를 찾습니다.
            if 'Arduino' in port.description or 'CH340' in port.description:
                return port.device
        return None

    def upload(self):
        """패키지에 내장된 범용 펌웨어를 아두이노에 업로드합니다."""
        sketch_name = f"Itple_Python_firmware_V{FIRMWARE_VERSION}"
        ino_filename = f"{sketch_name}.ino"
        print(f"'{sketch_name}' 펌웨어 업로드를 시작합니다...")
        
        try:
            self.close() # 기존 연결이 있다면 안전하게 닫습니다.
            time.sleep(1) # 포트가 완전히 닫힐 때까지 대기합니다.

            # 패키지 내 리소스 경로를 찾습니다.
            traversable_path = importlib.resources.files("itple.firmware").joinpath(sketch_name, ino_filename)
            with importlib.resources.as_file(traversable_path) as concrete_path:
                with tempfile.TemporaryDirectory() as temp_dir:
                    # arduino-cli는 스케치 파일과 폴더 이름이 같아야 합니다.
                    sketch_subdir = Path(temp_dir) / sketch_name
                    sketch_subdir.mkdir()
                    shutil.copy(concrete_path, sketch_subdir)
                    
                    command = [
                        'arduino-cli', 'compile', '--upload', 
                        '--port', str(self.port),
                        '--fqbn', 'arduino:avr:uno',
                        str(sketch_subdir)
                    ]
                    
                    subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
                    print("펌웨어 업로드 성공! 1초 후 재연결을 시도합니다.")
                    time.sleep(1)
                    self._connect_serial()
        except (ModuleNotFoundError, FileNotFoundError):
            print("오류: 패키지 또는 펌웨어 파일을 찾을 수 없습니다. 설치 상태를 확인해주세요.")
        except subprocess.CalledProcessError as e:
            print(f"펌웨어 업로드 실패: {e}\n{e.stderr}")
        except Exception as e:
            print(f"펌웨어 업로드 중 알 수 없는 오류 발생: {e}")

    def _connect_serial(self):
        """시리얼 포트에 연결합니다."""
        try:
            self.connection = serial.Serial(self.port, 9600, timeout=1)
            print(f"시리얼 포트 연결 성공! (port: {self.port})")
            time.sleep(2) # 아두이노 부팅 및 안정화 대기
        except serial.SerialException as e:
            print(f"시리얼 포트 연결 실패: {e}")

    def send_command(self, command: str):
        """아두이노에 시리얼 명령을 보냅니다."""
        if self.connection and self.connection.is_open:
            self.connection.write(f"{command}\n".encode('utf-8'))
        else:
            print("연결되지 않아 명령을 보낼 수 없습니다.")
            
    def _get_sensor_value(self, command: str) -> int:
        """아두이노로부터 정수형 센서 값을 읽어옵니다."""
        self.send_command(command)
        if self.connection:
            try:
                line = self.connection.readline()
                if line:
                    return int(line.decode('utf-8').strip())
            except (ValueError, TypeError):
                return -1 # 잘못된 값이 수신된 경우
        return -1

    def _get_sensor_value_float(self, command: str) -> float:
        """아두이노로부터 실수형 센서 값을 읽어옵니다."""
        self.send_command(command)
        if self.connection:
            try:
                line = self.connection.readline()
                if line:
                    return float(line.decode('utf-8').strip())
            except (ValueError, TypeError):
                return -1.0
        return -1.0

    def close(self):
        """시리얼 연결을 닫습니다."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print('시리얼 연결을 닫았습니다.')

    # --- ITPLayBase 메소드 구현 ---

    def red_on(self):
        self.send_command('lrn')

    def red_off(self):
        self.send_command('lrf')

    def blue_on(self):
        self.send_command('lbn')

    def blue_off(self):
        self.send_command('lbf')
        
    def all_light_on(self):
        self.send_command('lan')

    def all_light_off(self):
        self.send_command('laf')
        
    def buzzer_on(self, scale: str = "C0", octave: int = 4, note: int = 4):
        command = f'b{octave}{scale}{note}'
        self.send_command(command)
        # 'live' 모드에서는 파이썬이 직접 기다려야 음 길이를 보장할 수 있습니다.
        if self.duration > 0 and note > 0:
            time.sleep(self.duration / note / 1000.0)

    def buzzer_off(self):
        self.send_command('bnn')
        
    def set_duration(self, time: int = 2000):
        self.duration = time
        # 실시간 모드에서는 파이썬 변수만 업데이트해도 충분하지만,
        # 펌웨어와의 일관성을 위해 명령을 보낼 수도 있습니다.
        self.send_command(f'sd{time:05d}')

    def is_light(self, type: str = 'u', thresehold: int = 500) -> bool:
        command = "rl" + type + f'{thresehold}'
        return self._get_sensor_value(command) == 1

    def is_push(self, type: str = 'u') -> bool:
        command = "rb" + type
        return self._get_sensor_value(command) == 1

    def is_sound(self, type: str = 'u', thresehold: int = 500) -> bool:
        command = "rs" + type + f'{thresehold}'
        return self._get_sensor_value(command) == 1

    def get_light(self) -> int:
        return self._get_sensor_value("gl")

    def get_sound(self) -> int:
        return self._get_sensor_value("gs")

    def delay(self, ms: int):
        """파이썬 스크립트를 지정된 시간만큼 멈춥니다."""
        time.sleep(ms / 1000.0)