#include <Keypad.h>

int v1 = 0;
const byte ROWS = 4;
const byte COLS = 3;

char keys[ROWS][COLS] = {                    
  {'1','2','3'},
  {'4','5','6'},
  {'7','8','9'},
  {'*','0','#'}
};

byte rowPins[ROWS] = { 31, 33, 35, 37 };    
byte colPins[COLS] = { 39, 41, 43 }; 
Keypad kpd = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS ); 

void setup()
{              
Serial.println ("setup:");  
  Serial.begin(9600);                     
}

void loop()
{
   v1 = GetNumber();
   Serial.println ("Num:");
   Serial.print (v1);
}


int GetNumber()
{
   int num = 0;
   char key = kpd.getKey();
   while(key != '#')
   {
      switch (key)
      {
         case NO_KEY:
            break;

         case '0': case '1': case '2': case '3': case '4':
         case '5': case '6': case '7': case '8': case '9':
           
            num = num * 10 + (key - '0');
            break;

         case '*':
            num = 0;
          
            break;
      }

      key = kpd.getKey();
   }

   return num;
}

