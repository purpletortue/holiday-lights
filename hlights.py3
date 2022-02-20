#!/usr/bin/env python3
# version 2.1.0
# IOT holiday light interface for Philips Illuminate
"""

"""
import argparse
import socket
from socket import AF_INET, SOCK_STREAM, timeout
import sys
import time
import ipaddress
import logging
import codecs

decode_hex = codecs.getdecoder("hex_codec")
encode_hex = codecs.getencoder("hex_codec")

def send_code(code, BUFFER_SIZE):
    """
    Sends a hex code to the light control box and
    returns the response of predefined length
    """
    TCP_IP = args.device
    TCP_PORT = 5577
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    try:
        s.connect((TCP_IP, TCP_PORT))
    except timeout:
        exit(1)
    #print(decode_hex(code)[0])
    s.send(decode_hex(code)[0])

    # If we are expectng a response code, capture and return it
    if BUFFER_SIZE > 0:
        data = s.recv(BUFFER_SIZE)
        result = encode_hex(data)[0].decode()
        logging.debug(result)
    else:
        result = None
    s.close()

    return result


def decode_status(status):
    """
    Splits a 13byte status code into its components and
    returns a statuscode object with all components defined
    or None on invalid status
    """
    #print(status)
    header = status[0:2]
    field2 = status[2:4]
    powerstatecode = status[4:6]
    functioncode = status[6:8]
    field5 = status[8:10]
    speedcode = status[10:12]
    field7 = status[12:14]
    field8 = status[14:16]
    field9 = status[16:18]
    field10 = status[18:20]
    strands = status[20:22]
    field12 = status[22:24]
    footer = status[24:]

    if not (header == '66' and footer == '99'):
        logging.error('Unknown status received from lights')
        return None
    else:
        statuscode = {'header': header,
                      'field2': field2,
                      'powerstatecode': powerstatecode,
                      'functioncode': functioncode,
                      'field5': field5,
                      'speedcode': speedcode,
                      'R': field7,
                      'G': field8,
                      'B': field9,
                      'field10': field10,
                      'strands': strands,
                      'field12': field12,
                      'footer': footer
                      }

        logging.debug(header + field2 + powerstatecode + functioncode + field5 + speedcode + field7 + field8 + field9 + field10 + strands + field12 + footer)
        # Human readable values below where possible
        logging.debug('Field2 is ' + field2)
        logging.info('Lights are ' + code2powerstate(powerstatecode))
        logging.info('Function is ' + code2function(functioncode))
        logging.debug('Field5 is ' + field5)
        logging.info('Speed is ' + code2speed(speedcode))
        logging.info('R is ' + field7)
        logging.info('G is ' + field8)
        logging.info('B is ' + field9)
        logging.debug('Field10 is ' + field10)
        logging.info('# of Strands is ' + strands)
        logging.debug('Field12 is ' + field12)
        #output comma separated, app-converted status with header and footer stripped
#        print(field2  + ',' +
#            code2powerstate(powerstatecode) + ',' +
#            code2function(functioncode) + ',' +
#            field5  + ',' +
#            code2speed(speedcode) + ',' +
#            field7 + ',' +
#            field8 + ',' +
#            field9 + ',' +
#            field10 + ',' +
#            strands + ',' +
#            field12
#            )
        return statuscode


def get_status():
    """
    Requests status code from lights and
    returns the 13 byte response
    """
    time.sleep(0.1)
    code = 'ef0177'
    response = send_code(code, 13)
    return response


def turn_lights_on():
    code = 'cc2333'
    response = send_code(code, 3)
    if response == 'ee2311':
        return True
    return False


def turn_lights_off():
    code = 'cc2433'
    response = send_code(code, 3)
    if response == 'ee2411':
        return True
    return False


def function2code(functionnum):
    """
    Converts a given function number (1-21) and
    returns the 2-digit hex code(25-39 hex) for that function
    """
    functioncode = int(functionnum + 36)
    # print(functioncode)
    return format(functioncode, '02x')


