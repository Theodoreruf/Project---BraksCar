/**
 * @file rc_project_template.c
 * This is meant to be a skeleton program for Robot Control projects. Change
 * this description and file name before modifying for your own purpose.
 */

#include <stdio.h>
#include <signal.h>
#include <rc/pthread.h>
#include <robotcontrol.h> // includes ALL Robot Control subsystems
// code version 1.0.3

#include <time.h>

// function declarations
void on_pause_press();
void on_pause_release();


#define DT 0.05
#define DTus DT*1000000
#define pi 3.141592

// --------Lidar----------//
// Baud rate of Lidar
#define BAUDS 115200
#define TIMEOUT_S 0.5

uint8_t buffer[128]; // 128 to take the all packet of bytes

// 1500 pulses/ rotation
#define COD 1500/2.0/pi


int regul=0;

float w1=0,w2=0,w3=0,w4=0;
float c_cod1=0,c_cod2=0,c_cod3=0,c_cod4=0;


#define PWM_MAX 0.99
float sature(float v){
	if (v>PWM_MAX) return PWM_MAX;
	if (v<-PWM_MAX) return -PWM_MAX;
	return v;
}

uint64_t MyTime(void){
	struct timeval tv;

	gettimeofday(&tv,NULL);
	return (1000000*tv.tv_sec) + tv.tv_usec;
}

// interrupt handler to catch ctrl-c
static void __signal_handler(__attribute__ ((unused)) int dummy)
{
	regul=0;
	rc_set_state(EXITING);
	
	return;
}

// ------------------RPLIDAR Part------------------------//

/*
 * Format of data :
 * 		A5 | 5A | 00 | 00 | 40 | 81 | Data response packets
 * Format of data response packets :
 * 		Quality (8 -> 2), S_, S | Angle[6:0] (8 -> 1), C | Angle[14:7] | Distance[7:0] | Distance[15:8]
*/


// Functions

/*
 * This function has the goal to initialize every component and send the first message
 * into the Lidar
 *
 */
void Lidar_Scan()
{
	uint8_t stringtosend[2];
	stringtosend[0] = 0xA5;
	stringtosend[1] = 0x20;

	// We send in the UART the data to launch the scan of the lidar
	if(rc_uart_write(2,stringtosend,sizeof(stringtosend)) == -1)
	{
		printf("Failed to send bytes to start \n");
	}
}

/*
 * Function to Force Scan of Lidar
 */
void Lidar_Force_Scan()
{
	uint8_t stringtosend[2];
	stringtosend[0] = 0xA5;
	stringtosend[1] = 0x21;

	// We send in the UART the data to launch the scan of the lidar
	if(rc_uart_write(2,stringtosend,sizeof(stringtosend)) == -1)
	{
		printf("Failed to send bytes to force scan \n");
	}
}

/*
 * Function which allows to stop the Lidar
 */

void Lidar_Stop()
{
	uint8_t stringtosend[2];
	stringtosend[0] = 0xA5;
	stringtosend[1] = 0x20;

	// We send in the UART the data to launch the scan of the lidar
	if(rc_uart_write(2,stringtosend,sizeof(stringtosend)) == -1)
	{
		printf("Failed to send bytes to stop the lidar \n");
	}
}

/*
 * Function which allows us to display float format into the console
 */
static void affichage(float Angle, float Distance)
{
	// For the measure of the angle
	uint8_t sign = (Angle < 0.0) ? 45 : 0;
	float Val = (Angle < 0.0) ? -Angle : Angle;

	uint32_t Int1 = trunc(Val);
	float Frac = Val - Int1;
	uint32_t Int2 = trunc(Frac*10000);

	printf("Angle : %c%d.%d\r\n",sign,Int1,Int2);
	// For the measure of the Distance of the obstacle scanned by the Lidar
	sign = (Distance < 0.0) ? 45 : 0;
	Val = (Distance < 0.0) ? -Distance : Distance;

	Int1 = trunc(Val);
	Frac = Val - Int1;
	Int2 = trunc(Frac*10000);

	printf("Distance : %c%d.%d\r\n",sign,Int1,Int2);
}


// Thread
static pthread_t thread_lidar;

