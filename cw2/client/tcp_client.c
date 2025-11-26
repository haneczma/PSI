#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <err.h>

void bailout(const char *message){
    perror(message);
    exit(1);
}

int main(int argc, char *argv[])
{
    int sock;
    struct sockaddr_in server;
	struct hostent *hp;

    if (argc != 3) {
        errx(0, "Incorrect number of arguments. Correct usage: <server ip> <port>\n", argv[0]);
    }

    // Create socket
    sock = socket( AF_INET, SOCK_STREAM, 0 );
    if (sock == -1)
        bailout("Error opening socket\n");

    // Initialize server struct
    memset(&server, 0, sizeof(server));
    server.sin_family = AF_INET;

    server.sin_port = htons(atoi(argv[2]));
	
	//IP from name
    server.sin_family = AF_INET;
    hp = gethostbyname2(argv[1], AF_INET );

    if (hp == (struct hostent *) 0) {
        errx(2, "%s: unknown host\n", argv[1]);
    }
    printf("Address resolved\n");

    memcpy((char *) &server.sin_addr, (char *) hp->h_addr, hp->h_length);

    // Connect to server
    connect (sock, (struct sockaddr *) &server, sizeof(server) );
    printf ("Connected to: %s\n", argv[1]);
	fflush(stdout);
    /*
	int i;
    for (i=0; i<atol(argv[3]); i++ ) {
        struct timeval send_time, recieve_time;

        memset( databuf, '*', dgram_size );

        // Send datagram
        if ((send( sock, databuf, dgram_size, 0 )) <0 ) {
            perror("Error while sending\n");
        }
	gettimeofday(&send_time, NULL);
        // Server responds with number of bytes in datagram
        int response;
        int rec = recv(sock, &databuf, MAX_DGRAMSIZE, 0);
	gettimeofday(&recieve_time, NULL);
	databuf[rec] = '\0';
	response =  atoi(databuf);
        if (rec < 0) {
            bailout("Error while receving a response\n");
        }
        else if(response != dgram_size) {
            bailout("Invalid server response\n");
        }

        printf("Datagram size: %i Response delay: %lf\n", dgram_size, timediff(send_time, recieve_time));
	fflush(stdout);        
    }*/

    close(sock);
    exit(0);
}
