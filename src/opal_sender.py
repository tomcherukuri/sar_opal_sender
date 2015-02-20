#!/usr/bin/env python
import rospy
from sar_opal_msgs.msg import OpalCommand
import argparse
import json

# Opal sender uses ROS to send messages via a rosbridge_server 
# websocket connection to a SAR Opal tablet. 
def opal_sender():
    # parse python arguments 
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='Send a message to a' 
            + ' SAR Opal project tablet. Must have roscore and '
            + 'rosbridge_server running for message to be sent.')
    parser.add_argument('-l', '--load', dest='loadme', action='append', nargs='?',
            help='load the game object specified in this json config file' +
            ' on the tablet')
    parser.add_argument('-t', '--touch', choices=['enable','e','disable','d'],type=str, 
            dest='touch',help='enable/disable touch events on tablet')
    parser.add_argument('-r', '--reset', action='store_true',
            help='reload all objects and reset scene on tablet')
    parser.add_argument('-a', '--sidekick_do', dest='sidekick_do', 
            action='append', nargs='?', type=str,
            help='tells sidekick to do specified action')
    parser.add_argument('-s', '--sidekick_say', dest='sidekick_say', 
            action='append', nargs='?', type=str,
            help='tells sidekick to say specified speech')
    
    args = parser.parse_args()
    print(args)
    
    # now build a message based on the command:
    # open ros up here, then run through the below and send all

    # start ROS node
    pub = rospy.Publisher('opal_command', OpalCommand, queue_size=10)
    rospy.init_node('opal_sender', anonymous=True)
    r = rospy.Rate(10) # spin at 10 Hz
    r.sleep() # sleep to wait for subscribers


    # load an object
    if args.loadme:
        # for each object to load, send a message
        for obj in args.loadme:
            # parse config file to get details of object or
            # background to load
            try:
                with open (obj) as json_file:
                    json_data = json.load(json_file)
                print(json_data)
                 # build message
                msg = OpalCommand()
                msg.command = OpalCommand.LOAD_OBJECT
                # add the object properties to the message 
                # (the loaded json data)
                msg.properties = json.dumps(json_data) 
                # send Opal message to tablet game
                pub.publish(msg)
                rospy.loginfo(msg)
                r.sleep()
            except ValueError as e:
                print('Error! Could not open or parse json config file!'
                    + '\n  Did you put only one game object config in'
                    + ' the file?\n  Did you use valid json?'
                    + '\nError: %s' % e)
            except IOError as e:
                print('Error! Could not open or could not parse json '
                       +'config file!'
                    + '\n  Does the file exist in this directory, or did'
                    + ' you specify the full file path?'
                    + '\n  Did you include the file extension, if there is'
                    + ' one?\nError: %s' % e)

    # sidekick do an action
    if args.sidekick_do:
        # build message
        msg = OpalCommand()
        msg.command = OpalCommand.SIDEKICK_DO
        msg.properties = args.sidekick_do[0]
        # send Opal message to tablet game
        pub.publish(msg)
        rospy.loginfo(msg)
        r.sleep()

    # sidekick say something
    if args.sidekick_say:
        # build message
        msg = OpalCommand()
        msg.command = OpalCommand.SIDEKICK_SAY
        msg.properties = args.sidekick_say[0]
        # send Opal message to tablet game
        pub.publish(msg)
        rospy.loginfo(msg)
        r.sleep()

    # send enable or disable touch events command
    if args.touch:
        # build message
        msg = OpalCommand()
        msg.command = OpalCommand.ENABLE_TOUCH if args.touch == 'enabled' or args.touch == 'e' else OpalCommand.DISABLE_TOUCH
        # send Opal message to tablet game
        pub.publish(msg)
        rospy.loginfo(msg)
        r.sleep()

    # send reset scene and reload objects command
    if args.reset:
        print('reload');
        # build message
        msg = OpalCommand()
        msg.command = OpalCommand.RESET
        # send Opal message to tablet game
        pub.publish(msg)
        rospy.loginfo(msg)
        r.sleep()

        
if __name__ == '__main__':
    try:
        opal_sender()
    except rospy.ROSInterruptException:
        print('ROSnode shutdown')