static void* lidar(void *arg){
	printf("Je suis là\n");
	// Initialization of Variables
	int bytes_Received = 0;
	uint8_t state = 1;
	uint8_t cond = 0;
	uint8_t quality = 0;
	uint8_t index = 0;

	uint8_t index_angle = 0;
	float angle = 0;
	float angle_tab[100];
	float distance = 0;

    // Initialize UART2
	if(rc_uart_init(2,BAUDS,TIMEOUT_S,0,1,0) == -1)
	{
		printf("Failed to initialize UART%d\n",2);
	}

	// Flush the USART
	if(rc_uart_flush(2) == -1)
	{
		printf("Failed to Flush UART%d\n",2);
	}

	// Initialize Lidar to start Scan
	Lidar_Scan();

	// Reset Buffer
	for(int i = 0; i < 128; i ++)
	{
		buffer[i] = 0;
	}

	while(1)
	{
		// Data reception from the uart
		bytes_Received = rc_uart_read_bytes(2,buffer,sizeof(buffer));
		
		// Verify the presence of error
		if(bytes_Received == -1)
		{
			printf("Error when reading the uart\n");
		}
		else if(bytes_Received == 0)
		{
			printf("timeout reached, %d bytes read\n",bytes_Received);
		}
		index = -1;
		// Data Processing
		while(index != bytes_Received)
		{
			index ++;
			//printf("Valeur du buffer : %x avec index = %d et état : %d\n",buffer[index],index,state);
			// Protocol Verification : 
			// A5 | 5A | 00 | 00 | 40 | 81 | Data response packets
			switch(state)
			{
				case 1 :
					if(buffer[index] == 0xA5)
						state = 2;
					continue;
				case 2 :
					printf("Je suis à 2\n");
					if(buffer[index] == 0x5A)
						state = 3;
					continue;
				case 3 :
					printf("Je suis à 3\n");
					if(buffer[index] == 0x05)
						state = 4;
					continue;
				case 4 :
					printf("Je suis à 4\n");
					if(buffer[index] == 0x00)
						state = 5;
					continue;
				case 5 :
					printf("Je suis à 5\n");
					if(buffer[index] == 0x00)
						state = 6;
					continue;
				case 6 :
					if(buffer[index] == 0x40)
						state = 7;
					continue;
				case 7 :
					if(buffer[index] == 0x81)
						state = 8;
					continue;
				case 8 :
					if(buffer[index] == 0xA5 && buffer[index + 1] == 0x5A)
						state = 2;
					else
						if( (buffer[index] & 0x01) ^ (buffer[index] & 0x02))
						{
							quality = ((buffer[index] & 0xFC) >> 2U);
							state = 9;
						}
					continue;
				case 9 :
					angle = ((buffer[index] & 0xFE) >> 1U);
					state = 10;
					continue;
				case 10 :
					angle = angle + (buffer[index] << 7U);
					angle = angle/64;
					state = 11;
					// Allows us to verify the output in putty
					if(index_angle < 100)
					{
						angle_tab[index_angle] = angle;
						index_angle ++;
					}
					else
						index_angle = 100;
					continue;
				case 11 :
					distance = buffer[index];
					state = 12;
					continue;
				case 12 :
					distance = distance + (buffer[index] << 8U);
					if(quality > 5)
					{
						printf("--------------------\n");
						affichage(angle,distance); // Print in Console
					}
					state = 8;
					continue;
				}
			//if(index == 100) index = 0;
			rc_usleep(400);
		}
	}
	return 0;
}


static pthread_t thread_regulation;

//static void* regulation(void*arg){
static void* regulation(void*arg){
	uint64_t t0,t1,wait;
	int cod1,cod2,cod3,cod4;
	float cmd1=0;
	float cmd2=0;
	float cmd3=0;
	float cmd4=0;

	float err1=0;
	float err2=0;
	float err3=0;
	float err4=0;


while (1){
	while (regul){

	t0=MyTime();
	
	// pour asserv position
	c_cod1=c_cod1+w1*DT*COD;
	c_cod2=c_cod2+w2*DT*COD;
	c_cod3=c_cod3+w3*DT*COD;
	c_cod4=c_cod4+w4*DT*COD;


	// Read Encodeur
	cod1=rc_encoder_read(1);
	cod2=rc_encoder_read(2);
	cod3=rc_encoder_read(3);
	cod4=rc_encoder_read(4);
	printf("cod : %5d %5d %5d %5d\n",cod1,cod2,cod3,cod4);
	
	
	err1=c_cod1-cod1;
	err2=c_cod2-cod2;
	err3=c_cod3-cod3;
	err4=c_cod4-cod4;
	
	
	#define KP 0.01
	cmd1=KP*err1;
	cmd2=KP*err2;
	cmd3=KP*err3;
	cmd4=KP*err4;
	//printf("%1.2f %1.2f %1.2f %1.2f\n",cmd1,cmd2,cmd3,cmd4);

	//  limit pwm command -1< cmd <1
	cmd1=sature(cmd1);
	cmd2=sature(cmd2);
	cmd3=sature(cmd3);
	cmd4=sature(cmd4);
	
	rc_motor_set(1,cmd1);
	rc_motor_set(2,cmd2);
	rc_motor_set(3,cmd3);
	rc_motor_set(4,cmd4);
		
	t1=MyTime();
	wait=DTus-(t1-t0)-300;

	rc_usleep(wait);
	
	}

	//printf("reglation inactive\n");
	rc_usleep(1000000);
}
return NULL;	
}


/**
 * This template contains these critical components
 * - ensure no existing instances are running and make new PID file
 * - start the signal handler
 * - initialize subsystems you wish to use
 * - while loop that checks for EXITING condition
 * - cleanup subsystems at the end
 *
 * @return     0 during normal operation, -1 on error
 */
