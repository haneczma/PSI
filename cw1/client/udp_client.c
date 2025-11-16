#include <arpa/inet.h>
#include <err.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>

#define MAX_DGRAMSIZE 100000

void bailout(const char *message){
    perror(message);
    exit(1);
}

float timediff(struct timeval send, struct timeval rec){
	float diff = (rec.tv_sec - send.tv_sec)*1000 + (rec.tv_usec - send.tv_usec)/1000;
	return diff;
}

int main(int argc, char *argv[])
{
    int sock;
    struct sockaddr_in server;
    char databuf[MAX_DGRAMSIZE];
    int dgram_size = 2;

    if (argc != 4) {
        errx(0, "Incorrect number of arguments. Correct usage: <server ip> <port> <datagram size (power of 2)>\n", argv[0]);
    }

    // Create socket
    sock = socket( AF_INET, SOCK_DGRAM, 0 );
    if (sock == -1)
        bailout("Error opening socket\n");

    // Initialize server struct
    memset(&server, 0, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = inet_addr(argv[1]);
    server.sin_port = htons(atoi(argv[2]));

    // Connect to server
    connect (sock, (struct sockaddr *) &server, sizeof(server) );
    sprintf ("Connected to: %s\n", argv[1]);


    for (int i=0; i<atol(argv[3]); i++ ) {
        struct timeval send_time, recieve_time;

        memset( databuf, '*', dgram_size );

        // Send datagram
        fflush( stdout );
        gettimeofday(&send_time, NULL);
        if ((send( sock, databuf, dgram_size, 0 )) <0 ) {
            perror("Error while sending\n");
        }

        // Server responds with number of bytes in datagram
        int response;
        int rec = recv(sock, &response, sizeof(response), 0);
        gettimeofday(&recieve_time, NULL);
        if (rec < 0) {
            bailout("Error while receving a response\n");
        }
        else if(response != dgram_size) {
            bailout("Invalid server response\n");
        }

        sprintf("Datagram size: %i Response delay: %lf", dgram_size, timediff(send_time, recieve_time));
        dgram_size = dgram_size * 2;
    }

    close(sock);
    exit(0);
}
