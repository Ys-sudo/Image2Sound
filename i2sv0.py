import struct
import time
import wave
from tkinter import *
import numpy as np
import pyaudio
from PIL import ImageTk, Image
from numpy import *

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS,
        # and places our data files in a folder relative to that temp
        # folder named as specified in the datas tuple in the spec file
        base_path = os.path.join(sys._MEIPASS, 'data')
    except Exception:
        # sys._MEIPASS is not defined, so use the original path
        base_path = '/Users/Y-S/PycharmProjects/RGBsounds/'

    return os.path.join(base_path, relative_path)

window = Tk()
window.title("Image to Sound Converter v.1.1 by Ystudio")
window.geometry('1050x600')
window.configure(background="black")
# scaling the image
maxsize = (200, 200)




# DEFINITIONS OF FUNCTIONS
def load():
    if txt.get() == '':
        txt.insert(0, 'please specify the path!')

    else:

        pix.insert(INSERT, '\n' + 'work in progress...' + '\n')
        start_time = time.time()
        y = Image.open(txt.get())
        y.thumbnail(maxsize, Image.NEAREST)
        photo1 = ImageTk.PhotoImage(y)

        img1.image = photo1
        img1.grid(row=7, column=0)

        img1.configure(image=photo1)

        #print('image loaded...')
        pix.insert(INSERT, '\n' + 'image loaded...' + '\n')
        timing.configure(text=("Image loaded:" + '\n' + '\n'"--- %s seconds ---" % np.ceil(time.time() - start_time)))
        #print("--- %s seconds ---" % (time.time() - start_time))


def createsound():
    if txt5.get() == '':
        txt5.insert(0, 'please specify the path!')

    else:
        # define time
        pix.insert(INSERT, '\n' + 'creating sound...' + '\n')
        start_time = time.time()

        im = Image.open(txt.get())
        pix_val = list(im.getdata())  # scan pixels
        # (x,y,x)
        pixies = [x for sets in pix_val for x in sets]  # flatten the list
        # x,y,x
        # print(pix_val)
        # print('\n')
        # print(pixies)
        # print(pixies.count(3))

        # convet to list of arrays format
        str1 = pixies

        def chunk_str(st1r, chunk_size):
            return [str[i:i + chunk_size] for i in range(0, len(str1), chunk_size)]

        # print(chunk_str(str, 3))
        # we get a format like this [x,y,x],[x,y,z]...

        # Red 400-484(THz) frequency 620-750 (nm) wavelenght
        # Green 526-606 , 495-570  Blue 606-668 , 450-495
        # x,y,z = range(0 - 255) => x = R y = G z = B

        # frequency =  #R +x value = 400-484 = / 250 +(0-225) -- rgb scale
        # frequency =  #G + y value = 500-606 = / 375
        # frequency =  #B + z value = 606-789 = / 550

        # wavelenght = #R = 0.620-750
        # wavelenght = #G = 0.495-570
        # wavelenght = #B = 0.450-495

        # print(len(str))
        # print(str)

        # [x,y,z,x,y,z,x,y,z...]

        # index positions
        # print(str[0::3]) # R
        # print(str[1::3]) # G
        # print(str[2::3]) # B

        # duration* -2 [] , /3 for the number of pixels of each color
        num_samples = int((len(str1) - 2) / 3)
        #print('number of pixels:'+ str(num_samples) +'...')

        amplitude = int(txt1.get())
        # ##OUTPUT***
        file = txt5.get()

        nframes = num_samples

        comptype = "NONE"

        compname = "not compressed"

        nchannels = int(txt3.get())
        sampling_rate = int(txt2.get())
        sampwidth = int(txt4.get())

        wav_file = wave.open(file, 'w')
        wav_file.setparams((nchannels, sampwidth, int(sampling_rate), nframes, comptype, compname))

        # we need to map rgb values:
        # print side by side // print green // print time

        # frequency multiplier:
        fm = int(bl3.get())

        # R
        for x in str1[0::3]:
            x = (x * fm)
            frequency = x
            # print(x, end=' ')
            sine_wave = [np.sin(2 * np.pi * frequency * x / sampling_rate) for x in range(num_samples)]
            for s in sine_wave:
                wav_file.writeframes(struct.pack('h', int(s * amplitude)))
        # G
        for y in str1[1::3]:
            y = (y * fm)
            frequency = y
            # print(y, end=' ')
            sine_wave = [np.sin(2 * np.pi * frequency * y / sampling_rate) for y in range(num_samples)]
            for s in sine_wave:
                wav_file.writeframes(struct.pack('h', int(s * amplitude)))
        # B
        for z in str1[2::3]:
            z = (z * fm)
            frequency = z
            # print(z, end=' ')
            sine_wave = [np.sin(2 * np.pi * frequency * z / sampling_rate) for z in range(num_samples)]
            for s in sine_wave:
                wav_file.writeframes(struct.pack('h', int(s * amplitude)))

        #print('sound created...')
        pix.insert(INSERT, '\n' + '.wav file created...' + '\n')
        timing.configure(text=("Sound created:" + '\n' + '\n'"--- %s seconds ---" % np.ceil(time.time() - start_time)))
        #print("--- %s seconds ---" % (time.time() - start_time))