int main()
{

	int priority = 0;
	int priority_lidar = 0;
		int policy = SCHED_OTHER;
	// make sure another instance isn't running
	// if return value is -3 then a background process is running with
	// higher privaledges and we couldn't kill it, in which case we should
	// not continue or there may be hardware conflicts. If it returned -4
	// then there was an invalid argument that needs to be fixed.
	if(rc_kill_existing_process(2.0)<-2) return -1;

	// start signal handler so we can exit cleanly
	if(rc_enable_signal_handler()==-1){
		fprintf(stderr,"ERROR: failed to start signal handler\n");
		return -1;
	}

	// initialize pause button
	if(rc_button_init(RC_BTN_PIN_PAUSE, RC_BTN_POLARITY_NORM_HIGH,
						RC_BTN_DEBOUNCE_DEFAULT_US)){
		fprintf(stderr,"ERROR: failed to initialize pause button\n");
		return -1;
	}

	// initialize hardware first
	if(rc_encoder_init()){
		fprintf(stderr,"ERROR: failed to run rc_encoder_init\n");
		return -1;
	}

	// Assign functions to be called when button events occur
	rc_button_set_callbacks(RC_BTN_PIN_PAUSE,on_pause_press,on_pause_release);

	// make PID file to indicate your project is running
	// due to the check made on the call to rc_kill_existing_process() above
	// we can be fairly confident there is no PID file already and we can
	// make our own safely.
	rc_make_pid_file();


	printf("\nPress and release pause button to turn green LED on and off\n");
	printf("hold pause button down for 2 seconds to exit\n");

	// Keep looping until state changes to EXITING
	rc_set_state(RUNNING);
		
	int freq_hz = RC_MOTOR_DEFAULT_PWM_FREQ;
	rc_motor_init_freq(freq_hz);

	printf("Demarre le thread asservissement \n");
	if(rc_pthread_create(&thread_regulation, regulation, NULL, policy, priority)<0){
		fprintf(stderr, "failed to start thread controleur\n");
		return -1;
	}

	
	// Start the thread of the Lidar
	printf("Demarre le thread Lidar \n");
	if(rc_pthread_create(&thread_lidar,lidar,NULL,policy,priority_lidar)<0){
		fprintf(stderr,"failed to start thread of lidar\n");
		return -1;
	}
	
	// set signal handler so the loop can exit cleanly
	signal(SIGINT, __signal_handler);	
	
	
	
// ----------------------------  WHILE ------------------------------------	
	while(rc_get_state()==RUNNING){
		// do things based on the state
		if(rc_get_state()==RUNNING){
			rc_led_set(RC_LED_GREEN, 1);
			rc_led_set(RC_LED_RED, 0);
		}
		else{
			rc_led_set(RC_LED_GREEN, 0);
			rc_led_set(RC_LED_RED, 1);
		}
/* ------------------- Place your code here ---------------------- */
/* --------------------------------------------------------------- */
/* --------------------------------------------------------------- */


	void commande(float u, float v, float w){
	
	w1=(-(u)*sin(0)+v*cos(0)+1*w)/3;
	w2=(-(u)*sin((2*3.14)/3)+v*cos((2*3.14)/3)+1*w)/3;
	w3=(-(u)*sin((-2*3.14)/3)+v*cos((-2*3.14)/3)+1*w)/3;
}
	
	w1=0;w2=0;w3=0;w4=0;
	//active regulation
	regul=1;
	//
	w1=0;w2=0;w3=0;w4=0;
    
	commande(60,0,0);
	rc_usleep(3000);


/* --------------------------------------------------------------- */
/* --------------------------------------------------------------- */
/* ------------------- End your code here ------------------------ */
	rc_set_state(EXITING);

	}

	// turn off LEDs and close file descriptors
	printf("moteur cleanup\n");
	regul=0;
	rc_usleep(500000);
	rc_motor_cleanup();
	rc_usleep(500000);
	rc_led_set(RC_LED_GREEN, 0);
	rc_led_set(RC_LED_RED, 0);
	rc_led_cleanup();
	rc_button_cleanup();	// stop button handlers
	rc_remove_pid_file();	// remove pid file LAST
	return 0;
}


/**
 * Make the Pause button toggle between paused and running states.
 */
 
void on_pause_release()
{
	if(rc_get_state()==RUNNING)	rc_set_state(PAUSED);
	else if(rc_get_state()==PAUSED)	rc_set_state(RUNNING);
	return;
}

/**
* If the user holds the pause button for 2 seconds, set state to EXITING which
* triggers the rest of the program to exit cleanly.
**/
void on_pause_press()
{
	int i;
	const int samples = 100; // check for release 100 times in this period
	int us_wait = 2000000; // 2 seconds
	us_wait=200000;
	// now keep checking to see if the button is still held down
	for(i=0;i<samples;i++){
		rc_usleep(us_wait/samples);
		if(rc_button_get_state(RC_BTN_PIN_PAUSE)==RC_BTN_STATE_RELEASED) return;
	}
	printf("long press detected, shutting down\n");
	rc_set_state(EXITING);
	return;
}
