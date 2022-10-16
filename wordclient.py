from ctypes.wintypes import WORD
import sys
import socket

# How many bytes is the word length?
WORD_LEN_SIZE = 2

def usage():
    print("usage: wordclient.py server port", file=sys.stderr)

packet_buffer = b''

def get_next_word_packet(s):
    """
    Return the next word packet from the stream.

    The word packet consists of the encoded word length followed by the
    UTF-8-encoded word.

    Returns None if there are no more words, i.e. the server has hung
    up.
    """

    global packet_buffer
    word_packet = b''

    while True:

        # get packet length w/ bits = WORD_LEN_SIZE value
        end_of_packet = int.from_bytes(packet_buffer[0:WORD_LEN_SIZE], byteorder="big")

        # if end_of_packet is not null and has enough bits to capture whole word
        if end_of_packet != 0 and end_of_packet + WORD_LEN_SIZE <= len(packet_buffer):
            # save word_packet to own variable and drop from packet_buffer
            word_packet = packet_buffer[:end_of_packet + WORD_LEN_SIZE]
            packet_buffer = packet_buffer[end_of_packet + WORD_LEN_SIZE:]
            break

        chunk = s.recv(5)

        if chunk == b'':
            return None

        packet_buffer += chunk
        
    return word_packet
        


def extract_word(word_packet):
    """
    Extract a word from a word packet.

    word_packet: a word packet consisting of the encoded word length
    followed by the UTF-8 word.

    Returns the word decoded as a string.
    """
    word = word_packet[2:].decode()
    return word

# Do not modify:

def main(argv):
    try:
        host = argv[1]
        port = int(argv[2])
    except:
        usage()
        return 1

    s = socket.socket()
    s.connect((host, port))

    print("Getting words:")

    while True:
        word_packet = get_next_word_packet(s)

        if word_packet is None:
            break

        word = extract_word(word_packet)

        print(f"    {word}")

    s.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
