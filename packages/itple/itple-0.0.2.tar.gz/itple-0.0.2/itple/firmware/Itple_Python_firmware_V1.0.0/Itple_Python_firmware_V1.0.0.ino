const int RED_LED_PIN = 10;
const int BLUE_LED_PIN = 11;
const int BUZZER_PIN = 3;

const int LM_PWM_PIN = 5;
const int RM_PWM_PIN = 6;

const int LM_DIR_PIN = 2;
const int RM_DIR_PIN = 4;

const int UB_PIN = A0;
const int DB_PIN = A1;
const int LB_PIN = 7;
const int RB_PIN = 8;

const int LS_PIN = A2;
const int SS_PIN = A3;

const int IRL_PIN = A6;
const int IRR_PIN = A7;

const int TRIG_PIN = 13;
const int ECHO_PIN = 12;

int scale = 0;
int duration = 2000;
int _temp;
int Value;
int pushButton;

const int notes[6][12] = {
  // 1옥타브: C1 ~ B1
  { 33, 35, 37, 39, 41, 44, 46, 49, 52, 55, 58, 62 },
  // 2옥타브: C2 ~ B2
  { 65, 69, 73, 78, 82, 87, 93, 98, 104, 110, 117, 123 },
  // 3옥타브: C3 ~ B3
  { 131, 139, 147, 156, 165, 175, 185, 196, 208, 220, 233, 247 },
  // 4옥타브: C4 ~ B4
  { 262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494 },
  // 5옥타브: C5 ~ B5
  { 523, 554, 587, 622, 659, 698, 740, 784, 831, 880, 932, 988 },
  // 6옥타브: C6 ~ B6
  { 1047, 1109, 1175, 1245, 1319, 1397, 1480, 1568, 1661, 1760, 1865, 1976 }
};

long getDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long dura = pulseIn(ECHO_PIN, HIGH, 30000); // 30ms 타임아웃 설정
  long dist = dura / 29 / 2;
  return dist;
}

void setup() {
  // 시리얼 통신을 9600 속도로 시작합니다.
  Serial.begin(9600);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(BLUE_LED_PIN, OUTPUT);

  pinMode(LM_PWM_PIN, OUTPUT);
  pinMode(RM_PWM_PIN, OUTPUT);
  pinMode(LM_DIR_PIN, OUTPUT);
  pinMode(RM_DIR_PIN, OUTPUT);

  pinMode(LS_PIN, INPUT);
  pinMode(SS_PIN, INPUT);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    switch(command[0]){
      case 'l':
      // 첫글자가 l 인 경우 light를 제어
      // 두번째 글자가 a인 경우 전부 제어
        switch(command[1]){
          case 'a':
            if(command[2] == 'n'){
              digitalWrite(RED_LED_PIN, HIGH);
              digitalWrite(BLUE_LED_PIN, HIGH);
            }else{
              digitalWrite(RED_LED_PIN, LOW);
              digitalWrite(BLUE_LED_PIN, LOW);
            }
            break;
          case 'r':
            if(command[2] == 'n') digitalWrite(RED_LED_PIN, HIGH);
            else digitalWrite(RED_LED_PIN, LOW);
            break;
          case 'b':
            if(command[2] == 'n') digitalWrite(BLUE_LED_PIN, HIGH);
            else digitalWrite(BLUE_LED_PIN, LOW);
            break;
        }
        break;
      
      case 'b':
        switch(command[2]){
          case 'C':
            if(command[3] == '0') scale = 0;
            else scale = 1;
            break;
          case 'D':
            if(command[3] == '0') scale = 2;
            else scale = 3;
            break;
          case 'E':
            scale = 4;
            break;
          case 'F':
            if(command[3] == '0') scale = 5;
            else scale = 6;
            break;
          case 'G':
            if(command[3] == '0') scale = 7;
            else scale = 8;
            break;
          case 'A':
            if(command[3] == '0') scale = 9;
            else scale = 10;
            break;
          case 'B':
            scale = 11;
            break;
          default:
            scale = -1;
            break;
        }
        if(scale == -1){
          noTone(BUZZER_PIN);
        }else{
          tone(BUZZER_PIN, notes[command[1]-'1'][scale], duration/(command[4]-'0')*0.95);
          delay(duration/(command[4]-'0'));
        }
        break;
        
      case 's':
        switch(command[1]){
          case 'd':
            duration = command.substring(2).toInt();
            break;
          
          case 'm':
            _temp = command.substring(3).toInt();
            if(command[2] == 'l') analogWrite(LM_PWM_PIN, _temp);
            else if(command[2] == 'r') analogWrite(RM_PWM_PIN, _temp);
            else if(command[2] == 'a'){
              analogWrite(LM_PWM_PIN, _temp);
              analogWrite(RM_PWM_PIN, _temp);
            }
            break;
            
          case 'w':
            _temp = command[3] - '0';

            if(command[2] == 'l') digitalWrite(LM_DIR_PIN, _temp);
            else if(command[2] == 'r') digitalWrite(RM_DIR_PIN, _temp);
            else if(command[2] == 'a'){
              digitalWrite(LM_DIR_PIN,_temp);
              digitalWrite(RM_DIR_PIN,_temp);
            }
            break;
        }
        break;
      
      case 'r':
        switch(command[1]){
          case 'l':
            Value = analogRead(LS_PIN);
            _temp = command.substring(3).toInt();
            if(command[2]=='u') Serial.println(Value>_temp);
            else Serial.println(Value<_temp);
            break;
          
          case 'b':
            switch(command[2]){
              case 'u':
                pushButton = analogRead(UB_PIN);
                break;
              case 'd':
                pushButton = analogRead(DB_PIN);
                break;
              case 'l':
                pushButton = digitalRead(LB_PIN);
                break;
              case 'r':
                pushButton = digitalRead(RB_PIN);
                break;
            }
            Serial.println(pushButton==0);
            break;
          
          case 's':
            Value = analogRead(SS_PIN);
            _temp = command.substring(3).toInt();
            if(command[2]=='u') Serial.println(Value>_temp);
            else Serial.println(Value<_temp);
            break;
          
          case 't':
            if(command[2]=='l') Value = analogRead(IRL_PIN);
            else Value = analogRead(IRR_PIN);
            _temp = command.substring(4).toInt();
            if(command[3]=='u') Serial.println(Value>_temp);
            else Serial.println(Value<_temp);
            break;
          
          case 'd':
            long dist = getDistance(); // 함수 호출\

            _temp = command.substring(3).toInt();

            if(command[2]=='u') Serial.println(dist > _temp);
            else Serial.println(dist < _temp);

            break;
        }
        break;

      case 'g':
        switch(command[1]){
          
          case 'l':
            Value = analogRead(LS_PIN);
            Serial.println(Value);
            break;
          
          case 's':
            Value = analogRead(SS_PIN);
            Serial.println(Value);
            break;
          
          case 't':
            if(command[2]=='l') Value = analogRead(IRL_PIN);
            else Value = analogRead(IRR_PIN);
            Serial.println(Value);
            break;
          
          case 'd':
            long dist = getDistance(); // 함수 호출
            Serial.println(dist);
            break;
        break;
      }
    }
  }
}