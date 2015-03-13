"""
Library for encoding arbitrary data into images.
"""
#!~/usr/bin/python


import Image
import itertools as its

def n_at_a_time(items, n, fillvalue):
    '''Returns an iterator which groups n items at a time.
    
    Any final partial tuple will be padded with the fillvalue
    
    >>> list(n_at_a_time([1, 2, 3, 4, 5], 2, 'X'))
    [(1, 2), (3, 4), (5, 'X')]
    '''
    it = iter(items)
    return its.izip_longest(*[it] * n, fillvalue=fillvalue)

def biterator(data):
    '''Returns a biterator over the input data.
    
    >>> list(biterator(chr(0b10110101)))
    [1, 0, 1, 1, 0, 1, 0, 1]
    '''
    return ((ord(ch) >> shift) & 1
            for ch, shift in its.product(data, range(7, -1, -1)))


def header(n):
    n=len(n)
    '''Return n packed in a 4 byte string.'''
    bytes = (chr(n >> s & 0xff) for s in range(24, -8, -8))
    return ('%s' * 4) % tuple(bytes)
def pather(filepath):
    return header(filepath)

def setlsb(cpt, bit):
    '''Set least significant bit of a colour component.'''
    return cpt & ~1 | bit

def hide_bits(pixel, bits):
    '''Hide a bit in each pixel component, returning the resulting pixel.'''
    return tuple(its.starmap(setlsb, zip(pixel, bits)))

def hide_bit(pixel, bit):
    '''Similar to the above, but for single band images.'''
    return setlsb(pixel, bit[0])

def unpack_lsbits_from_image(image):
    '''Unpack least significant bits from image pixels.'''
    # Return depends on number of colour bands. See also hide_bit(s)
    if len(image.getbands()) == 1:
        return (px & 1 for px in image.getdata())
    else:
      
        return (cc & 1 for px in image.getdata() for cc in px)
    


def call(f): # (Used to defer evaluation of f)
    return f()

def disguise(image, data, filepath=""):
    '''Disguise data by packing it into an image.
    
    On success, the image is modified and returned to the caller.
    On failure, None is returned and the image is unchanged.
    '''
    
    payload = "%s"%header(filepath)+filepath+header(data)+data

    #print header(filepath), filepath
    # print header(len(data))
    npixels = image.size[0] * image.size[1]
    nbands = len(image.getbands())
    if len(payload) * 8 <= npixels * nbands:
        new_pixel = hide_bit if nbands == 1 else hide_bits
        pixels = image.getdata()
        bits = n_at_a_time(biterator(payload), nbands, 0)
        new_pixels = its.starmap(new_pixel, its.izip(pixels, bits))
        image.putdata(list(new_pixels))
        return image

def reveal(image):
    '''Returns any message disguised in the supplied image file, or None.'''
    bits = unpack_lsbits_from_image(image)
    def accum_bits(n):
        return reduce(lambda a, b: a << 1 | b, its.islice(bits, n), 0)
    def next_ch():
        return chr(accum_bits(8))
    npixels = image.size[0] * image.size[1] 
    nbands = len(image.getbands())
    path_length = accum_bits(32)
    path = ''.join(its.imap(call, its.repeat(next_ch, path_length)))
    data_length = accum_bits(32)
    data = ''.join(its.imap(call, its.repeat(next_ch, data_length)))
    return data, path