def code2function(functioncode):
    """
    Converts a given function code (25-39 hex) and
    returns the function number (1-21) for that function
    """
    functionnum = int(functioncode, 16) - 36
    # print(functioncode)
    return str(functionnum)


def speed2code(speednum):
    """
    Converts a given speed number (0-100) and
    returns the 2-digit hex code (01-36 hex) for that speed
    """
    # speednum can be from 0-100
    # speedcode ranges from 01-36 in hex
    ratio = speednum / float(100)
    a = (53 * ratio)
    b = 53 - a
    speedcode = int(b + 1)
    # print(format(speedcode, '02x'))
    return format(speedcode, '02x')


def code2speed(speedcode):
    """
    Converts a given speed code (01-36 hex) and
    returns the speed number (0-100) for that code
    """
    # speednum can be from 0-100
    # speedcode ranges from 01-36 in hex
    b = int(speedcode, 16) - 1
    a = 53 - b
    ratio = float(a) / 53
    speednum = int(ratio * 100)
    return str(speednum)


def code2powerstate(powercode):
    """
    Converts a given powerstate code and
    returns on or off
    """
    if powercode == '23':
        return 'on'
    elif powercode == '24':
        return 'off'
    else:
        return None


def validate_args(args):

    if args.speed != -1:
        if not (0 <= args.speed <= 100):
            print('Speed value must be between 0 and 100')
            sys.exit(1)
    if args.function is not None:
        if not (1 <= args.function <= 21):
            print('Function value must be between 1 and 21')
            sys.exit(1)
    if args.verbose == 1:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    elif args.verbose >=2:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    logging.debug(args)
#    try:
#        ip = ipaddress.ip_address(args.device)
#        print('%s is a correct IP%s address.' % (ip, ip.version))
#    except ValueError:
#        print('address/netmask is invalid: %s' % args.device)
#        sys.exit(1)
#    except:
#        print('Usage : %s  ip' % sys.argv[0])
#        sys.exit(1)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Holiday light control for Philips Illuminate.')
    parser.add_argument('device', type=str, help='Device IP')
    powerstate = parser.add_mutually_exclusive_group()
    powerstate.add_argument('--on', dest='on', action='store_true', help='Turn lights on')
    powerstate.add_argument('--off', dest='off', action='store_true', help='Turn lights off')
    parser.add_argument('-s', '--status', dest='status', action='store_true', help='Get current status of lights')
    parser.add_argument('--function', dest='function', type=int, help='Set FUNCTION from 1-21 for desired pattern')
    parser.add_argument('--speed', dest='speed', type=int, default=-1, help='Set SPEED from 0-100 for desired speed')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Once for INFO, Twice for DEBUG')
    parser.add_argument('--ha', dest='homeassistant', action='store_true', help='Flag to enable Homeassistant exit status for state detection')
    args = parser.parse_args()

    validate_args(args)
    #print(args.device)
    # if args.status:
    #    current_status = get_status()
    #    print('Current status is ' + current_status)

    if args.speed >= 0:
        speedcode = speed2code(args.speed)

    if args.function:
        functioncode = function2code(args.function)
        if functioncode:
            if args.speed == -1:
                speedcode = decode_status(get_status())['speedcode']
            # print('bb' + functioncode + speedcode + '44')
            send_code('bb' + functioncode + speedcode + '44', 0)

        # print(functioncode)

    if args.on:
        logging.info('Turning lights on')
        turn_lights_on()

    if args.off:
        logging.info('Turning lights off')
        turn_lights_off()


#    if args.status:
#        new_status = get_status()
#        logging.info('Updated status is ' + new_status)
#        statuscode = decode_status(new_status)


    current_status = get_status()
    decode_status(current_status)

    if args.homeassistant:
        if code2powerstate(decode_status(current_status)['powerstatecode']) == 'on':
            exit(0);
        else:
            exit(1);
