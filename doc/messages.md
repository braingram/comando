Base comando messages consist of 3 parts

- header [1 byte] the number of bytes in the message payload
- payload [N bytes] the payload bytes
- checksum [1 byte] the sum of all the payload bytes modulo 256

This basic message format allows for arbitrary payloads (up to some maximum)
and by using the header and checksum can allow for resyncing connections
by parsing bytes until a valid packet is found. The maximum message length
(including header and checksum) may be limited to reduce memory usage. See
[comando.h](https://github.com/braingram/comando/blob/master/libraries/comando/comando.h) for the MAX_MSG_LENGTH define.
