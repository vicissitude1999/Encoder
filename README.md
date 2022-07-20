# Install system
Download RPi image writer from its official website.
Download RPi OS image from https://mirrors.tuna.tsinghua.edu.cn/raspberry-pi-os-images/raspios_full_arm64/images/
Burn the downloaded image to a MicroSD card.
Insert SD card to RPi and plug in the power supply. RPi will boot automatically when power is connected.

# Change package download source
$ mv /etc/apt/sources.list /etc/apt/sources.list.bak
Edit /etc/apt/source.list and write
deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ bullseye main non-free contrib
deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ bullseye main non-free contrib

/etc/apt/sources.list.d/raspi.list
deb http://mirrors.tuna.tsinghua.edu.cn/raspberrypi/ bullseye main ui

If the following error occurs,
W: GPG error: http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian bullseye InRelease: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 9165938D90FDDD2E
set $ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys <PUBKEY>

# Update and install packages
sudo apt update

sudo apt install supervisor

pip install pigpio

pip install pyserial

# Enable services
systemctl enable pigpiod

Enable serial transmission in raspberry pi config

# Setup service to run rotary_encoder automatically
Copy tools/supervisor to /etc/

# Receive data on host
Download and install driver for PL2303 from https://www.prolific.com.tw/US/ShowProduct.aspx?p_id=223&pcid=126
Once you connect RPi with host computer, you may run receiver.py.
The order between running receiver.py on host and running rotary_encoder.py on client doesn't matter.
