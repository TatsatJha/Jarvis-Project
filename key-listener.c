#include <ApplicationServices/ApplicationServices.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 65432

void send_signal() { 
    int sock = 0;
    struct sockaddr_in serv_addr;
    char* msg = "wake";

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("Socket creation error");
        return;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    // Convert IPv4 and IPv6 addresses from text to binary form
    if(inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)<=0) {
        printf("\nInvalid address/ Address not supported");
        return;
    }

    // Connect to server
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("Connection Failed");
        return;
    }

    send(sock, msg, strlen(msg), 0);
    close(sock);
}

// Key event callback
CGEventRef keyCallback(CGEventTapProxy proxy, CGEventType type, CGEventRef event, void *userInfo) {
    if (type == kCGEventKeyDown) {
        // Get the virtual key code
        CGKeyCode keycode = (CGKeyCode)CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode);
        CGEventFlags flags = CGEventGetFlags(event);

        int isCmd = flags & kCGEventFlagMaskCommand;
        int isCtrl = flags & kCGEventFlagMaskControl;

	printf("Key code: %d | Modifiers: %s%s\n",
            keycode,
            isCmd ? "Cmd " : "",
            isCtrl ? "Ctrl " : ""
	);


        if(keycode == 38 && isCmd && isCtrl) { 
            printf("Custom shortcut triggered: Cmd+Ctrl+J\n");
            send_signal();
        }
    }

    return event; // pass event along to system
}


int main() {
    // Create an event tap to capture key presses
    CGEventMask eventMask = CGEventMaskBit(kCGEventKeyDown);
    CFMachPortRef eventTap = CGEventTapCreate(
        kCGSessionEventTap,        // Listen at the session level
        kCGHeadInsertEventTap,     // Highest priority
        0,                         // No option flags
        eventMask,
        keyCallback,
        NULL
    );

    if (!eventTap) {
        fprintf(stderr, "Failed to create event tap. Do you have Input Monitoring permission?\n");
        return 1;
    }

    // Create a run loop source and add to current run loop
    CFRunLoopSourceRef runLoopSource = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, eventTap, 0);
    CFRunLoopAddSource(CFRunLoopGetCurrent(), runLoopSource, kCFRunLoopCommonModes);

    // Enable the tap
    CGEventTapEnable(eventTap, true);
    printf("Listening for global keystrokes.");

    CFRunLoopRun(); // Run loop forever
    return 0;
}
