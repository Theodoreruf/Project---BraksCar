/**
 * @file rc_project_template.c
 *
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
//	printf("cod : %5d %5d %5d %5d\n",cod1,cod2,cod3,cod4);
	
	
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


	w1=0;w2=0;w3=0;w4=0;
	//active regulation
	regul=1;
	//
	w1=3.14;w2=3.14;w3=3.14;w4=3.14;
    rc_usleep(2000000);
	w2=0;
	w1=0;w2=0;w3=0;w4=0;
    rc_usleep( 500000);

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