def play():
    #print('playback active...')
    filename = txt5.get()
    # define stream chunk
    chunk = 1024

    # open a wav format music
    f = wave.open(filename, "rb")
    # instantiate PyAudio
    p = pyaudio.PyAudio()
    # open stream
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True)
    # read data
    data = f.readframes(chunk)

    # play stream
    while data:
        stream.write(data)
        data = f.readframes(chunk)

    # stop stream
    stream.stop_stream()
    stream.close()

    # close PyAudio
    p.terminate()


def clearnote():
    pix.delete('1.0', END)
    #print('log cleared...')


#x = file = resource_path('kot2.jpg')
#x1 = Image.open(x)
#x1.thumbnail(maxsize, Image.NEAREST)
#photo1 = ImageTk.PhotoImage(x1)
#x2 = file = resource_path('audio.png')
#audio = ImageTk.PhotoImage(Image.open(x2))
#img1 = Label(window, image=photo1, bg="black", bd=-2)
#plays = Button(window, image=audio, bg="black", bd=0, highlightbackground='black', highlightthickness=0, command=play)
#img1.grid(row=7, column=0)
#plays.grid(row=7, column=3)

# INTERFACE ITEMS
# description
bl = Label(window, bg="black", height=4, padx=10, fg="white", font="Courier 12 bold underline",
           text="Creates a .wav file based on" + '\n' + " the RGB values of pixels" + '\n' + 'of an image.')
bl.grid(column=0, row=0, sticky=W + E + N + S)
# info
bl1 = Label(window, bg="black", fg="white", font="Courier 9 ",
            text="For best results use small images." + '\n' + "e.g. 100x100 pixels")
bl1.grid(column=1, row=0)
# Frequency
bl2 = Label(window, bg="black", fg="white", font="Courier 12 bold", text="Frequency" + '\n' + 'multiplier:')
bl2.grid(column=3, row=0)

bl3 = Entry(window, width=5, bg="black", fg="white", bd=5, highlightthickness=1, justify='center')
bl3.insert(0, '1')
bl3.grid(column=3, row=1)

lbl = Label(window, bg="black", padx=10, fg="white", font="Courier 10 bold", text="Path to image (.png or .jpg):")
lbl.grid(column=0, row=1, sticky=W, pady=15)
txt = Entry(window, width=25, bg="black", fg="white", bd=5, highlightthickness=1, font="Courier 12")
txt.grid(column=1, row=1)
btn = Button(window, text="load image", bg="yellow", fg="black", font="Courier 12 bold", command=load,
             highlightbackground='yellow')
btn.grid(column=2, row=1)

bld = Label(window, bg="black", fg="white", text="--------------------")
bld.grid(column=0, row=2)
bld1 = Label(window, bg="black", fg="white", text="--------------------")
bld1.grid(column=1, row=2)
bld2 = Label(window, bg="black", fg="white", text="--------------------")
bld2.grid(column=2, row=2)
bld3 = Label(window, bg="black", fg="white", text="--------------------")
bld3.grid(column=3, row=2)

