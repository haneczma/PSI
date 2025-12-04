#include <err.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#define BUF_SIZE 200
#define PACKET_SIZE 100
#define FILE_PATH "recv_data.bin"

void bailout(const char *message){
    perror(message);
    exit(1);
}

int main(int argc, char *argv[])
{
    int sock, s;
    char buf[BUF_SIZE];
    ssize_t pkt_size;
    socklen_t peer_addrlen;
    struct sockaddr_in server;
    struct sockaddr_storage peer_addr;

    FILE *file = fopen(FILE_PATH, "wb");

    if (argc != 2)
        errx(0, "Incorrect number of arguments. Correct usage: <port>", argv[0]);

    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
        bailout("Error opening socket\n");

    server.sin_family = AF_INET;
    server.sin_port = htons(atoi(argv[1]));
    server.sin_addr.s_addr = INADDR_ANY;

    if ((s = bind(sock, (struct sockaddr *)&server, sizeof(server))) < 0)
        bailout("Bind unsuccessfull");

    printf("Waiting for packets");

    while(1)
    {
        uint32_t count=0;
        uint32_t seq, seq_be;
        char host[NI_MAXHOST], service[NI_MAXSERV];
        uint8_t *data;
        ssize_t data_size;

        peer_addrlen = sizeof(peer_addr);
        pkt_size = recvfrom(sock, buf, BUF_SIZE, 0,
                         (struct sockaddr *)&peer_addr, &peer_addrlen);
        if (pkt_size < 4)
        {
            fprintf(stderr, "Recvfrom not a valid package\n");
            continue;
        }

        s = getnameinfo((struct sockaddr *)&peer_addr, peer_addrlen, host, NI_MAXHOST,
                        service, NI_MAXSERV, NI_NUMERICSERV);
        if (s == 0)
            fprintf("Received %zd bytes from %s:%s\n", pkt_size, host, service);
        else
        {
            fprintf(stderr, "Error while getting client data\n");
            continue;
        }

        memcpy(&seq_be, buf, 4);
        seq = ntohl(seq_be);
        if (seq == count){
            data = buf + 4;
            data_size = pkt_size - 4;
            fwrite(data, 1, data_size, file);
            sendto(sock, seq_be, 4, 0, ((struct sockaddr *)&peer_addr, peer_addrlen));
            count = count + 1;
        }
        else {
            bailout("Missing packets\n");
        }

    }
}