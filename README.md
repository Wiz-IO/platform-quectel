# Quectel development platform for [PlatformIO](http://platformio.org)

**A few words in the beginning**
* **Version: 2.0.9** ( [look here, if there is something new](https://github.com/Wiz-IO/platform-quectel/blob/master/fix.md) )
* Python 2 & 3 compatable in process, if issue - report
* * NEW: BG96 integrated application uploader
* * NEW: EC2x [OpenLinux](https://github.com/Wiz-IO/platform-quectel/wiki/Framework-OpenLinux), Arduino - coming soon
* * NEW: Board support [Olimex-NB-IoT-DevKit](https://github.com/Wiz-IO/platform-quectel/wiki/BOARD-Olimex-NB-IoT-DevKit)
* This project not an official product of Quectel and is based on **reverse engineering**
* Frameworks: 
* * OpenCPU ( M66, MC60, BC66 ) 
* * ThreadX ( BG96 )
* * OpenLinux ( EC21, EC25 )
* * Arduino ( BC66, M66, BG96, EC2x )
* **Windows(preferably)**, Linux, macOS (I not have hardware machines for tests, compiler must work)
* Read [WIKI](https://github.com/Wiz-IO/platform-quectel/wiki/PLATFORM-QUECTEL)
* [Examples](https://github.com/Wiz-IO/platformio-quectel-examples) 

**it should look like this...**

![Project](https://raw.githubusercontent.com/Wiz-IO/platform-opencpu/master/platform.png) 

Video

https://youtu.be/YvHy1MLqH70

https://www.youtube.com/watch?v=DJ0nZS5HwHU

![Project](https://raw.githubusercontent.com/Wiz-IO/platform-opencpu/master/boards.png) 

![Project](https://raw.githubusercontent.com/Wiz-IO/LIB/master/images/bc66-oled.jpg) 

![Project](https://raw.githubusercontent.com/Wiz-IO/platform-opencpu/master/on_linux.png) 

## Install Platform

_Python 2 & 3 compatable in process, if issue - report_

PIO Home > Platforms > Advanced Installation 

paste https://github.com/Wiz-IO/platform-quectel.git

**How to: [WIKI](https://github.com/Wiz-IO/platform-quectel/wiki/PLATFORM-QUECTEL)**
 and [EXAMPLES](https://github.com/Wiz-IO/platformio-quectel-examples)

## Fast Uninstal
* goto C:\Users\USER_NAME.platformio\platforms delete folder **quectel** ( builders )
* goto C:\Users\USER_NAME.platformio\packages delete folder **framework-quectel** ( sources )
* _goto C:\Users\USER_NAME.platformio\packages delete folder tool-quectel ( azsphere )_
* _goto C:\Users\USER_NAME.platformio\packages delete folder toolchain-gccarmnoneeabi (compiler )_

## Thanks to

* Radu Igret ( Quectel )
* Ivan Kravets ( PlatformIO )
* [comet.bg](https://www.comet.bg/?cid=92)

**Support links**

* https://forums.quectel.com/
* https://www.quectel.com/support/contact.htm
* https://community.platformio.org
* https://www.comet.bg/?cid=92
* 

>If you want to help / support:   
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ESUP9LCZMZTD6)
