#include <err.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <openssl/sha.h>

#define BUF_SIZE 2048
#define PACKET_SIZE 100
#define FILE_PATH "./recv_data.bin"
#define EOF_UDP 0xFFFFFFFF

void bailout(const char *message){
    perror(message);
    exit(1);
}

int hash(unsigned char hash[SHA256_DIGEST_LENGTH]) {
    unsigned char buf[BUF_SIZE];
    ssize_t data_size;
    FILE *file = fopen(FILE_PATH, "rb");
    if(!file)
        bailout("File not found\n");

    SHA256_CTX sha;
    SHA256_Init(&sha);
    while ((data_size = fread(buf, sizeof(char), sizeof(buf), file)) > 0) {
        SHA256_Update(&sha, buf, data_size);
    }
    SHA256_Final(hash, &sha);
    fclose(file);
    return 0;
}

int main(int argc, char *argv[])
{
    uint32_t count = 0;
    int sock, s;
    char buf[BUF_SIZE];
    ssize_t pkt_size;
    socklen_t peer_addrlen;
    struct sockaddr_in server;
    struct sockaddr_storage peer_addr;

    //Open file in write mode
    FILE *file = fopen(FILE_PATH, "wb");

    if (argc != 2)
        errx(0, "Incorrect number of arguments. Correct usage: <port>", argv[0]);

    //Create socket
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
        bailout("Error opening socket\n");

    server.sin_family = AF_INET;
    server.sin_port = htons(atoi(argv[1]));
    server.sin_addr.s_addr = INADDR_ANY;

    //Bind socket to port
    if ((s = bind(sock, (struct sockaddr *)&server, sizeof(server))) < 0)
        bailout("Bind unsuccessfull");

    printf("[SERVER] Waiting for packets\n");

    while(1)
    {
        uint32_t seq, seq_be;
        char host[NI_MAXHOST], service[NI_MAXSERV];
        uint8_t *data;
        ssize_t data_size;

        peer_addrlen = sizeof(peer_addr);
        //Recieve packet
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
	    {
            printf("[SERVER] Received %zd bytes from %s:%s\n", pkt_size, host, service);
            fflush(stdout);
	    }
        else
        {
            fprintf(stderr, "Error while getting client data\n");
            continue;
        }

        //Get packet number in sequence
        memcpy(&seq_be, buf, 4);
        seq = ntohl(seq_be);

        if (seq == count){
            data = buf + 4;
            data_size = pkt_size - 4;
            fwrite(data, 1, data_size, file);
            sendto(sock, &seq_be, sizeof(seq_be), 0, (struct sockaddr *)&peer_addr, peer_addrlen);
            printf("[SERVER] Send confirmation of recevieng %zd packet\n", seq);
            fflush(stdout);
            count = count + 1;
        }
        else if (seq < count)
        {
            sendto(sock, &seq_be, sizeof(seq_be), 0, (struct sockaddr *)&peer_addr, peer_addrlen);
            printf("[SERVER] Send confirmation of recevieng %zd packet\n", seq);
            fflush(stdout);
            continue;
        }
        else if (seq == EOF_UDP){
            printf("[SERVER] End of file\n");
            fflush(stdout);
            //Save file
            fflush(file);
            fclose(file);
            
            //Get hash
            unsigned char file_hash[SHA256_DIGEST_LENGTH];
            hash(file_hash);
            sendto(sock, &file_hash, sizeof(file_hash), 0, (struct sockaddr *)&peer_addr, peer_addrlen);
            printf("[SERVER] ");
            int i = 0;
            for(i; i<SHA256_DIGEST_LENGTH; ++i)
            {
                //Print in hex
                printf("%02x", file_hash[i]);
            }
            printf("\n");
            fflush(stdout);
        }
        else 
        {
            bailout("Missing packets\n");
        }
    }

    return(0);
}
