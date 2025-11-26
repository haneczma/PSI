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
const int TREE_SIZE = 15;

void bailout(const char *message){
    perror(message);
    exit(1);
}

typedef struct Node {
    int id;
    int value;
    struct Node* left;
    struct Node* right;
} Node;

Node* createNode(int id, int value)
{
    Node* node = malloc(sizeof(Node));
    node->id = id;
    node->value = value;
    node->left = NULL;
    node->right = NULL;
    return node;
}

Node* makeChild(int index, int n)
{
    if (index >= n)
        return NULL;

    Node* node = createNode(index, index);
    node->left  = makeChild(2*index + 1, n);
    node->right = makeChild(2*index + 2, n);

    return node;
}

Node* makeTree(int n)
{
    if (n <= 0) return NULL;
    return makeChild(0, n);
}

// sends binary tree in BFS order 
//(0;1;2;3;4;5;6;7;8;9;10;11;12;13;14) for 15 Nodes
void sendBinaryTree(Node* tree, int sock, int treeSize)
{
    if (!tree) return;

    Node** queue = malloc(sizeof(Node*) * treeSize);
    int front = 0, back = 0;

    queue[back++] = tree;

    while (front < back)
    {
        Node* n = queue[front++];

        int data[2] = { n->id, n->value };
        if (send(sock, data, sizeof(data), 0) != sizeof(data))
            bailout("send failed");

        if (n->left)  queue[back++] = n->left;
        if (n->right) queue[back++] = n->right;
    }
    free(queue);
}

void freeTree(Node* tree)
{
    if (!tree) return;
    freeTree(tree->left);
    freeTree(tree->right);
    free(tree);
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

    // send the binary tree
    Node* tree = makeTree(TREE_SIZE);
    sendBinaryTree(tree, sock, TREE_SIZE);

    freeTree(tree);
    close(sock);
    exit(0);
}
