/* (c) Grzegorz Blinowski 2000-2023 [ PSI] */
/* this example from: getaddrinfo man page */

#include <err.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#define BUF_SIZE 500

#define bailout(s) \
    {              \
        perror(s); \
        exit(1);   \
    }
#define Usage()                                               \
    {                                                         \
        errx(0, "Usage: %s address-or-ip [port]\n", argv[0]); \
    }
#define timeinms(tv) ((tv.tv_sec) * 1000.0 + (tv.tv_usec) / 1000.0)

int main(int argc, char *argv[])
{
    int sfd, s;
    char buf[BUF_SIZE];
    ssize_t nread;
    socklen_t peer_addrlen;
    struct sockaddr_in server;
    struct sockaddr_storage peer_addr;

    if (argc != 2)
        Usage();

    if ((sfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
        bailout("socker() ");

    server.sin_family = AF_INET;            /* Server is in Internet Domain */
    server.sin_port = htons(atoi(argv[1])); /* Use any available port      */
    server.sin_addr.s_addr = INADDR_ANY;    /* Server's Internet Address   */

    if ((s = bind(sfd, (struct sockaddr *)&server, sizeof(server))) < 0)
        bailout("bind() ");
    printf("bind() successful\n");

    /* Read datagrams and echo them back to sender. */
    printf("waiting for packets...\n");

    for (;;)
    {
        long int counter = 0;
        char host[NI_MAXHOST], service[NI_MAXSERV];
        double stimestamp, rtimestamp;
        struct timeval tv;

        peer_addrlen = sizeof(peer_addr);
        nread = recvfrom(sfd, buf, BUF_SIZE, 0,
                         (struct sockaddr *)&peer_addr, &peer_addrlen);
        printf("recvfrom ok\n");
        if (nread < 0)
        {
            fprintf(stderr, "failed recvfrom\n");
            continue; /* Ignore failed request */
        }

        s = getnameinfo((struct sockaddr *)&peer_addr, peer_addrlen, host, NI_MAXHOST,
                        service, NI_MAXSERV, NI_NUMERICSERV);
        if (s == 0)
            printf("Received %zd bytes from %s:%s\n", nread, host, service);
        else
        {
            fprintf(stderr, "getnameinfo() error: %s\n", gai_strerror(s));
            continue;
        }
        sscanf(buf, "%ld %lf", &counter, &stimestamp);
        gettimeofday(&tv, NULL);
        rtimestamp = timeinms(tv);
        // printf("r=%lf s=%lf ", rtimestamp, stimestamp);
        printf("Received counter = %ld time_delta = %10.2lf\n", counter, rtimestamp - stimestamp);
    }
}