lbl1 = Label(window, bg="black", fg="white", font="Courier 12 bold", text="Amplitude:" + '\n' + '(e.g. 16000)')
lbl1.grid(column=0, row=3)
txt1 = Entry(window, width=10, bg="black", fg="white", bd=5, highlightthickness=1, justify='center')
txt1.insert(0, '16000')
txt1.grid(column=0, row=4)

lbl2 = Label(window, bg="black", fg="white", font="Courier 12 bold", text="Sampling Rate:" + '\n' + '(e.g. 48000)')
lbl2.grid(column=1, row=3)
txt2 = Entry(window, width=10, bg="black", fg="white", bd=5, highlightthickness=1, justify='center')
txt2.insert(0, '48000')
txt2.grid(column=1, row=4)

lbl3 = Label(window, bg="black", fg="white", font="Courier 12 bold", text="Number of channels:" + '\n' + '(e.g. 1-2)')
lbl3.grid(column=2, row=3)
txt3 = Entry(window, width=5, bg="black", fg="white", bd=5, highlightthickness=1, justify='center')
txt3.insert(0, '2')
txt3.grid(column=2, row=4)

lbl4 = Label(window, bg="black", fg="white", font="Courier 12 bold", text="Sample width:" + '\n' + '(bit value: 1-4)')
lbl4.grid(column=3, row=3)
txt4 = Entry(window, width=5, bg="black", fg="white", bd=5, highlightthickness=1, justify='center')
txt4.insert(0, '1')
txt4.grid(column=3, row=4)

lbld = Label(window, bg="black", fg="white", text="--------------------")
lbld.grid(column=0, row=5)
lbld1 = Label(window, bg="black", fg="white", text="--------------------")
lbld1.grid(column=1, row=5)
lbld2 = Label(window, bg="black", fg="white", text="--------------------")
lbld2.grid(column=2, row=5)
lbld3 = Label(window, bg="black", fg="white", text="--------------------")
lbld3.grid(column=3, row=5)

lbl5 = Label(window, bg="black", padx=10, fg="white", font="Courier 10 bold", text="Path to sound output (.wav):")
lbl5.grid(column=0, row=6, sticky=W)
txt5 = Entry(window, width=25, bg="black", fg="white", bd=5, highlightthickness=1, font="Courier 12")
txt5.grid(column=1, row=6)
btn5 = Button(window, text="create sound", bg="yellow", fg="black", font="Courier 12 bold", command=createsound,
              highlightbackground='yellow')
btn5.grid(column=2, row=6, pady=20)

timing = Label(window, bg="black", fg="white", font="Courier 10 bold", text=("Conversion" + '\n' + "Time"))
timing.grid(row=7, column=2)

pix = Text(window, bg="black", fg="white", font="Courier 10", highlightthickness=2, height=20, width=31,
           xscrollcommand="true")
pix.grid(row=7, column=1)

pixv = Label(window, text="Notes", bg='black', fg="yellow", font="Courier 11 bold", highlightbackground='yellow')
pixv.grid(column=1, row=8)

btnote = Button(window, text="clear log", bg="yellow", fg="black", font="Courier 12 bold", command=clearnote,
                highlightbackground='yellow')
btnote.grid(column=1, row=10, sticky=S)

iml = Label(window, text="Image preview", bg='black', fg="yellow", font="Courier 11 bold", highlightbackground='yellow')
iml.grid(column=0, row=8)

tl = Label(window, text="Timing", bg='black', fg="yellow", font="Courier 11 bold", highlightbackground='yellow')
tl.grid(column=2, row=8)

pl = Label(window, text="Audio prewiev", bg='black', pady=10, fg="yellow", font="Courier 11 bold",
           highlightbackground='yellow')
pl.grid(column=3, row=8)

btn6 = Button(window, text="EXIT", bg="yellow", fg="black", font="Courier 12 bold", command=window.destroy,
              highlightbackground='yellow')
btn6.grid(column=3, row=11, sticky=S + E)

window.mainloop()
